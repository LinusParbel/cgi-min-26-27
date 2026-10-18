"""Blender side of the photo-to-model workflow (runs inside Blender 5.2; never imports PIL).

Builds on the shared tools/asset-spike/asset_lib.py (materials, primitives, bake + export), which is
imported read-only — never edit it from here.

Conventions: Z-up, 1 unit = 1 m. Vehicles face +Y (they drive towards -Z in the engine), props face -Y.
Landmarks are empties named LM_<name>; the same names are used for pixel positions in refs.json.
"""
import json
import math
import shutil
import sys
import tempfile
from pathlib import Path

import bpy
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Quaternion, Vector

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools" / "asset-spike"))
import asset_lib as al  # noqa: E402,F401  (re-exported for asset build scripts)


class Spec:
    """spec.json of an asset: measured dimensions (metres/degrees) and linear RGB colours."""

    def __init__(self, path):
        self.path = Path(path)
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.dims = data["dims"]
        self.colors = data["colors"]

    def d(self, name):
        if name not in self.dims:
            raise KeyError(f"{self.path.name} has no dim '{name}'")
        return self.dims[name]["value"]

    def c(self, name):
        if name not in self.colors:
            raise KeyError(f"{self.path.name} has no colour '{name}'")
        return tuple(self.colors[name]["linear"])


def landmark(name, loc):
    o = bpy.data.objects.new("LM_" + name, None)
    o.empty_display_size = 0.03
    o.location = loc
    bpy.context.scene.collection.objects.link(o)
    bpy.context.view_layer.update()   # so matrix_world is valid right away
    return o


def tube(name, p0, p1, r, mat, verts=16, bevel=0.0):
    """Cylinder of radius r from point p0 to point p1 (any direction)."""
    p0, p1 = Vector(p0), Vector(p1)
    axis = p1 - p0
    o = al.cyl(name, r, axis.length, (p0 + p1) / 2, mat, axis='Z', verts=verts, bevel=bevel)
    o.rotation_euler = axis.to_track_quat('Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    return o


def arc_shell(name, centre, r, width, a0_deg, a1_deg, thickness, mat, step_deg=8):
    """Curved band (mudguard) around an X axis through centre: radius r..r+thickness, `width` along X,
    from angle a0 to a1 in degrees (0 = +Y forward, 90 = up)."""
    import bmesh
    bm = bmesh.new()
    n = max(2, math.ceil((a1_deg - a0_deg) / step_deg))
    rings = []
    for i in range(n + 1):
        a = math.radians(a0_deg + (a1_deg - a0_deg) * i / n)
        ring = []
        for x in (-width / 2, width / 2):
            for rad in (r, r + thickness):
                ring.append(bm.verts.new((x, rad * math.cos(a), rad * math.sin(a))))
        rings.append(ring)        # order: (-x, in), (-x, out), (+x, in), (+x, out)
    for a, b in zip(rings, rings[1:]):
        for i, j in ((0, 1), (1, 3), (3, 2), (2, 0)):
            bm.faces.new((a[i], a[j], b[j], b[i]))
    for ring in (rings[0], rings[-1]):
        bm.faces.new((ring[0], ring[1], ring[3], ring[2]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.location = centre
    if mat is not None:
        me.materials.append(mat)
    bpy.context.view_layer.update()
    return o


# ---------------------------------------------------------------- photo matching

MATCH_CAM = "__match_cam"


def match_camera(photo_size, cam):
    """Camera that sees the scene like the photo: cam = {loc, look_at, lens_mm, roll_deg} in world
    coordinates, 36 mm sensor fitted to the photo's longer side. Sets the render size to the photo."""
    scene = bpy.context.scene
    old = bpy.data.objects.get(MATCH_CAM)
    if old:
        bpy.data.objects.remove(old)
    data = bpy.data.cameras.new(MATCH_CAM)
    data.lens = cam["lens_mm"]
    data.sensor_width = 36
    data.sensor_fit = 'AUTO'
    data.clip_end = 1000
    o = bpy.data.objects.new(MATCH_CAM, data)
    scene.collection.objects.link(o)
    o.location = cam["loc"]
    look = (Vector(cam["look_at"]) - Vector(cam["loc"])).to_track_quat('-Z', 'Y')
    o.rotation_euler = (look @ Quaternion((0, 0, 1), math.radians(cam.get("roll_deg", 0)))).to_euler()
    scene.camera = o
    scene.render.resolution_x, scene.render.resolution_y = photo_size
    scene.render.resolution_percentage = 100
    scene.render.pixel_aspect_x = scene.render.pixel_aspect_y = 1
    bpy.context.view_layer.update()
    return o


def project_landmarks(cam_obj):
    """Pixel position (origin top left) of every LM_* empty, or None when off-frame / behind the camera."""
    scene = bpy.context.scene
    w, h = scene.render.resolution_x, scene.render.resolution_y
    result = {}
    for o in bpy.data.objects:
        if not o.name.startswith("LM_"):
            continue
        x, y, z = world_to_camera_view(scene, cam_obj, o.matrix_world.translation)
        inside = z > 0 and 0 <= x <= 1 and 0 <= y <= 1
        result[o.name[3:]] = (x * w, (1 - y) * h) if inside else None
    return result


def landmark_errors(projected, photo):
    """Pixel distance per landmark present (and on-frame) in both, and their RMS (None if no pairs)."""
    errors = {}
    for name, (px, py) in photo.items():
        p = projected.get(name)
        if p is not None:
            errors[name] = math.hypot(p[0] - px, p[1] - py)
    if not errors:
        return {}, None
    return errors, math.sqrt(sum(e * e for e in errors.values()) / len(errors))


def _project_np(cam_vec, points, size):
    """Pinhole projection matching match_camera (36 mm sensor on the longer side); nan when behind."""
    loc, look, lens, roll = cam_vec[:3], cam_vec[3:6], cam_vec[6], math.radians(cam_vec[7])
    f = look - loc
    f = f / np.linalg.norm(f)
    right = np.cross(f, (0, 0, 1.0))
    right /= np.linalg.norm(right)
    up = np.cross(right, f)
    right, up = right * math.cos(roll) + up * math.sin(roll), up * math.cos(roll) - right * math.sin(roll)
    v = points - loc
    z = v @ f
    fpx = lens / 36 * max(size)
    px = size[0] / 2 + fpx * (v @ right) / z
    py = size[1] / 2 - fpx * (v @ up) / z
    px[z <= 0] = np.nan
    return px, py


def _nelder_mead(fn, x0, steps, iters=3000, tol=1e-6):
    pts = [np.array(x0, float)] + [np.array(x0, float) + np.eye(len(x0))[i] * s for i, s in enumerate(steps)]
    vals = [fn(p) for p in pts]
    for _ in range(iters):
        order = np.argsort(vals)
        pts, vals = [pts[i] for i in order], [vals[i] for i in order]
        if abs(vals[-1] - vals[0]) < tol:
            break
        centre = np.mean(pts[:-1], axis=0)
        refl = centre + (centre - pts[-1])
        fr = fn(refl)
        if fr < vals[0]:
            exp = centre + 2 * (centre - pts[-1])
            fe = fn(exp)
            pts[-1], vals[-1] = (exp, fe) if fe < fr else (refl, fr)
        elif fr < vals[-2]:
            pts[-1], vals[-1] = refl, fr
        else:
            con = centre + 0.5 * (pts[-1] - centre)
            fc = fn(con)
            if fc < vals[-1]:
                pts[-1], vals[-1] = con, fc
            else:
                pts = [pts[0] + 0.5 * (p - pts[0]) for p in pts]
                vals = [fn(p) for p in pts]
    i = int(np.argmin(vals))
    return pts[i], vals[i]


def fit_camera(photo_size, cam0, photo_landmarks, names=None, z_range=None):
    """Find the camera (loc, look_at, lens, roll) that best projects the LM_* empties onto the photo's
    landmark pixels, starting from cam0. `names` limits the fit to some landmarks (e.g. to leave the
    ones being checked out). z_range=(lo, hi) keeps the camera height plausible (e.g. a photo taken from a
    lake shore). Returns (cam dict, RMS in px measured with Blender's own projection)."""
    names = [n for n in (names or photo_landmarks) if bpy.data.objects.get("LM_" + n)]
    pts = np.array([bpy.data.objects["LM_" + n].matrix_world.translation for n in names])
    target = np.array([photo_landmarks[n] for n in names], float)

    def cost(p):
        if p[6] < 8 or p[6] > 200:
            return 1e9
        if z_range and not z_range[0] <= p[2] <= z_range[1]:
            return 1e9
        px, py = _project_np(p, pts, photo_size)
        d2 = (px - target[:, 0]) ** 2 + (py - target[:, 1]) ** 2
        return float(np.nanmean(d2) + 1e6 * np.isnan(d2).sum())

    x = np.array([*cam0["loc"], *cam0["look_at"], cam0["lens_mm"], cam0.get("roll_deg", 0)], float)
    if z_range:
        x[2] = min(max(x[2], z_range[0]), z_range[1])
    for _ in range(4):                      # restarts escape flat simplices
        x, _ = _nelder_mead(cost, x, [0.2, 0.2, 0.2, 0.1, 0.1, 0.1, 4, 3])
    cam = {"loc": [round(float(v), 4) for v in x[:3]], "look_at": [round(float(v), 4) for v in x[3:6]],
           "lens_mm": round(float(x[6]), 2), "roll_deg": round(float(x[7]), 2)}
    projected = project_landmarks(match_camera(photo_size, cam))
    _, rms = landmark_errors(projected, {n: photo_landmarks[n] for n in names})
    return cam, rms


def _load_pixels(path):
    img = bpy.data.images.load(str(path), check_existing=False)
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)   # rows bottom-up
    bpy.data.images.remove(img)
    return px


def _mark(px, x, y, colour, r=4):
    h, w = px.shape[:2]
    row = int(round(h - 1 - y))
    col = int(round(x))
    px[max(0, row - r):min(h, row + r + 1), max(0, col - r):min(w, col + r + 1), :3] = colour


def _save_overlay_crop(overlay, mask, photo_landmarks, out_png, margin=40, max_side=1000):
    """The one image to look at per round: overlay cropped to model + landmarks, at most max_side px."""
    h, w = overlay.shape[:2]
    rows, cols = np.nonzero(mask)
    ys = list(rows) + [h - 1 - y for _, y in photo_landmarks.values()]
    xs = list(cols) + [x for x, _ in photo_landmarks.values()]
    if not xs:
        ys, xs = [0, h - 1], [0, w - 1]
    r0, r1 = max(0, int(min(ys)) - margin), min(h, int(max(ys)) + margin + 1)
    c0, c1 = max(0, int(min(xs)) - margin), min(w, int(max(xs)) + margin + 1)
    crop = overlay[r0:r1, c0:c1]
    step = max(1, math.ceil(max(crop.shape[:2]) / max_side))
    crop = np.ascontiguousarray(crop[::step, ::step])
    img = bpy.data.images.new("__overlay", crop.shape[1], crop.shape[0])
    img.pixels[:] = crop.ravel()
    p = Path(out_png).resolve()
    img.filepath_raw = str(p.with_name(p.stem + "_overlay.png"))
    img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)


def compare_image(photo_path, cam, out_png, photo_landmarks):
    """Render the scene from the matched camera and write photo | render | overlay side by side.
    Overlay: the render's outline in magenta on the photo, photo landmarks green, model landmarks red.
    Returns the landmark RMS error in pixels (None if no landmark pairs)."""
    scene = bpy.context.scene
    photo = _load_pixels(photo_path)
    h, w = photo.shape[:2]
    cam_obj = match_camera((w, h), cam)

    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'SINGLE'
    scene.display.shading.single_color = (0.8, 0.8, 0.8)
    scene.render.film_transparent = True
    scene.render.image_settings.color_mode = 'RGBA'
    tmp = str(Path(out_png).resolve()) + ".render.png"
    scene.render.filepath = tmp
    bpy.ops.render.render(write_still=True)
    render = _load_pixels(tmp)
    Path(tmp).unlink()

    alpha = render[:, :, 3]
    grey = np.full_like(photo, 0.35)
    grey[:, :, 3] = 1
    render_panel = grey * (1 - alpha[..., None]) + render * alpha[..., None]
    render_panel[:, :, 3] = 1

    mask = alpha > 0.5
    inner = mask.copy()
    for axis, shift in ((0, 1), (0, -1), (1, 1), (1, -1)):
        inner &= np.roll(mask, shift, axis=axis)
    edge = mask & ~inner
    edge |= np.roll(edge, 1, axis=0) | np.roll(edge, 1, axis=1)
    overlay = photo.copy()
    overlay[edge, :3] = (1.0, 0.0, 1.0)

    projected = project_landmarks(cam_obj)
    errors, rms = landmark_errors(projected, photo_landmarks)
    for name, (x, y) in photo_landmarks.items():
        _mark(overlay, x, y, (0.0, 1.0, 0.0))
        p = projected.get(name)
        if p is not None:
            for t in np.linspace(0, 1, 40):
                _mark(overlay, x + (p[0] - x) * t, y + (p[1] - y) * t, (1.0, 1.0, 0.0), r=0)
            _mark(overlay, p[0], p[1], (1.0, 0.0, 0.0))

    sheet = np.concatenate([photo, render_panel, overlay], axis=1)
    out = bpy.data.images.new("__compare", sheet.shape[1], h)
    out.pixels[:] = sheet.ravel()
    out.filepath_raw = str(Path(out_png).resolve())
    out.file_format = 'PNG'
    out.save()
    bpy.data.images.remove(out)
    _save_overlay_crop(overlay, mask, photo_landmarks, out_png)
    for name, e in sorted(errors.items(), key=lambda kv: -kv[1]):
        print(f"  {name:20s} {e:6.1f} px")
    return rms


# ---------------------------------------------------------------- shared bake + multi-part export

def export_obj(obj, path):
    """OBJ with the engine settings of asset_lib.bake_and_export (selected object only)."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.obj_export(filepath=str(path), export_selected_objects=True, forward_axis='NEGATIVE_Z',
                          up_axis='Y', export_triangulated_mesh=True, export_normals=True, export_uv=True,
                          export_materials=False, apply_modifiers=True, global_scale=1.0)


def bake_shared_and_export(parts, pivots, out_dir, name, res=1024, samples=32):
    """Bake all parts into ONE texture, then write one OBJ per part (origin at its pivot, vertices relative
    to it) plus <name>.png and <name>_parts.json. Pivots are in Blender coordinates. Returns the json dict."""
    import bmesh
    out_dir = str(Path(out_dir).resolve())
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    for key, objs in parts.items():                       # one vertex group per part
        for o in objs:
            if o.type != 'MESH':
                bpy.context.view_layer.objects.active = o
                bpy.ops.object.convert(target='MESH')
    bpy.ops.object.select_all(action='DESELECT')
    for objs in parts.values():                           # bake transforms so the joined origin is the world origin
        for o in objs:
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for key, objs in parts.items():
        for o in objs:
            vg = o.vertex_groups.new(name=key)
            vg.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')
    joined = al.join_all("__joined", objects=[o for objs in parts.values() for o in objs])
    joined.location = (0, 0, 0)

    with tempfile.TemporaryDirectory() as tmp:
        _, png = al.bake_and_export(joined, tmp, name, res, samples=samples, keep_origin=True)
        shutil.copyfile(png, str(Path(out_dir) / (name + ".png")))

    info = {"texture": name + ".png", "parts": []}
    for key in parts:
        idx = joined.vertex_groups[key].index
        part = joined.copy()
        part.data = joined.data.copy()
        part.name = part.data.name = f"{name}_{key}"
        bpy.context.scene.collection.objects.link(part)
        bm = bmesh.new()
        bm.from_mesh(part.data)
        layer = bm.verts.layers.deform.verify()
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if idx not in v[layer]], context='VERTS')
        pivot = Vector(pivots[key])
        bmesh.ops.translate(bm, vec=-pivot, verts=bm.verts)
        bm.to_mesh(part.data)
        bm.free()
        part.vertex_groups.clear()
        part.location = (0, 0, 0)
        obj_name = f"{name}_{key}.obj"
        export_obj(part, Path(out_dir) / obj_name)
        print(f"part {key}: tris {al.tri_count(part)}")
        info["parts"].append({"name": key, "obj": obj_name, "pivot": [round(v, 5) for v in pivot]})
    (Path(out_dir) / (name + "_parts.json")).write_text(json.dumps(info, indent=2), encoding="utf-8")
    return info
