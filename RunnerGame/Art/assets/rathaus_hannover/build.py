"""Neues Rathaus Hannover, blockout backdrop built from spec.json.

Blender Z-up, metres. Static prop: the Maschteich facade faces -Y, origin = footprint centre on the ground.
Every number comes from spec.json; fix measurements there, never here.

Headless:  blender --background --factory-startup --python RunnerGame/Art/assets/rathaus_hannover/build.py -- [--preview out.png | --export]
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "lib"))
import photo_lib as pl  # noqa: E402

al = pl.al
bpy = pl.bpy


def mesh_obj(name, verts, faces, mat):
    import bmesh
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    if mat is not None:
        me.materials.append(mat)
    return o


def frustum(name, cx, cy, z0, z1, w0, d0, w1, d1, mat):
    """Rectangular frustum (hip roof); bottom w0 x d0 at z0, top w1 x d1 at z1."""
    v = [(cx + sx * w0 / 2, cy + sy * d0 / 2, z0) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    v += [(cx + sx * w1 / 2, cy + sy * d1 / 2, z1) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return mesh_obj(name, v, f, mat)


def lathe(name, cx, cy, profile, mat, seg=16):
    """Solid of revolution about the Z axis through (cx, cy); profile = [(radius, z)] bottom to top.
    A radius of 0 makes an apex; open (non-zero radius) ends get a flat cap."""
    v, f, rings = [], [], []
    for r, z in profile:
        if r <= 1e-6:
            rings.append(("apex", len(v)))
            v.append((cx, cy, z))
        else:
            rings.append(("ring", len(v)))
            v += [(cx + r * math.cos(2 * math.pi * i / seg), cy + r * math.sin(2 * math.pi * i / seg), z)
                  for i in range(seg)]
    for (ka, a), (kb, b) in zip(rings, rings[1:]):
        for i in range(seg):
            j = (i + 1) % seg
            if ka == "ring" and kb == "ring":
                f.append((a + i, a + j, b + j, b + i))
            elif ka == "apex":
                f.append((a, b + j, b + i))
            else:
                f.append((a + i, a + j, b))
    for kind, base in (rings[0], rings[-1]):
        if kind == "ring":
            f.append(tuple(base + i for i in range(seg)))
    return mesh_obj(name, v, f, mat)


def boxes(name, specs, mat):
    """One mesh of axis-aligned boxes; specs = [(cx, cy, cz, sx, sy, sz)]."""
    v, f = [], []
    for cx, cy, cz, sx, sy, sz in specs:
        b = len(v)
        for ix in (-1, 1):
            for iy in (-1, 1):
                for iz in (-1, 1):
                    v.append((cx + ix * sx / 2, cy + iy * sy / 2, cz + iz * sz / 2))
        f += [(b + i, b + j, b + k, b + m) for i, j, k, m in
              ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3))]
    return mesh_obj(name, v, f, mat)


def arch_outline(cx, zb, w, h, n=6):
    """Convex (x, z) outline of a rectangle with a semicircular top, sill at zb, total height h."""
    r = w / 2
    zs = zb + h - r
    pts = [(cx - r, zb), (cx + r, zb)]
    pts += [(cx + r * math.cos(math.pi * i / n), zs + r * math.sin(math.pi * i / n)) for i in range(n + 1)]
    return pts


def prisms(name, items, mat):
    """One mesh of prisms; items = [(outline_xz, y0, y1)], outline counter-clockwise seen from -Y."""
    v, f = [], []
    for pts, y0, y1 in items:
        b, k = len(v), len(pts)
        v += [(x, y0, z) for x, z in pts] + [(x, y1, z) for x, z in pts]
        f.append(tuple(range(b, b + k)))
        f.append(tuple(range(b + 2 * k - 1, b + k - 1, -1)))
        f += [(b + i, b + (i + 1) % k, b + k + (i + 1) % k, b + k + i) for i in range(k)]
    return mesh_obj(name, v, f, mat)


def build(spec):
    d, c = spec.d, spec.c
    mat = {
        "stone": al.material("stone", c("stone"), dust=0.2, streaks=0.4, grime=0.3, scratches=0.1, mottle=0.2),
        "roof": al.material("roof", c("roof"), dust=0.15, streaks=0.3, grime=0.2, scratches=0.1, mottle=0.2),
        "copper": al.material("copper", c("copper"), dust=0.1, streaks=0.4, grime=0.1, scratches=0.05, mottle=0.2),
        "window": al.flat("window", c("window")),
        "clock": al.flat("clock", c("clock")),
    }
    body = []
    add = body.append
    W, D = d("width"), d("depth")
    fy = -D / 2
    eave, ridge = d("wing_eave_h"), d("wing_roof_h")

    # main block + hipped red roof (45 degree slopes: inset equals rise)
    add(al.box("main", (W, D, eave), (0, 0, eave / 2), mat["stone"], bevel=0))
    rise = ridge - eave
    add(frustum("main_roof", 0, 0, eave, ridge, W, D, W - 2 * rise, D - 2 * rise, mat["roof"]))

    # central projection
    cw, cd, cf = d("center_w"), d("center_d"), d("center_fwd")
    ce, ch = d("center_eave_h"), d("center_h")
    cy = fy - cf + cd / 2
    add(al.box("centre", (cw, cd, ce), (0, cy, ce / 2), mat["stone"], bevel=0))
    cr = ch - ce
    add(frustum("centre_roof", 0, cy, ce, ch, cw, cd, cw - 2 * cr, cd - 2 * cr, mat["roof"]))

    # corner towers with copper spires, flush with the front facade
    tw, tb, tt = d("tower_w"), d("tower_body_h"), d("tower_tip_h")
    for side in (-1, 1):
        tx, ty = side * d("tower_x"), fy + tw / 2
        add(al.box(f"tower_{side}", (tw, tw, tb), (tx, ty, tb / 2), mat["stone"], bevel=0))
        spire = al.cyl(f"tower_spire_{side}", tw / 2 * math.sqrt(2), tt - tb, (tx, ty, (tb + tt) / 2), mat["copper"],
                       verts=4, bevel=0, r2=0.0)
        spire.rotation_euler.z = math.radians(45)
        add(spire)

    # dome group
    dy, R = d("dome_y"), d("drum_w") / 2
    dt, dm, lt, st = d("drum_top_h"), d("dome_top_h"), d("lantern_top_h"), d("spire_tip_h")
    add(lathe("drum", 0, dy, [(R, 0), (R, dt)], mat["stone"]))
    steps = 6
    dome = [(R * math.cos(math.radians(90 * i / steps)), dt + (dm - dt) * math.sin(math.radians(90 * i / steps)))
            for i in range(steps)]
    lr = R * 0.18
    add(lathe("dome", 0, dy, dome + [(lr, dm)], mat["copper"]))
    add(lathe("lantern", 0, dy, [(lr, dm), (lr, lt), (lr * 1.3, lt), (lr * 0.2, lt + (st - lt) * 0.12), (0, st)],
              mat["copper"], seg=12))

    # ---- details (all numbers in spec.json) ----
    pw = d("win_protrude")
    ww, wh = d("window_w"), d("window_h")
    ah = d("win_arch_h")
    floors = [d("win_floor1_z"), d("win_floor2_z"), d("win_floor3_z")]
    items, wboxes = [], []                                   # dark window prisms / dark boxes

    def arch(cx, zb, w, h, yface, sign=-1):
        items.append((arch_outline(cx, zb, w, h), yface, yface + sign * pw))

    # front wings: three floors of arched windows (skip towers and centre projection)
    pitch = d("window_pitch")
    x = -W / 2 + pitch
    while x < W / 2 - pitch / 2:
        if not (abs(abs(x) - d("tower_x")) < tw / 2 + 1 or abs(x) < cw / 2 + 1):
            for zb in floors:
                arch(x, zb, ww, ah, fy)
        x += pitch
    # towers: two floors of narrow windows
    for side in (-1, 1):
        for zb in (floors[1], floors[2], 24.0, 30.0):
            for dx in (-2.2, 2.2):
                arch(side * d("tower_x") + dx, zb, 1.4, 3.2, fy)

    # central projection: three entrance arches, two floors of arched windows
    yc = fy - cf
    ew, eh = d("entrance_w"), d("entrance_h")
    for ex in (-d("entrance_x"), 0.0, d("entrance_x")):
        arch(ex, 0.0, ew, eh, yc)
    cp, cww = d("centre_win_pitch"), d("centre_win_w")
    n = int((cw - 6) // cp)
    for i in range(n + 1):
        cx_ = (i - n / 2) * cp
        for zb in (floors[1] + 1.0, floors[2] + 2.0):
            arch(cx_, zb, cww, ah, yc)

    # side and rear facades: one simple grid of window boxes
    sp = d("side_pitch")
    for zb in floors:
        zc = zb + wh / 2
        y = -D / 2 + sp
        while y < D / 2 - sp / 2:
            for sx in (-1, 1):
                wboxes.append((sx * (W / 2 + pw / 2 - 0.05), y, zc, pw, ww, wh))
            y += sp
        x = -W / 2 + sp
        while x < W / 2 - sp / 2:
            wboxes.append((x, D / 2 + pw / 2 - 0.05, zc, ww, pw, wh))
            x += sp

    # cornice bands and a string course
    co, chh = d("cornice_out"), d("cornice_h")
    bands = [(0, fy - co / 2 + 0.1, eave - chh / 2, W, co, chh),
             (0, yc - co / 2 + 0.1, ce - chh / 2, cw + 1.6, co, chh),
             (0, fy - co / 2 + 0.1, d("string_course_z"), W, co * 0.7, 0.6),
             (0, yc - co / 2 + 0.1, d("string_course_z"), cw + 0.8, co * 0.7, 0.6)]
    add(boxes("cornices", bands, mat["stone"]))

    # stepped gables: central projection and both wing ends (stone walls standing on the eaves)
    gt = d("gable_t")
    steps = []
    for i in range(int(d("gable_steps"))):
        steps.append((0, yc + gt / 2, ce + (i + 0.5) * d("gable_step_h"), d("gable_w") - i * d("gable_inset"), gt, d("gable_step_h")))
    wsh = d("wing_gable_step_h")
    for side in (-1, 1):
        for i in range(3):
            steps.append((side * d("wing_gable_x"), fy + gt / 2, eave + (i + 0.5) * wsh, d("wing_gable_w") - i * 3.0, gt, wsh))
    add(boxes("gables", steps, mat["stone"]))

    # dormers on the front slope of the red roof (hip-roofed boxes with a dark window)
    dw, dh, dd = d("dormer_w"), d("dormer_h"), d("dormer_d")
    for dx in (-58, -52, -30, -24, 24, 30, 52, 58):
        zb = d("dormer_z")
        yf = fy + (zb - eave)                                # slope is 45 degrees
        cy_ = yf + dd / 2
        add(boxes(f"dormer_{dx}", [(dx, cy_, zb + dh / 2 - 0.3, dw, dd, dh + 0.6)], mat["stone"]))
        add(frustum(f"dormer_roof_{dx}", dx, cy_, zb + dh, zb + dh + 1.4, dw + 0.5, dd + 0.5, 0.3, 0.3, mat["roof"]))
        wboxes.append((dx, yf - 0.03, zb + dh / 2, dw * 0.55, 0.1, dh * 0.6))

    # copper-capped turrets at the central projection corners
    tuw, tut, tuc = d("turret_w"), d("turret_top_h"), d("turret_cap_h")
    for side in (-1, 1):
        tx_, ty_ = side * (cw / 2 - tuw / 2), yc + tuw / 2
        add(al.box(f"turret_{side}", (tuw, tuw, tut - ce + 2), (tx_, ty_, (ce - 2 + tut) / 2), mat["stone"], bevel=0))
        cap = al.cyl(f"turret_cap_{side}", tuw / 2 * math.sqrt(2) * 1.1, tuc, (tx_, ty_, tut + tuc / 2), mat["copper"],
                     verts=4, bevel=0, r2=0.0)
        cap.rotation_euler.z = math.radians(45)
        add(cap)

    # clock faces on the four sides of the drum, with two dark hands each
    cr_, cz = d("clock_r"), d("clock_z")
    for axis, sx_, sy_ in (("X", 1, 0), ("X", -1, 0), ("Y", 0, 1), ("Y", 0, -1)):
        add(al.cyl(f"clock_{sx_}_{sy_}", cr_, 0.8, (sx_ * R, dy + sy_ * R, cz), mat["clock"], axis=axis, verts=20, bevel=0))
        ox, oy = sx_ * (R + 0.45), sy_ * (R + 0.45)
        if sx_:
            wboxes += [(ox, dy, cz + cr_ * 0.25, 0.1, 0.25, cr_ * 0.6), (ox, dy + cr_ * 0.2, cz, 0.1, cr_ * 0.5, 0.25)]
        else:
            wboxes += [(0, dy + oy, cz + cr_ * 0.25, 0.25, 0.1, cr_ * 0.6), (cr_ * 0.2, dy + oy, cz, cr_ * 0.5, 0.1, 0.25)]

    add(prisms("windows_arched", items, mat["window"]))
    add(boxes("windows_boxes", wboxes, mat["window"]))

    # landmarks (names match refs.json)
    for name, loc in {
        "facade_left_base": (-W / 2, fy, 0), "facade_right_base": (W / 2, fy, 0),
        "wing_l_eave": (-W / 2, fy, eave), "wing_r_eave": (W / 2, fy, eave),
        "spire_tip": (0, dy, st), "dome_top": (0, dy, dm),
        "drum_left_top": (-R, dy, dt), "drum_right_top": (R, dy, dt),
        "tower_l_tip": (-d("tower_x"), fy + tw / 2, tt), "tower_r_tip": (d("tower_x"), fy + tw / 2, tt),
    }.items():
        pl.landmark(name, loc)
    return {"body": body}


def main(argv):
    al.clear_scene()
    parts = build(pl.Spec(HERE / "spec.json"))
    if "--export" in argv:
        out = HERE / "out"
        pl.bake_shared_and_export({"body": parts["body"]}, {"body": (0, 0, 0)}, str(out.resolve()), "BLD_NeuesRathaus",
                                  res=1024, samples=32)
        return
    if "--preview" in argv:
        objs = [o for group in parts.values() for o in group]
        out = str(Path(argv[argv.index("--preview") + 1]).resolve())   # Blender resolves relative paths oddly
        al.render_previews(objs[0], out, size=384, extra_objects=objs[1:])


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
