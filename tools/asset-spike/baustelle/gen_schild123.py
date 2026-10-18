# German traffic sign Zeichen 123 "Arbeitsstelle" (road works warning triangle), size 2 (900 mm),
# on a galvanised Ø 60.3 mm post with red plastic edge clamps (Schellen) at the apex and the bottom edge.
# Reference: tools/asset-spike/ref/baustelle/28.jpg; artwork: ref/signs/z123.png (official StVO 2013 graphic).
#
# Run headless:
#   "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup \
#       --python tools/asset-spike/baustelle/gen_schild123.py [-- post|mobil|all]
#
# Blender Z-up, 1 unit = 1 m, the sign face looks towards -Y.
# Own helpers (not in asset_lib): clean_artwork() (white plate rim instead of transparency/hairline),
# build_plate() (rounded-triangle tray with rolled edge), bake_and_export_sign() (= asset_lib.bake_and_export
# but the sign face gets a fixed, large UV region and everything else is packed around it).
import bpy, bmesh, os, sys, math
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
SPIKE = os.path.dirname(HERE)
sys.path.insert(0, SPIKE)
import asset_lib as al

ART_SRC = os.path.join(SPIKE, "ref", "signs", "z123.png")
OUT = os.path.join(SPIKE, "out", "baustelle", "schild123")
WORK = os.path.join(OUT, "_work")

# ---------------------------------------------------------------- artwork geometry (measured from z123.png)
# Pixel coordinates u right, v down, pixel i covers [i, i+1]. The outer edge of the black hairline is a rounded
# equilateral triangle: sharp side 1362.45 px, centre u 639.79, base v 1123.37, corner radius 56.6 px.
# Inside it: white rim ~15.6 px, red band ~121 px, then the (sharp-cornered) white field with the symbol.
G_W, G_H = 1280, 1124
G_CX, G_BASE, G_SIDE, G_R = 639.79, 1123.37, 1362.45, 56.6
G_INSET = 1.0                      # plate edge = centre of the hairline (1 px inside its outer edge)

# ---------------------------------------------------------------- real dimensions (m)
SQ3 = math.sqrt(3)
SIDE = 0.900                       # sharp-triangle side of the plate (StVO size 2)
PX = SIDE / (G_SIDE - 2 * SQ3 * G_INSET)   # metres per artwork pixel
R_CORNER = (G_R - G_INSET) * PX    # ~37 mm corner radius
H_TRI = SIDE * SQ3 / 2
Z0 = 2.000                         # bottom edge of the sign above ground
Z_TOP = Z0 + H_TRI - R_CORNER      # highest point of the rounded apex
T = 0.002                          # aluminium thickness
ROLL = 0.003                       # radius of the rolled front edge
RIM = 0.020                        # depth of the folded edge (visible from the side)
SEGS = 8                           # segments per rounded corner (15° steps)

POST_R = 0.0603 / 2
RAIL_W, RAIL_D = 0.040, 0.0235     # vertical mounting rail (Klemmschiene) on the back
POST_Y = T + RAIL_D + 0.0005 + POST_R
POST_TOP = Z_TOP + 0.05

FOOT_BLACK = (0.014, 0.014, 0.016)  # recycled-PVC foot plate (mobile variant)

# Mobile variant ("mobil"): temporary road-works setup, Ø 42.4 mm stand pipe in a black foot plate
# (800 x 400 mm, ~28 kg type), sign bottom edge at 1.0 m.
MOBIL_Z0, MOBIL_POST_R = 1.000, 0.0424 / 2
FOOT_W, FOOT_L, FOOT_H = 0.40, 0.80, 0.075   # x (parallel to the sign), y (long axis, against wind load), z


def configure(variant):
    """Set the variant-dependent dimensions (module globals used by all builders)."""
    global Z0, Z_TOP, POST_R, POST_Y, POST_TOP, CLAMP_RING_R
    Z0, POST_R = (2.000, 0.0603 / 2) if variant == "post" else (MOBIL_Z0, MOBIL_POST_R)
    Z_TOP = Z0 + H_TRI - R_CORNER
    POST_Y = T + RAIL_D + 0.0005 + POST_R
    POST_TOP = Z_TOP + 0.05
    CLAMP_RING_R = POST_R + 0.0024


CLAMP = 0.064                      # red clamp jaw, square (photo: ~7.5 % of the sign width)
CLAMP_RING_R = 0.0325

# Colours: linear RGB (Blender shader space)
ALU = (0.33, 0.34, 0.35)           # mill-finish aluminium, back of the sign
GALV = (0.40, 0.41, 0.42)          # galvanised steel post
CLAMP_RED = (0.56, 0.035, 0.025)   # red plastic clamps
BOLT = (0.48, 0.48, 0.49)
CAP = (0.30, 0.31, 0.32)           # galvanised steel cap, a bit darker than the post


# ---------------------------------------------------------------- artwork

def clean_artwork():
    """Copy of z123.png in which everything outside the red band (transparent area, black hairline and the
    white rim) is opaque white, so no transparent/black fringe can ever be sampled at the plate edge."""
    os.makedirs(WORK, exist_ok=True)
    src = bpy.data.images.load(ART_SRC)
    w, h = src.size
    px = np.array(src.pixels[:], dtype=np.float32).reshape(h, w, 4)
    reddish = (px[..., 0] - px[..., 1]) > 0.10
    outside = px[..., 3] < 0.5
    m = outside.copy()
    for _ in range(80):                       # flood fill from the transparent area over non-red pixels
        n = m.copy()
        n[1:] |= m[:-1]; n[:-1] |= m[1:]; n[:, 1:] |= m[:, :-1]; n[:, :-1] |= m[:, 1:]
        n &= ~reddish
        n |= outside
        if np.array_equal(n, m):
            break
        m = n
    px[m] = (1.0, 1.0, 1.0, 1.0)
    px[..., 3] = 1.0
    # Brighter border red: the engine's Phong lighting shows textures at ~0.72x, so the official red
    # (193, 18, 28) reads maroon. Shift red pixels (and the red part of anti-aliased edges) to ~(222, 38, 43),
    # which bakes to ~(215, 35, 40).
    wr = np.clip((px[..., 0] - px[..., 1]) / ((193 - 18) / 255), 0, 1)[..., None]
    px[..., :3] += wr * (np.array((222, 38, 43)) - np.array((193, 18, 28))) / 255
    px[..., :3] = np.clip(px[..., :3], 0, 1)
    out = bpy.data.images.new("z123_clean", w, h, alpha=True)
    out.pixels[:] = px.ravel()
    path = os.path.join(WORK, "z123_clean.png")
    out.filepath_raw = path; out.file_format = 'PNG'; out.save()
    bpy.data.images.remove(out); bpy.data.images.remove(src)
    return path


def art_uv(co, n=None):
    """World position on the sign face -> UV in the artwork (not mirrored: +X is right when seen from -Y)."""
    u_px = G_CX + co.x / PX
    v_px = (G_BASE - G_INSET) - (co.z - Z0) / PX
    return (u_px / G_W, 1.0 - v_px / G_H)


# ---------------------------------------------------------------- plate

def corner_centres():
    verts = [(SIDE / 2, Z0), (0.0, Z0 + H_TRI), (-SIDE / 2, Z0)]          # BR, apex, BL (counter-clockwise)
    gx, gz = 0.0, Z0 + H_TRI / 3
    out = []
    for vx, vz in verts:
        dx, dz = gx - vx, gz - vz
        l = math.hypot(dx, dz)
        out.append((vx + dx / l * 2 * R_CORNER, vz + dz / l * 2 * R_CORNER))   # 60° corner: centre 2r inside
    return out


def contour(offset):
    """Rounded-triangle outline offset by `offset` (negative = inwards), counter-clockwise seen from -Y."""
    pts = []
    for (cx, cz), (a0, a1) in zip(corner_centres(), ((-90, 30), (30, 150), (150, 270))):
        for i in range(SEGS + 1):
            a = math.radians(a0 + (a1 - a0) * i / SEGS)
            pts.append((cx + (R_CORNER + offset) * math.cos(a), cz + (R_CORNER + offset) * math.sin(a)))
    return pts


def build_plate(art_mat, alu_mat):
    """Aluminium sign plate as a shallow tray: flat face, rolled front edge, 20 mm folded rim, plain back."""
    rings = [(-ROLL - 0.0015, 0.0), (-ROLL, 0.0)]            # face n-gon + 1.5 mm flat strip (keeps normals flat)
    for phi in (30, 60, 90):                                 # rolled edge
        p = math.radians(phi)
        rings.append((-ROLL + ROLL * math.sin(p), ROLL - ROLL * math.cos(p)))
    rings += [(0.0, RIM), (-T, RIM), (-T, T)]                # folded rim, lip, inner wall down to the plate back
    n_art_bands = 4                                          # strip + 3 roll bands carry the artwork

    bm = bmesh.new()
    rv = [[bm.verts.new((x, y, z)) for x, z in contour(off)] for off, y in rings]
    face = bm.faces.new(rv[0]); face.material_index = 0
    n = len(rv[0])
    for k, (a, b) in enumerate(zip(rv, rv[1:])):
        for i in range(n):
            j = (i + 1) % n
            f = bm.faces.new((a[i], b[i], b[j], a[j]))
            f.material_index = 0 if k < n_art_bands else 1
    back = bm.faces.new(list(reversed(rv[-1]))); back.material_index = 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    assert face.normal.y < -0.99 and back.normal.y > 0.99, (face.normal, back.normal)
    me = bpy.data.meshes.new("plate")
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("plate", me)
    bpy.context.scene.collection.objects.link(o)
    me.materials.append(art_mat); me.materials.append(alu_mat)
    return o


# ---------------------------------------------------------------- clamps, post, rail

def clamp(name, zc, z_body, red, bolt):
    """Red edge clamp: square jaw with a pyramid face and a bolt in front of the plate edge, a body behind it
    (above/below the plate) bridging to a ring around the post, and a nut at the back."""
    yb = -0.001                                               # back of the jaw, 1 mm in front of the sign face
    al.box(f"{name}_jaw", (CLAMP, 0.010, CLAMP), (0, yb - 0.005, zc), red, bevel=0.003)
    ph = 0.012                                                # pyramid face (gives the diagonal ribs of the photo)
    p = al.cyl(f"{name}_pyramid", CLAMP * 0.66, ph, (0, yb - 0.010 - ph / 2 + 0.0005, zc), red, axis='Y', verts=4,
               r2=CLAMP * 0.26, bevel=0.0015, segments=1)
    p.rotation_euler.y = math.radians(45)
    yt = yb - 0.010 - ph + 0.0005                             # front of the pyramid
    al.cyl(f"{name}_washer", 0.016, 0.002, (0, yt - 0.0005, zc), bolt, axis='Y', verts=12, bevel=0)
    al.cyl(f"{name}_bolt", 0.0115, 0.006, (0, yt - 0.0045, zc), bolt, axis='Y', verts=12,
           bevel=0.002, segments=1)
    z0, z1 = z_body
    yb2 = yb - 0.002                                          # body reaches 2 mm into the jaw (no coplanar faces)
    al.box(f"{name}_body", (CLAMP * 0.86, POST_Y - yb2, z1 - z0), (0, (POST_Y + yb2) / 2, (z0 + z1) / 2), red,
           bevel=0.003, segments=1)
    al.cyl(f"{name}_ring", CLAMP_RING_R, z1 - z0, (0, POST_Y, (z0 + z1) / 2), red, verts=16, bevel=0)
    al.cyl(f"{name}_nut", 0.009, 0.008, (0, POST_Y + CLAMP_RING_R + 0.003, (z0 + z1) / 2), bolt, axis='Y',
           verts=6, bevel=0)


def build_post_mount(alu, galv, red, bolt, cap, post_bottom=0.0):
    # vertical hat-profile rail (Klemmschiene) on the back: flanges on the plate, channel with a slot
    z_r0, z_r1 = Z0 + T + 0.002, Z0 + 0.66
    y0 = T + 0.0005
    al.box("rail_flange", (RAIL_W + 0.036, 0.003, z_r1 - z_r0 - 0.01), (0, y0 + 0.0015, (z_r0 + z_r1) / 2 - 0.005),
           alu, bevel=0.001, segments=1)
    al.box("rail_body", (RAIL_W, RAIL_D - 0.005, z_r1 - z_r0), (0, y0 + (RAIL_D - 0.005) / 2, (z_r0 + z_r1) / 2),
           alu, bevel=0.002, segments=1)
    for s in (-1, 1):
        al.box(f"rail_lip_{s}", (0.014, 0.005, z_r1 - z_r0), (s * (RAIL_W / 2 - 0.007), y0 + RAIL_D - 0.0025,
               (z_r0 + z_r1) / 2), alu, bevel=0.0015, segments=1)
    # post (set into the pavement, ends at z = 0; mobile: ends inside the foot plate sleeve), with a cap
    al.cyl("post", POST_R, POST_TOP - post_bottom, (0, POST_Y, (POST_TOP + post_bottom) / 2), galv,
           verts=20 if variant_is_post() else 16, bevel=0)
    al.cyl("post_cap", POST_R + 0.0025, 0.012, (0, POST_Y, POST_TOP + 0.006), cap, verts=16, r2=POST_R - 0.004,
           bevel=0.002, segments=1)
    # clamps (as in the photo): the top jaw covers the upper 40 mm of the rounded apex (the plate sticks out on both
    # sides below it), the bottom jaw overlaps the bottom edge by 20 mm
    top_lo, top_hi = Z_TOP - 0.040, Z_TOP - 0.040 + CLAMP
    clamp("clamp_top", (top_lo + top_hi) / 2, (Z_TOP + 0.003, top_hi), red, bolt)
    bot_lo, bot_hi = Z0 + 0.020 - CLAMP, Z0 + 0.020
    clamp("clamp_bot", (bot_lo + bot_hi) / 2, (bot_lo, Z0 - 0.003), red, bolt)


def variant_is_post():
    return abs(POST_R - 0.0603 / 2) < 1e-6


def build_mobile_stand(black, galv, bolt):
    """Black foot plate with a raised centre, a galvanised socket sleeve and a T-handle clamping screw."""
    al.box("foot", (FOOT_W, FOOT_L, FOOT_H), (0, POST_Y, FOOT_H / 2), black, bevel=0.018, segments=2)
    h = al.cyl("foot_hump", 0.13 * math.sqrt(2), 0.03, (0, POST_Y, FOOT_H + 0.015 - 0.001), black, verts=4,
               r2=0.075 * math.sqrt(2), bevel=0.004, segments=1)
    h.rotation_euler.z = math.radians(45)
    sr = POST_R + 0.005
    al.cyl("sleeve", sr, 0.16, (0, POST_Y, FOOT_H + 0.08), galv, verts=16, bevel=0.002, segments=1)
    al.cyl("screw", 0.006, 0.03, (sr + 0.013, POST_Y, FOOT_H + 0.125), bolt, axis='X', verts=8, bevel=0)
    al.cyl("screw_handle", 0.005, 0.07, (sr + 0.031, POST_Y, FOOT_H + 0.125), bolt, axis='Y', verts=8, bevel=0)


def build(variant="post"):
    configure(variant)
    al.clear_scene()
    art = al.material("sign_face", (0.8, 0.8, 0.8), roughness=0.4, dust=0.15, streaks=0.35, grime=0.22,
                      scratches=0.10, mottle=0.04, image=clean_artwork())
    alu = al.material("alu", ALU, roughness=0.45, dust=0.3, streaks=0.5, grime=0.45, scratches=0.25, mottle=0.12)
    galv = al.material("galv", GALV, roughness=0.45, dust=0.3, streaks=0.6, grime=0.5, scratches=0.2, mottle=0.25)
    red = al.material("clamp_red", CLAMP_RED, roughness=0.5, dust=0.25, streaks=0.4, grime=0.4, scratches=0.2,
                      mottle=0.10)
    bolt = al.material("bolt", BOLT, roughness=0.4, dust=0.2, streaks=0.3, grime=0.4, scratches=0.2, mottle=0.15)
    cap = al.material("cap", CAP, roughness=0.6, dust=0.35, streaks=0.3, grime=0.3, scratches=0.2, mottle=0.2)
    build_plate(art, alu)
    if variant == "post":
        build_post_mount(alu, galv, red, bolt, cap)
    else:
        black = al.material("foot_black", FOOT_BLACK, roughness=0.8, dust=0.10, streaks=0.3, grime=0.3,
                            scratches=0.25, mottle=0.3)
        build_post_mount(alu, galv, red, bolt, cap, post_bottom=FOOT_H + 0.02)
        build_mobile_stand(black, galv, bolt)
    name = "PROP_Schild_Zeichen123" + ("" if variant == "post" else "_" + variant)
    dg = bpy.context.evaluated_depsgraph_get()
    parts = {o.name: sum(len(p.vertices) - 2 for p in o.evaluated_get(dg).data.polygons)
             for o in bpy.data.objects if o.type == 'MESH'}
    print("tris per part:", sorted(parts.items(), key=lambda kv: -kv[1]))
    obj = al.join_all(name)
    al.set_src_uv(obj, art_uv)
    return obj, art


# ---------------------------------------------------------------- bake + export with a sign-first UV layout

ART_REGION = (0.015, 0.012, 0.970)    # u0, v0, size of the sharp triangle's side in UV units


def layout_uvs(obj, art):
    """Fixed planar UV island for the sign face (pinned), everything else smart-projected and packed around it."""
    me = obj.data
    art_idx = [i for i, m in enumerate(me.materials) if m == art][0]
    bake_uv = me.uv_layers.get(al.BAKE_UV) or me.uv_layers.new(name=al.BAKE_UV)
    me.uv_layers.active = bake_uv
    mw = obj.matrix_world
    u0, v0, s = ART_REGION
    for poly in me.polygons:
        if poly.material_index != art_idx:
            continue
        for li in poly.loop_indices:
            co = mw @ me.vertices[me.loops[li].vertex_index].co
            bake_uv.data[li].uv = (u0 + (co.x + SIDE / 2) / SIDE * s, v0 + (co.z - Z0) / SIDE * s)
    return art_idx


def bake_and_export_sign(obj, art, out_dir, name, res=1024, ao_strength=0.55, samples=32, margin=16,
                         uv_margin=0.005):
    """Like asset_lib.bake_and_export (same bake, margin, empty-texel fill and export settings), but with
    layout_uvs() + pinned pack instead of a plain smart_project."""
    os.makedirs(out_dir, exist_ok=True)
    art_idx = layout_uvs(obj, art)
    al.place_bottom_centre_at_origin(obj)
    me = obj.data
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
    bpy.context.scene.tool_settings.use_uv_select_sync = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.context.scene.tool_settings.mesh_select_mode = (False, False, True)
    bm = bmesh.from_edit_mesh(me)
    uvl = bm.loops.layers.uv[al.BAKE_UV]
    for e in (*bm.verts, *bm.edges, *bm.faces):
        e.select = False
    # Post side faces: one cylindrical UV island (seam at the back), so its shading is continuous.
    post = [f for f in bm.faces if f.material_index != art_idx
            and max(v.co.z for v in f.verts) - min(v.co.z for v in f.verts) > 0.5]
    cx = sum(v.co.x for f in post for v in f.verts) / max(1, sum(len(f.verts) for f in post))
    cy = sum(v.co.y for f in post for v in f.verts) / max(1, sum(len(f.verts) for f in post))
    for f in post:
        fc = f.calc_center_median()
        a_c = math.atan2(fc.x - cx, -(fc.y - cy))            # 0 at the front, seam (±pi) at the back
        for l in f.loops:
            a = math.atan2(l.vert.co.x - cx, -(l.vert.co.y - cy))
            if a - a_c > math.pi: a -= 2 * math.pi
            if a_c - a > math.pi: a += 2 * math.pi
            l[uvl].uv = ((a + math.pi) * POST_R, l.vert.co.z)
    bm.faces.index_update()
    post_set = {f.index for f in post}
    for f in bm.faces:
        is_art = f.material_index == art_idx
        if not is_art and f.index not in post_set:
            f.select_set(True)
        for l in f.loops:
            l[uvl].pin_uv = is_art
    bmesh.update_edit_mesh(me)
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=uv_margin, correct_aspect=False)
    bm = bmesh.from_edit_mesh(me)
    uvl = bm.loops.layers.uv[al.BAKE_UV]
    # smart_project scales its islands into 0..1; bring the post strip to the same texel density (relative
    # size is what pack_islands keeps). Reference: a smart-projected face of known area.
    ref = max((f for f in bm.faces if f.select and f.index not in post_set and f.material_index != art_idx),
              key=lambda f: f.calc_area())
    uv_area = abs(sum((ref.loops[i][uvl].uv.x * ref.loops[(i + 1) % len(ref.loops)][uvl].uv.y
                       - ref.loops[(i + 1) % len(ref.loops)][uvl].uv.x * ref.loops[i][uvl].uv.y)
                      for i in range(len(ref.loops)))) / 2
    k = math.sqrt(uv_area / ref.calc_area())
    for f in bm.faces:
        if f.index in post_set:
            for l in f.loops:
                l[uvl].uv = l[uvl].uv * k
        f.select_set(True)
    bmesh.update_edit_mesh(me)
    bpy.ops.uv.pack_islands(udim_source='CLOSEST_UDIM', rotate=True, rotate_method='ANY', scale=True,
                            margin_method='SCALED', margin=uv_margin, pin=True, pin_method='LOCKED',
                            shape_method='CONCAVE')
    bm = bmesh.from_edit_mesh(me)
    for f in bm.faces:
        for l in f.loops:
            l[uvl].pin_uv = False
    bmesh.update_edit_mesh(me)
    bpy.ops.object.mode_set(mode='OBJECT')

    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = samples
    scene.cycles.device = 'CPU'

    def bake(kind):
        img = bpy.data.images.new(f"{name}_{kind}", res, res, alpha=True)   # transparent start: unbaked
        img.generated_color = (0, 0, 0, 0)                                  # texels keep alpha 0
        for slot in obj.material_slots:
            nt = slot.material.node_tree
            node = nt.nodes.new("ShaderNodeTexImage"); node.image = img; node.name = "__bake_target"
            nt.nodes.active = node
        if kind == 'DIFFUSE':
            scene.render.bake.use_pass_direct = False
            scene.render.bake.use_pass_indirect = False
            scene.render.bake.use_pass_color = True
        scene.render.bake.margin = margin
        bpy.ops.object.bake(type=kind)
        for slot in obj.material_slots:
            nt = slot.material.node_tree
            nt.nodes.remove(nt.nodes["__bake_target"])
        return img

    color = bake('DIFFUSE')
    ao = bake('AO')
    c = np.array(color.pixels[:]).reshape(-1, 4)
    a = np.array(ao.pixels[:]).reshape(-1, 4)[:, :1].copy()
    empty = c[:, 3] < 0.5                 # outside all islands (+margin): average colour, no dark mip bleeding
    if empty.any() and (~empty).any():
        c[empty, :3] = c[~empty, :3].mean(axis=0)
        a[empty] = 1.0
    c[:, :3] *= (1 - ao_strength) + ao_strength * a
    c[:, 3] = 1.0
    final = bpy.data.images.new(name, res, res)
    final.pixels[:] = c.ravel()
    png = os.path.join(out_dir, name + ".png")
    final.filepath_raw = png; final.file_format = 'PNG'
    final.save()

    for layer in [l for l in me.uv_layers if l.name != al.BAKE_UV]:
        me.uv_layers.remove(layer)
    preview = bpy.data.materials.new(name + "_baked")
    preview.use_nodes = True
    pn = preview.node_tree.nodes
    t = pn.new("ShaderNodeTexImage"); t.image = final
    preview.node_tree.links.new(t.outputs["Color"],
                                next(n for n in pn if n.type == "BSDF_PRINCIPLED").inputs["Base Color"])
    pn.active = t
    me.materials.clear(); me.materials.append(preview)

    path = os.path.join(out_dir, name + ".obj")
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
    bpy.ops.wm.obj_export(filepath=path, export_selected_objects=True, forward_axis='NEGATIVE_Z', up_axis='Y',
                          export_triangulated_mesh=True, export_normals=True, export_uv=True,
                          export_materials=False, apply_modifiers=True, global_scale=1.0)
    print(f"exported {name}: tris {al.tri_count(obj)}, dims {tuple(round(d, 4) for d in obj.dimensions)}, {path}")
    return path, png


# ---------------------------------------------------------------- close-up previews of the sign head

def render_closeups(obj, out_png, zmin, size=512):
    """Workbench renders framed on the part of the object above `zmin` (front, 3/4, side, back)."""
    vs = [obj.matrix_world @ v.co for v in obj.data.vertices if (obj.matrix_world @ v.co).z > zmin]
    lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
    hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'TEXTURE'
    scene.render.resolution_x = scene.render.resolution_y = size
    centre, radius = (lo + hi) / 2, (hi - lo).length / 2
    cam_data = bpy.data.cameras.new("__close_cam"); cam_data.lens = 50
    cam = bpy.data.objects.new("__close_cam", cam_data); scene.collection.objects.link(cam)
    scene.camera = cam
    tiles, tmp = [], out_png + ".tmp.png"
    for d in ((0, -1, 0.05), (0.75, -0.75, 0.3), (1, 0.02, 0.05), (-0.3, 1, 0.1)):
        d = Vector(d).normalized()
        cam.location = centre + d * radius * 2.9
        cam.rotation_euler = (centre - cam.location).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = tmp
        bpy.ops.render.render(write_still=True)
        img = bpy.data.images.load(tmp)
        tiles.append(np.array(img.pixels[:]).reshape(size, size, 4))
        bpy.data.images.remove(img)
    os.remove(tmp)
    sheet = np.concatenate(tiles, axis=1)
    out = bpy.data.images.new("__close_sheet", size * len(tiles), size)
    out.pixels[:] = sheet.ravel()
    out.filepath_raw = out_png; out.file_format = 'PNG'; out.save()
    bpy.data.images.remove(out)
    bpy.data.objects.remove(cam); bpy.data.cameras.remove(cam_data)
    print("closeups", out_png)


def run(variant):
    obj, art = build(variant)
    name = obj.name
    print(f"{name}: tris before export {al.tri_count(obj)}")
    bake_and_export_sign(obj, art, OUT, name)
    al.render_previews(obj, os.path.join(OUT, name + "_preview.png"))
    render_closeups(obj, os.path.join(OUT, name + "_closeup.png"), zmin=Z0 - 0.08 if variant == "post" else 0.0)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    which = argv[0] if argv else "post"
    for v in (("post", "mobil") if which == "all" else (which,)):
        if "dry" in argv:                                    # geometry + triangle count only, no bake
            o, _ = build(v); print(f"DRY {o.name}: tris {al.tri_count(o)}, dims {tuple(round(d, 4) for d in o.dimensions)}")
        else:
            run(v)
