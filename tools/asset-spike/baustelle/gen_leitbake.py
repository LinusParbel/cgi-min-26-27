# German Leitbake (StVO Zeichen 605-10 / 605-20, 1000 x 250 mm) on a mobile rubber Fussplatte.
# Main reference: ref/baustelle/03.jpg (board with light-grey rounded frame, V-shaped bracket, short black
# post, black recycled-rubber foot plate with handle pockets); also 04.jpg, 02.jpg, 18.jpg.
# Artwork: ref/signs/z605.png (official Zeichen 605-10, "Aufstellung rechts"), mapped 1:1 onto the board
# (the full 1000 x 250 sign = the full board outline; the frame lip covers its outer ~17 mm, as on the
# real board). Variant "links" uses the horizontally mirrored artwork; geometry is identical.
#
# Blender Z-up, 1 unit = 1 m, front (sign face) towards -Y. The warning lamp is a separate asset; its
# mounting point (centre of the board's top edge) is written to mounts.json.
#
# Usage (headless):
#   blender --background --factory-startup --python gen_leitbake.py [-- rechts links]
# Comparison sheet (plain Python with Pillow, after the SpikeViewer screenshots exist):
#   python gen_leitbake.py compare
import sys, os, math, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # tools/asset-spike
OUT = os.path.join(ROOT, "out", "baustelle", "leitbake")
WORK = os.path.join(OUT, "work")
ART = os.path.join(ROOT, "ref", "signs", "z605.png")

# ---------------------------------------------------------------- dimensions (metres)
BW, BH, BT = 0.25, 1.00, 0.022     # board width, height, thickness (blow-moulded plastic board)
BOARD_Z0 = 0.21                    # board bottom edge above ground (photo: ~0.2 m)
CORNER_R = 0.025                   # outer corner radius of the board outline
FRAME = 0.017                      # width of the light-grey frame lip around the sign face
RECESS = 0.005                     # sign face sits this much behind the frame lip

# Foot plate. NOTE: measured in 03.jpg the plate is ~1.6-1.7x the board width long (~0.40-0.45 m) and
# ~0.30-0.37 m deep, i.e. much shorter than the 0.75-0.8 m in the task text; we follow the photo.
PL, PD, PH = 0.42, 0.34, 0.095     # length (X, along the board width), depth (Y), height (Z)
SKIRT = 0.03                       # vertical skirt height before the chamfered slope starts
SLOPE_X, SLOPE_Y = 0.025, 0.045    # horizontal inset of the top face at the ends / front+back

V_TOP_HW, V_BOT_HW = 0.112, 0.022  # V bracket half widths (top under the board, bottom at the sleeve)
V_Z0 = 0.148                       # V bracket bottom
V_T = 0.028                        # V bracket thickness
POST_R = 0.02                      # 40 mm post

# ---------------------------------------------------------------- colours (linear RGB)
FRAME_COL = (0.62, 0.63, 0.62)     # light-grey/white plastic
BACK_COL = (0.55, 0.56, 0.55)      # back side: same plastic, a bit dirtier
RUBBER_COL = (0.022, 0.022, 0.024) # recycled rubber foot plate (black, dusty)
POST_COL = (0.018, 0.018, 0.019)
STEEL_COL = (0.16, 0.16, 0.17)
FRAME_SRGB = (0.82, 0.82, 0.81)    # same frame colour, sRGB-encoded, for compositing the artwork


# ================================================================ Blender part
def _blender_main(variants):
    import bpy, bmesh
    import numpy as np
    from mathutils import Vector
    sys.path.insert(0, ROOT)
    import asset_lib as al

    os.makedirs(WORK, exist_ok=True)

    # ------------------------------------------------------------ artwork preparation
    def prep_artwork(variant):
        """Official z605 PNG -> transparent corners/black outline composited onto the frame colour (all of
        it lies under the frame lip anyway), small blue owner sticker added (as in 03.jpg, top left),
        mirrored for 'links', resampled to a SQUARE 2048x2048 image.
        Why square: bake_and_export's smart_project uses UV aspect correction, which picks up the active
        texture node's image aspect (1:4 here) and squeezes the whole bake layout into a strip. The 'src'
        UVs are 0..1 over the board, so the physical 1:1 mapping does not depend on the pixel aspect."""
        dst = os.path.join(WORK, f"z605_{variant}.png")
        img = bpy.data.images.load(ART)
        w, h = img.size
        px = np.empty(w * h * 4, dtype=np.float32)
        img.pixels.foreach_get(px)
        px = px.reshape(h, w, 4)                    # rows bottom-up, sRGB-encoded bytes / 255
        bpy.data.images.remove(img)
        a = px[..., 3:4]
        px[..., :3] = px[..., :3] * a + np.array(FRAME_SRGB, dtype=np.float32) * (1 - a)
        px[..., 3] = 1.0

        # Sticker: blue disc (~29 mm) with white rim and a white arrow pointing down-left.
        ppm = w / BW
        cx, cy = (-0.083 + BW / 2) * ppm, (1.0 - 0.047 / BH) * h
        r = 0.0145 * ppm
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        dx, dy = xx - cx, yy - cy
        dist = np.sqrt(dx * dx + dy * dy)
        px[dist < r] = (0.92, 0.92, 0.92, 1)
        px[dist < r * 0.86] = (0.0, 0.22, 0.58, 1)
        t = (-dx - dy) / math.sqrt(2)          # along the arrow (towards down-left)
        s = (-dx + dy) / math.sqrt(2)          # across the arrow
        shaft = (t > -0.55 * r) & (t < 0.15 * r) & (np.abs(s) < 0.12 * r)
        head = (t >= 0.05 * r) & (t < 0.62 * r) & (np.abs(s) < (0.62 * r - t) * 0.95)
        px[(shaft | head) & (dist < r * 0.86)] = (0.95, 0.95, 0.95, 1)

        if variant == "links":
            px = px[:, ::-1].copy()
        out = bpy.data.images.new(f"z605_{variant}_prep", w, h)
        out.pixels.foreach_set(np.ascontiguousarray(px, dtype=np.float32).ravel())
        out.scale(2048, 2048)
        out.filepath_raw = dst; out.file_format = 'PNG'; out.save()
        bpy.data.images.remove(out)
        return dst

    # ------------------------------------------------------------ geometry helpers
    def rounded_rect(w, h, r, seg):
        """2D rounded rectangle outline, CCW, as (a, b) tuples."""
        pts = []
        corners = [(w / 2 - r, -h / 2 + r, -90), (w / 2 - r, h / 2 - r, 0),
                   (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180)]
        for ca, cb, a0 in corners:
            for i in range(seg + 1):
                ang = math.radians(a0 + 90 * i / seg)
                pts.append((ca + r * math.cos(ang), cb + r * math.sin(ang)))
        return pts

    def mesh_object(name, bm, mats):
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(o)
        for m in mats:
            me.materials.append(m)
        return o

    def front_face(bm):
        for f in bm.faces:
            f.normal_update()
        return min(bm.faces, key=lambda f: f.normal.y)

    def back_face(bm):
        return max(bm.faces, key=lambda f: f.normal.y)

    def extruded_xz(bm, outline, y0, y1):
        """Prism from an XZ outline (CCW seen from -Y) between y0 (front) and y1 (back)."""
        fv = [bm.verts.new((x, y0, z)) for x, z in outline]
        bv = [bm.verts.new((x, y1, z)) for x, z in outline]
        n = len(outline)
        bm.faces.new(fv)
        bm.faces.new(list(reversed(bv)))
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((fv[i], bv[i], bv[j], fv[j]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

    def inset_front(bm, width, depth):
        """Inset the -Y face by `width` and push the inner face back by `depth` -> raised frame lip."""
        f = front_face(bm)
        bmesh.ops.inset_region(bm, faces=[f], thickness=width, depth=0.0, use_even_offset=True)
        for v in f.verts:
            v.co.y += depth
        return f

    def apply_modifiers(o):
        bpy.ops.object.select_all(action='DESELECT')
        o.select_set(True); bpy.context.view_layer.objects.active = o
        for m in list(o.modifiers):
            bpy.ops.object.modifier_apply(modifier=m.name)

    def boolean_cut(target, cutters):
        bpy.ops.object.select_all(action='DESELECT')
        for c in cutters:
            c.select_set(True)
        bpy.context.view_layer.objects.active = cutters[0]
        if len(cutters) > 1:
            bpy.ops.object.join()
        cutter = bpy.context.active_object
        mod = target.modifiers.new("cut", 'BOOLEAN')
        mod.operation = 'DIFFERENCE'; mod.object = cutter
        try:
            mod.solver = 'EXACT'
        except TypeError:
            pass
        apply_modifiers(target)
        bpy.data.objects.remove(cutter)

    # ------------------------------------------------------------ build
    def build(variant):
        al.clear_scene()
        art = prep_artwork(variant)
        FRAME_M = al.material("frame_plastic", FRAME_COL, 0.45, dust=0.12, streaks=0.4, grime=0.3,
                              scratches=0.25, mottle=0.06)
        BACK_M = al.material("back_plastic", BACK_COL, 0.5, dust=0.18, streaks=0.7, grime=0.45,
                             scratches=0.3, mottle=0.1)
        SIGN_M = al.flat("sign_sheeting", (0.8, 0.8, 0.8), 0.35, image=art)
        RUBBER = al.material("rubber", RUBBER_COL, 0.9, dust=0.32, streaks=0.3, grime=0.5,
                             scratches=0.2, mottle=0.3)
        LABEL = al.material("rubber_label", RUBBER_COL, 0.9, dust=0.2, streaks=0.3, grime=0.5,
                            scratches=0.08, mottle=0.3)
        POST_M = al.material("post", POST_COL, 0.4, dust=0.25, scratches=0.35, mottle=0.2)
        STEEL = al.material("steel", STEEL_COL, 0.4, dust=0.15, scratches=0.3, mottle=0.2)

        # --- board: rounded-rectangle slab, raised frame lip on the front, sign face recessed
        bm = bmesh.new()
        outline = [(x, z + BOARD_Z0 + BH / 2) for x, z in rounded_rect(BW, BH, CORNER_R, 4)]
        extruded_xz(bm, outline, -BT / 2, BT / 2)
        sign = inset_front(bm, FRAME, RECESS)
        sign.material_index = 1
        back_face(bm).material_index = 2
        board = mesh_object("board", bm, [FRAME_M, SIGN_M, BACK_M])
        al.add_bevel(board, 0.004, 3, 40)

        # --- V-shaped bracket under the board (light-grey plastic, recessed front panel, two bolts)
        bm = bmesh.new()
        vz1 = BOARD_Z0 + 0.003
        extruded_xz(bm, [(-V_BOT_HW, V_Z0), (V_BOT_HW, V_Z0), (V_TOP_HW, vz1), (-V_TOP_HW, vz1)],
                    -V_T / 2, V_T / 2)
        inset_front(bm, 0.008, 0.002)
        vb = mesh_object("v_bracket", bm, [FRAME_M])
        al.add_bevel(vb, 0.003, 2, 40)
        for i, z in enumerate((0.195, 0.169)):
            al.cyl(f"bolt_{i}", 0.0065, 0.006, (0, -V_T / 2 - 0.0005, z), STEEL, axis='Y', verts=10,
                   bevel=0.0015, segments=1)
        al.cyl("sleeve", 0.0225, 0.02, (0, 0, 0.147), POST_M, verts=16, bevel=0.003)   # black joint (03.jpg)

        # --- post plugged into the foot plate socket
        p0, p1 = PH - 0.004, 0.152
        al.cyl("post", POST_R, p1 - p0, (0, 0, (p0 + p1) / 2), POST_M, verts=16, bevel=0.002)
        al.cyl("collar", 0.042, 0.016, (0, 0, PH + 0.004), RUBBER, verts=24, bevel=0.004)

        # --- foot plate: skirt + chamfered slopes to a flat top
        bm = bmesh.new()
        rings = [[(x, y, 0.0) for x, y in rounded_rect(PL, PD, 0.03, 3)],
                 [(x, y, SKIRT) for x, y in rounded_rect(PL, PD, 0.03, 3)],
                 [(x, y, PH) for x, y in rounded_rect(PL - 2 * SLOPE_X, PD - 2 * SLOPE_Y, 0.02, 3)]]
        vs = [[bm.verts.new(p) for p in ring] for ring in rings]
        n = len(rings[0])
        for a, b in zip(vs, vs[1:]):
            for i in range(n):
                j = (i + 1) % n
                bm.faces.new((a[i], a[j], b[j], b[i]))
        bm.faces.new(vs[-1])                     # top (winding above is already outward-facing)
        plate = mesh_object("plate", bm, [RUBBER])
        # Bevel while the bottom is still OPEN: boundary edges are not bevelled, so the skirt runs straight
        # down to z=0 and the plate sits flat on the ground. 32 deg skips the 30 deg corner steps.
        al.add_bevel(plate, 0.006, 2, 32)
        apply_modifiers(plate)
        bm = bmesh.new(); bm.from_mesh(plate.data)   # close the bottom for the boolean (removed below)
        bmesh.ops.holes_fill(bm, edges=bm.edges[:], sides=0)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.to_mesh(plate.data); bm.free()
        cutters = []
        for sx in (-1, 1):   # hand-grip notches, open to the top and to the plate ends (as in 03.jpg)
            cutters.append(al.box(f"cut_handle_{sx}", (0.2, 0.14, 0.2), (sx * (PL / 2 - 0.005), 0, 0.04 + 0.1), RUBBER,
                                  bevel=0))
        for i, (x, y, sx_, sy_) in enumerate(((0, 0.072, 0.06, 0.024), (0, -0.072, 0.07, 0.028),
                                              (-0.072, 0, 0.024, 0.05), (0.072, 0, 0.024, 0.05))):
            cutters.append(al.box(f"cut_small_{i}", (sx_, sy_, 0.04), (x, y, PH), RUBBER, bevel=0))
        boolean_cut(plate, cutters)
        # drop the bottom face: it sits on the ground and is never seen (saves texture space)
        bm = bmesh.new(); bm.from_mesh(plate.data)
        for f in bm.faces:
            f.normal_update()
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.normal.z < -0.9
                                   and all(v.co.z < 0.001 for v in f.verts)], context='FACES')
        bm.to_mesh(plate.data); bm.free()
        for sx in (-1, 1):   # round grip bars spanning the handle notches at the plate ends
            al.cyl(f"grip_{sx}", 0.014, 0.141, (sx * (PL / 2 - SLOPE_X - 0.004), 0, PH - 0.03), RUBBER,
                   axis='Y', verts=12, bevel=0.002, segments=1)
        # raised label panel on the front slope (embossed maker text in reality)
        dy, dz = SLOPE_Y, PH - SKIRT
        ang = math.atan2(dz, dy)      # rotates the panel's local +Z onto the slope normal
        ln = math.hypot(dy, dz)
        nrm = Vector((0, -dz / ln, dy / ln))
        mid = Vector((0, -PD / 2 + dy / 2, SKIRT + dz / 2)) + nrm * 0.001
        lab = al.box("label_panel", (0.26, ln * 0.75, 0.004), tuple(mid), LABEL, bevel=0.0015, segments=1)
        lab.rotation_euler.x = ang

        obj = al.join_all(f"PROP_Leitbake_{variant}")
        for i in reversed(range(len(obj.material_slots))):     # safety: no empty slots for the baker
            if obj.material_slots[i].material is None:
                obj.active_material_index = i
                bpy.ops.object.material_slot_remove()
        print("material slots:", [s.material.name for s in obj.material_slots])
        al.set_src_uv(obj, lambda co, nrm_: ((co.x + BW / 2) / BW, (co.z - BOARD_Z0) / BH))
        return obj

    # ------------------------------------------------------------ previews
    def render_closeup(obj, target, direction, dist, out_png, size=512, lens=50):
        scene = bpy.context.scene
        cam_data = bpy.data.cameras.new("__close_cam"); cam_data.lens = lens
        cam = bpy.data.objects.new("__close_cam", cam_data); scene.collection.objects.link(cam)
        scene.camera = cam
        d = Vector(direction).normalized()
        cam.location = Vector(target) + d * dist
        cam.rotation_euler = (Vector(target) - cam.location).to_track_quat('-Z', 'Y').to_euler()
        scene.render.engine = 'BLENDER_WORKBENCH'
        scene.display.shading.light = 'STUDIO'
        scene.display.shading.color_type = 'TEXTURE'
        scene.render.resolution_x = scene.render.resolution_y = size
        scene.render.filepath = out_png
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(cam); bpy.data.cameras.remove(cam_data)

    mount = {"x": 0.0, "y": 0.0, "z": round(BOARD_Z0 + BH, 4)}
    for variant in variants:
        name = f"PROP_Leitbake_{variant}"
        obj = build(variant)
        pivot = al.place_bottom_centre_at_origin(obj)
        mount = {"x": round(0.0 - pivot.x, 4), "y": round(0.0 - pivot.y, 4),
                 "z": round(BOARD_Z0 + BH - pivot.z, 4)}
        al.bake_and_export(obj, OUT, name, res=1024)
        print(f"STATS {name}: tris {al.tri_count(obj)}, dims {tuple(round(d, 3) for d in obj.dimensions)}, "
              f"pivot {tuple(round(p, 4) for p in pivot)}")
        al.render_previews(obj, os.path.join(OUT, name + "_preview.png"))
        render_closeup(obj, (0, 0, 0.12), (0.55, -1, 0.75), 1.2, os.path.join(OUT, name + "_closeup_foot.png"))
        render_closeup(obj, (0, 0, 1.05), (0.35, -1, 0.25), 0.9, os.path.join(OUT, name + "_closeup_top.png"))
        # mount check: a small marker disc at the lamp mounting point
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.03, depth=0.01,
                                            location=(mount["x"], mount["y"], mount["z"] + 0.005))
        marker = bpy.context.active_object
        mm = bpy.data.materials.new("marker"); mm.diffuse_color = (1, 0, 1, 1)
        marker.data.materials.append(mm)
        al.render_previews(obj, os.path.join(OUT, name + "_mountcheck.png"), views=("front", "side"),
                           extra_objects=(marker,))
        bpy.data.objects.remove(marker)

    with open(os.path.join(OUT, "mounts.json"), "w") as f:
        json.dump({"mounts": [mount]}, f, indent=2)
    print("mounts", mount)


# ================================================================ comparison sheet (plain Python)
def _compare():
    """Reference photo + engine screenshots (top row) and Blender previews (bottom row)."""
    from PIL import Image, ImageDraw
    H = 600
    def fit(im, h):
        return im.resize((max(1, int(im.width * h / im.height)), h), Image.LANCZOS)
    for variant in ("rechts", "links"):
        top = [fit(Image.open(os.path.join(ROOT, "ref", "baustelle", "03.jpg")).convert("RGB"), H)]
        for a in (0, 30, 160):
            p = os.path.join(OUT, f"engine_{variant}_{a}.png")
            if os.path.exists(p):
                top.append(fit(Image.open(p).convert("RGB"), H))
        w = sum(t.width for t in top)
        prev = Image.open(os.path.join(OUT, f"PROP_Leitbake_{variant}_preview.png")).convert("RGB")
        prev = prev.resize((w, int(prev.height * w / prev.width)), Image.LANCZOS)
        sheet = Image.new("RGB", (w, H + prev.height), (40, 40, 40))
        x = 0
        for t in top:
            sheet.paste(t, (x, 0)); x += t.width
        sheet.paste(prev, (0, H))
        ImageDraw.Draw(sheet).text((8, 8), f"03.jpg (reference) | engine 0 / 30 / 160 deg | Blender previews  [{variant}]",
                                   fill=(255, 255, 0))
        out = os.path.join(OUT, f"PROP_Leitbake_{variant}_comparison.png")
        sheet.save(out); print("saved", out)


if __name__ == "__main__":
    if "compare" in sys.argv:
        _compare()
    else:
        argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
        _blender_main(argv or ["rechts", "links"])
