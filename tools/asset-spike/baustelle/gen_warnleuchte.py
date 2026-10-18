# Warnleuchte: German road-works battery warning lamp (Nissen Euro-Nitra / Horizont type) that the game
# places on top of Leitbaken and Absperrschranken. References: ref/baustelle/16.jpg (close-up),
# 03.jpg (on a Leitbake), 10.jpg (red lenses on barrier gates).
#
# Run headless:
#   "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup \
#       --python tools/asset-spike/baustelle/gen_warnleuchte.py [-- gelb rot]
#
# Outputs (tools/asset-spike/out/baustelle/warnleuchte/):
#   PROP_Warnleuchte_<v>.obj/.png       full lamp, v = gelb (amber lens) | rot (red lens)
#   PROP_Warnleuchte_lens_<v>.obj/.png  lens domes only, same coordinates as the full lamp but pushed
#                                       LENS_LIFT outwards along the lens axis, to be drawn on top (blinking)
#
# Origin = bottom centre of the mounting clamp = the point that sits on the carrier's top edge.
# The two clamp jaws hang below the origin (z < 0) and straddle a board up to GAP thick.
# Blender Z-up, 1 unit = 1 m, front (lens) faces -Y. The lamp is two-sided (lens dome front and back).
import bpy, bmesh, math, os, sys
import numpy as np
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # tools/asset-spike
sys.path.insert(0, ROOT)
import importlib, asset_lib as al
importlib.reload(al)

OUT = os.path.join(ROOT, "out", "baustelle", "warnleuchte")
WORK = os.path.join(OUT, "_work")          # generated pattern images (lens Fresnel, label)
os.makedirs(WORK, exist_ok=True)

# Everything is modelled LIFT metres higher than it ends up: the shared weathering material fades
# "ground grime" in from object Z = 0.25 m down to Z = 0, which is meant for props standing on the road.
# This lamp is mounted ~1 m up, so it is baked as if its clamp seat were 0.15 m above the ground: only a
# faint road-spray gradient reaches the clamp, foot and lowest ~10 cm of the housing. The joined object
# keeps the lifted mesh (local coords) and gets location z = -LIFT, so the bake sees the lifted
# coordinates while the OBJ export (world space) puts the clamp seat exactly at the origin.
LIFT = 0.15

SEG = 32                      # segments around the lens head
# Proportions measured on 03.jpg (lamp on a 250 mm Leitbake), in units of the lens diameter:
# housing width 1.11, yellow housing height 0.72 (raised after review; 03 ~0.6-0.85, 16 ~0.7), black foot 0.16, handle 0.14 above the lens,
# central column 0.51. Lens Ø 180 mm -> total 0.358 m above the seat.
# Battery housing (front view: rectangle with steep slanted shoulders, 03.jpg)
W, D = 0.200, 0.104
ZB, ZT = 0.025, 0.155         # bottom (3 mm inside the foot), top: housing 0.13 m (review: ~0.7x lens)
ZS = ZT - 0.031               # shoulder start (shoulders ~51° steep)
WT = 0.150                    # top width
COLW = 0.092                  # raised central column (grooves either side, 03.jpg)
# Lens head (centred on the Y axis through (0, *, ZC))
R_L = 0.090                   # visible lens radius (Ø 180 mm)
R_B = 0.096                   # yellow bezel outer radius (Ø 192 mm)
HY = 0.036                    # bezel half depth (lens head 72 mm deep)
RIM_Y = 0.031                 # lens rim sits 5 mm inside the bezel bore
APEX_Y = 0.049                # dome apex (dome height 18 mm)
ZC = ZT - 0.002 + R_L         # lens bottom dips 2 mm below the housing top (0.220)
# Carry handle: yellow arc above the bezel (03.jpg / 10.jpg)
H_R = 0.110                   # handle centre-line radius at the top (outer edge 25 mm above the lens)
H_T = 0.010                   # radial thickness
H_D = 0.026                   # depth (Y)
H_A0 = math.radians(28)       # handle leaves the bezel at 28° / 152°
# Black foot + clamp
BW, BD, BH = 0.194, 0.094, 0.028
GAP, JT, JW, JH = 0.028, 0.005, 0.060, 0.030   # Leitbake board is 21 mm thick, Absperrschranke rail Ø36
LENS_LIFT = 0.003             # lens overlay offset along the lens axis

YELLOW = (0.90, 0.52, 0.004)  # RAL 1023-ish traffic yellow (linear) -> sRGB ~ (245, 190, 12)

# Lens colours in sRGB 0..1: (hot centre, mid, rim). The pattern PNG is read as sRGB by Blender.
LENS = {
    "gelb": dict(hot=(1.00, 0.80, 0.36), mid=(1.00, 0.58, 0.07), rim=(0.96, 0.47, 0.02)),
    "rot":  dict(hot=(1.00, 0.50, 0.40), mid=(0.95, 0.15, 0.11), rim=(0.80, 0.06, 0.06)),
}


def z(v):
    return v + LIFT


# ---------------------------------------------------------------- generated images

def save_image(name, rgb, path):
    """rgb: (h, w, 3) float array, row 0 = bottom (Blender order), sRGB values."""
    h, w, _ = rgb.shape
    img = bpy.data.images.new(name, w, h)
    px = np.ones((h, w, 4), dtype=np.float32)
    px[:, :, :3] = np.clip(rgb, 0, 1)
    img.pixels[:] = px.ravel()
    img.filepath_raw = path; img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)
    return path


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def lens_pattern(variant, lit=False, res=1024):
    """Fresnel lens texture over the square [-R_L, R_L]^2 (u = x, v = z - ZC):
    radial colour gradient (hot centre), saw-tooth Fresnel rings with a dark step line, faint radial
    prism segments in the outer zone, a plain rim band, central bullseye and three screw bosses
    (12, 5 and 7 o'clock, as on the Euro-Nitra in 16.jpg). `lit` = brighter 'on' version for the overlay."""
    c = LENS[variant]
    hot, mid, rim = (np.array(c[k]) for k in ("hot", "mid", "rim"))
    s = (np.arange(res) + 0.5) / res * 2 - 1
    X, Y = np.meshgrid(s, s)                       # Y = row index = up (row 0 = bottom)
    rho = np.sqrt(X * X + Y * Y)                   # 0..1 inside the lens
    r = rho * R_L                                  # metres
    phi = np.arctan2(Y, X)

    hot_w = 0.50 if lit else 0.36
    t1 = smooth(0.0, hot_w, rho)[..., None]
    t2 = smooth(0.60, 1.0, rho)[..., None]
    col = hot * (1 - t1) + mid * t1
    col = col * (1 - t2) + rim * t2

    # Fresnel rings: brightness ramps across each 6.5 mm zone, dark step line at the zone boundary.
    P = 0.0065
    f = (r / P) % 1.0
    ring = 0.92 + 0.12 * f ** 1.6
    ring = np.where(f < 0.10, 0.86, ring)
    zone = (rho > 0.16) & (rho < 0.93)
    b = np.where(zone, ring, 1.0)
    # prism segments in the outer zone (spider-web look in 16.jpg)
    seg = 1.0 + 0.025 * np.sign(np.sin(phi * 24)) * smooth(0.45, 0.6, rho)
    b = b * np.where(zone, seg, 1.0)
    # bullseye: bright centre, dark ring around it
    b = np.where((rho > 0.13) & (rho <= 0.16), 0.91, b)
    b = np.where(rho <= 0.13, 1.04, b)
    # rim band (flat border of the lens), slightly darker, thin dark line at its inner edge
    b = np.where((rho >= 0.93) & (rho < 0.945), 0.82, b)
    b = np.where(rho >= 0.945, 0.93, b)
    # screw bosses at 12, 5 and 7 o'clock (16.jpg)
    for ang in (90, -60, -120):
        a = math.radians(ang)
        bx, by = 0.875 * math.cos(a), 0.875 * math.sin(a)
        d = np.sqrt((X - bx) ** 2 + (Y - by) ** 2) * R_L
        b = np.where(d < 0.0072, 0.96, b)
        b = np.where((d >= 0.0058) & (d < 0.0072), 0.80, b)
        b = np.where(d < 0.0022, 0.85, b)
    if lit:
        b = b * 1.06
    out = col * b[..., None]
    # lens outside the circle: rim colour (only the bleed area of the texture)
    out = np.where((rho > 1.0)[..., None], rim * 0.9, out)
    path = os.path.join(WORK, f"lens_pattern_{variant}{'_lit' if lit else ''}.png")
    return save_image("lens_pattern", out, path)


def label_image(res=(256, 128)):
    """Generic type-plate sticker (no brand): off-white, grey border, dark 'text' lines, small logo block."""
    w, h = res
    img = np.ones((h, w, 3)) * np.array([0.92, 0.92, 0.88])
    rows = np.arange(h)[:, None]; cols = np.arange(w)[None, :]
    border = (rows < 4) | (rows >= h - 4) | (cols < 4) | (cols >= w - 4)
    img[border] = (0.55, 0.55, 0.52)
    rng = np.random.default_rng(7)
    # text lines from the top (row index counts from the bottom)
    lines = [(h - 22, 12, 150), (h - 48, 9, 190), (h - 70, 9, 120), (h - 92, 9, 170)]
    for top, th, length in lines:
        x = 16
        while x < 16 + length:
            wl = int(rng.integers(6, 22))
            img[top - th:top, x:min(x + wl, 16 + length)] = (0.12, 0.12, 0.12)
            x += wl + int(rng.integers(3, 7))
    img[h - 30:h - 12, w - 60:w - 16] = (0.12, 0.25, 0.55)      # small blue logo block
    return save_image("label", img, os.path.join(WORK, "label.png"))


# ---------------------------------------------------------------- geometry helpers

def mesh_object(name, bm, mat):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    if mat is not None:
        me.materials.append(mat)
    return o


def lathe(name, profile, zc, mat, segs=SEG):
    """Surface of revolution around the Y axis through (0, *, zc). profile = [(r, y), ...]; a point with
    r == 0 becomes a single centre vertex (fan). Face normal = d(profile) x d(angle), i.e. walking the
    profile 'right-handed' around the axis: outward for the bezel A..F sequence, the back dome rim->centre
    and the front dome centre->rim."""
    bm = bmesh.new()
    angs = [2 * math.pi * j / segs for j in range(segs)]
    rings = []
    for r, y in profile:
        if r == 0:
            rings.append(bm.verts.new((0, y, zc)))
        else:
            rings.append([bm.verts.new((r * math.cos(a), y, zc + r * math.sin(a))) for a in angs])
    for i in range(len(profile) - 1):
        A, B = rings[i], rings[i + 1]
        for j in range(segs):
            k = (j + 1) % segs
            if isinstance(A, list) and isinstance(B, list):
                bm.faces.new((A[j], B[j], B[k], A[k]))
            elif isinstance(A, list):
                bm.faces.new((A[j], B, A[k]))
            else:
                bm.faces.new((A, B[j], B[k]))
    return mesh_object(name, bm, mat)


def handle_radius(a):
    """Centre-line radius of the carry handle: leaves the bezel at H_A0 and rises to H_R within 22°."""
    ramp = math.radians(22)
    t = min(1.0, (a - H_A0) / ramp, (math.pi - H_A0 - a) / ramp)
    t = max(0.0, t); t = t * t * (3 - 2 * t)
    return (R_B - 0.001) + (H_R - R_B + 0.001) * t


def handle(name, mat, n=14):
    bm = bmesh.new()
    secs = []
    for i in range(n + 1):
        a = H_A0 + (math.pi - 2 * H_A0) * i / n
        rc = handle_radius(a)
        ca, sa = math.cos(a), math.sin(a)
        sec = []
        for dr, dy in ((-H_T / 2, -H_D / 2), (H_T / 2, -H_D / 2), (H_T / 2, H_D / 2), (-H_T / 2, H_D / 2)):
            rr = rc + dr
            sec.append(bm.verts.new((rr * ca, dy, z(ZC) + rr * sa)))
        secs.append(sec)
    for i in range(n):
        for k in range(4):
            bm.faces.new((secs[i][k], secs[i][(k + 1) % 4], secs[i + 1][(k + 1) % 4], secs[i + 1][k]))
    # orient every face away from the centre line
    bm.normal_update()
    for f in bm.faces:
        c = f.calc_center_median()
        a = math.atan2(c.z - z(ZC), c.x)
        rc = handle_radius(a)
        p = Vector((rc * math.cos(a), 0, z(ZC) + rc * math.sin(a)))
        if f.normal.dot(c - p) < 0:
            f.normal_flip()
    bm.normal_update()
    return mesh_object(name, bm, mat)


def housing_body(name, mat):
    """Battery housing: front-view outline with slanted shoulders, extruded along Y, bevelled."""
    bm = bmesh.new()
    outline = [(-W / 2, ZB), (W / 2, ZB), (W / 2, ZS), (WT / 2, ZT), (-WT / 2, ZT), (-W / 2, ZS)]
    fr = [bm.verts.new((x, -D / 2, z(zz))) for x, zz in outline]
    bk = [bm.verts.new((x, D / 2, z(zz))) for x, zz in outline]
    bm.faces.new(fr); bm.faces.new(list(reversed(bk)))
    n = len(outline)
    for i in range(n):
        bm.faces.new((fr[i], fr[(i + 1) % n], bk[(i + 1) % n], bk[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    o = mesh_object(name, bm, mat)
    al.add_bevel(o, 0.009, 2, 30)
    return o


def disc(name, r, loc, mat, verts=12, facing=-1):
    """Flat disc decal in the XZ plane facing -Y (facing=-1) or +Y."""
    bm = bmesh.new()
    angs = [2 * math.pi * j / verts for j in range(verts)]
    vs = [bm.verts.new((loc[0] + r * math.cos(a), loc[1], loc[2] + r * math.sin(a))) for a in angs]
    f = bm.faces.new(vs if facing < 0 else list(reversed(vs)))
    return mesh_object(name, bm, mat)


def planar_lens_uv(obj):
    al.set_src_uv(obj, lambda co, n: (co.x / (2 * R_L) + 0.5, (co.z - z(ZC)) / (2 * R_L) + 0.5))


def lens_domes(prefix, mat, push=0.0):
    """Front (-Y) and back (+Y) Fresnel domes. Rim at (R_L, ±RIM_Y), spherical-cap profile."""
    s = APEX_Y - RIM_Y
    rho = (R_L ** 2 + s ** 2) / (2 * s)            # sphere radius of the cap

    def y_at(r):
        return RIM_Y + s - (rho - math.sqrt(rho ** 2 - r ** 2))
    radii = [0.0, 0.030, 0.062, R_L]
    front = lathe(prefix + "_front", [(r, -(y_at(r) + push)) for r in radii], z(ZC), mat)
    back = lathe(prefix + "_back", [(r, y_at(r) + push) for r in reversed(radii)], z(ZC), mat)
    for o in (front, back):
        planar_lens_uv(o)
    return [front, back]


# ---------------------------------------------------------------- build

def build_lamp(variant):
    al.clear_scene()
    HOUSING = al.material("housing_yellow", YELLOW, 0.45, dust=0.16, streaks=0.6, grime=0.38,
                          scratches=0.28, mottle=0.10)
    BEZEL = al.material("bezel_yellow", YELLOW, 0.45, dust=0.14, streaks=0.5, grime=0.32,
                        scratches=0.22, mottle=0.08)
    BLACK = al.material("black_plastic", (0.016, 0.016, 0.017), 0.7, dust=0.30, streaks=0.3, grime=0.25,
                        scratches=0.3, mottle=0.25)
    METAL = al.material("clamp_metal", (0.035, 0.035, 0.038), 0.5, dust=0.25, streaks=0.3, grime=0.3,
                        scratches=0.45, mottle=0.2)
    KNOB = al.material("switch_knob", (0.50, 0.51, 0.53), 0.3, dust=0.1, streaks=0.1, grime=0.25,
                       scratches=0.1, mottle=0.1)
    DARK = al.flat("dark_ring", (0.02, 0.02, 0.022))
    LENSMAT = al.material(f"lens_{variant}", (1, 1, 1), 0.2, dust=0.06, streaks=0.15, grime=0.12,
                          scratches=0.02, mottle=0.03, image=lens_pattern(variant))

    parts = []
    # lens head: bezel ring (front face, outer band, back face, short inner walls of the bore)
    parts.append(lathe("bezel", [(R_L, -RIM_Y), (R_L, -HY), (R_B, -HY), (R_B, HY), (R_L, HY), (R_L, RIM_Y)],
                       z(ZC), BEZEL))
    parts += lens_domes("lens", LENSMAT)
    parts.append(handle("handle", BEZEL))

    # battery housing with raised central column
    parts.append(housing_body("housing", HOUSING))
    col_h = (ZT - 0.0015) - (ZB + 0.001)
    for sy in (-1, 1):   # raised central column, front and back (only 7 mm deep, 4 mm sunk into the body)
        parts.append(al.box(f"column_{sy}", (COLW, 0.007, col_h), (0, sy * (D / 2 - 0.0005), z(ZB + 0.001 + col_h / 2)),
                            HOUSING, bevel=0.003, segments=1))
    # neck: yellow cradle block under the lens head (16.jpg), hides the bezel/lens bottom joint
    parts.append(al.box("neck", (0.070, 2 * HY + 0.014, 0.016), (0, 0, z(ZT + 0.004)), HOUSING, bevel=0.005,
                        segments=2))
    yf = -(D / 2 + 0.003)                                   # front face of the column
    parts.append(al.image_plane("label", label_image(), 0.054, 0.028, (0, yf - 0.001, z(0.094))))
    parts.append(disc("switch_ring", 0.014, (0, yf - 0.001, z(0.050)), DARK, 12))
    parts.append(al.cyl("switch_knob", 0.0095, 0.009, (0, yf - 0.0035, z(0.050)), KNOB, axis='Y', verts=12,
                        bevel=0, r2=0.0075))
    for sx in (-0.012, 0.012):
        parts.append(disc(f"sensor_{sx}", 0.0028, (sx, yf - 0.001, z(0.138)), DARK, 6))

    # black foot (sits on the carrier) + clamp jaws straddling the board, wing screw at the front
    parts.append(al.box("foot", (BW, BD, BH), (0, 0, z(BH / 2)), BLACK, bevel=0.004, segments=2))
    for sy in (-1, 1):
        parts.append(al.box(f"jaw_{sy}", (JW, JT, JH + 0.002), (0, sy * (GAP / 2 + JT / 2), z(-JH / 2 + 0.001)),
                            METAL, bevel=0.0015, segments=1))
    parts.append(al.cyl("screw", 0.0035, 0.012, (0, -(GAP / 2 + JT + 0.005), z(-0.015)), METAL, axis='Y',
                        verts=8, bevel=0))
    parts.append(al.box("wing", (0.034, 0.004, 0.009), (0, -(GAP / 2 + JT + 0.012), z(-0.015)), METAL,
                        bevel=0.0015, segments=1))

    obj = al.join_all(f"PROP_Warnleuchte_{variant}", smooth_angle=50, objects=parts)
    return finalize(obj)


def finalize(obj):
    """Apply transforms (mesh in lifted world coords, origin at world 0), then drop the object by LIFT so
    the clamp seat is at the world origin while the bake still sees the lifted local coordinates."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.location = (0, 0, -LIFT)
    bpy.context.view_layer.update()
    return obj


def build_overlay(variant):
    # 'on' state: flat emissive look, no grime/AO crevice term (and baked with ao_strength=0 below)
    mat = al.material(f"lens_on_{variant}", (1, 1, 1), 0.2, dust=0.0, streaks=0.0, grime=0.0,
                      scratches=0.0, mottle=0.02, image=lens_pattern(variant, lit=True))
    parts = lens_domes("lens_overlay", mat, push=LENS_LIFT)
    obj = al.join_all(f"PROP_Warnleuchte_lens_{variant}", smooth_angle=50, objects=parts)
    return finalize(obj)


CARRIERS = {   # context check on the finished carriers (other agents' outputs, read-only)
    "gelb": ("leitbake", "PROP_Leitbake_rechts"),          # 03.jpg
    "rot": ("absperrschranke", "PROP_Absperrschranke_gelb"),  # 10.jpg: red lamps on yellow gates
}


def context_previews(lamp, lens, variant):
    """Import the carrier and put lamp + lens overlay on every mount from its mounts.json."""
    import json
    folder, name = CARRIERS[variant]
    base = os.path.join(ROOT, "out", "baustelle", folder)
    path = os.path.join(base, name + ".obj")
    if not os.path.exists(path):
        print("context: carrier missing", path)
        return
    carrier = al.import_obj(path, os.path.join(base, name + ".png"), "ctx_" + name)
    mounts = json.load(open(os.path.join(base, "mounts.json")))["mounts"]
    lamps = []
    for i, m in enumerate(mounts):
        for src in (lamp, lens):
            o = src
            if i:
                o = src.copy(); bpy.context.scene.collection.objects.link(o)
            o.location = (m["x"], m["y"], m["z"] - LIFT)
            lamps.append(o)
    bpy.context.view_layer.update()
    al.render_previews(carrier, os.path.join(OUT, f"{lamp.name}_context.png"),
                       views=("front", "three_quarter", (1, -0.25, 0.2)), extra_objects=lamps)
    # close-up of the first lamp, carrier visible around it: clamp jaws straddling the top edge
    al.render_previews(lamp, os.path.join(OUT, f"{lamp.name}_mountcheck.png"),
                       views=("front", (1, -0.6, 0.35), (1, 0, -0.1)))


def run(variants):
    for v in variants:
        lamp = build_lamp(v)
        print("tris lamp", v, al.tri_count(lamp))
        al.bake_and_export(lamp, OUT, lamp.name, res=512, keep_origin=True)
        al.render_previews(lamp, os.path.join(OUT, f"{lamp.name}_preview.png"),
                           views=("front", "three_quarter", "side", "back", (0.35, -1, 0.9)))
        lens = build_overlay(v)
        print("tris lens", v, al.tri_count(lens))
        al.bake_and_export(lens, OUT, lens.name, res=512, keep_origin=True, ao_strength=0.0)
        al.render_previews(lens, os.path.join(OUT, f"{lens.name}_preview.png"),
                           views=("front", "three_quarter", "side"))
        context_previews(lamp, lens, v)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    run(argv or list(LENS))
