# Spike v3: German 120 L wheelie bin (Mülltonne) built from photo references (Wikimedia Commons:
# Berlin BSR Biotonne, Heidelberg "Mülltonnen diverse", Haan bin row, Duisburg bins with orange lids).
# One geometry, four colour variants; each variant is baked to one PNG (colour × AO) and exported as OBJ.
#
# Blender Z-up while modelling. Front of the bin faces -Y (ends up facing the runner camera, +Z in the engine).
#
# Usage inside Blender (MCP):  exec(open(PATH).read()); build("restmuell"); bake_and_export("restmuell")
import bpy, bmesh, os, math
import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "mull")

# Colours are linear RGB (Blender shader space), derived from RAL references.
ANTHRACITE = (0.030, 0.034, 0.038)   # RAL 7021-ish
BROWN = (0.075, 0.040, 0.018)        # RAL 8014-ish
BLUE = (0.012, 0.13, 0.40)           # RAL 5015-ish
YELLOW = (0.95, 0.55, 0.01)          # RAL 1023-ish (warm traffic yellow)

VARIANTS = {
    "restmuell": dict(body=ANTHRACITE, lid=ANTHRACITE, label="Restmüll", label_bg=(0.10, 0.13, 0.18), label_fg=(0.95, 0.95, 0.95), number="12"),
    "bio":       dict(body=BROWN, lid=BROWN, label="Bioabfälle", label_bg=(0.75, 0.75, 0.73), label_fg=(0.12, 0.03, 0.02), number="12"),
    "papier":    dict(body=ANTHRACITE, lid=BLUE, label="Papier", label_bg=(0.05, 0.2, 0.6), label_fg=(0.95, 0.95, 0.95), number="7"),
    "gelb":      dict(body=ANTHRACITE, lid=YELLOW, label="Gelbe Tonne", label_bg=(0.85, 0.55, 0.0), label_fg=(0.01, 0.01, 0.01), number="3"),
}

# Dimensions (metres) of a 120 L bin: ~0.93 m high overall, 0.48 m wide, 0.55 m deep.
W, D, H = 0.46, 0.50, 0.80     # body at the top (below the rim)
TAPER = 0.84                   # bottom of the body is 84 % of the top
Z0 = 0.03                      # body starts slightly above the ground (wheels/foot carry it)
RIM_H = 0.075
RIM_OUT = 0.035                # rim overhang beyond the body on each side
WHEEL_R = 0.1


# ---------------------------------------------------------------- materials

def material(name, color, roughness=0.6, dust=0.35, streaks=0.5, grime=0.6, scratches=0.4, mottle=0.2):
    """Weathered plastic: mottled base, lighter scratches/worn edges, dust on upward faces,
    vertical rain streaks, grime near the ground and in crevices. Baked later, so only Base Color matters."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    bsdf = next(n for n in N if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Roughness"].default_value = roughness
    coord = N.new("ShaderNodeTexCoord")
    geo = N.new("ShaderNodeNewGeometry")

    def mix(a, b, fac):
        n = N.new("ShaderNodeMix"); n.data_type = 'RGBA'; n.clamp_factor = True
        for sock, val in ((n.inputs[6], a), (n.inputs[7], b)):
            if isinstance(val, tuple): sock.default_value = (*val, 1)
            else: L.new(val, sock)
        if isinstance(fac, float): n.inputs[0].default_value = fac
        else: L.new(fac, n.inputs[0])
        return n.outputs[2]

    def math_node(op, a, b=None, clamp=True):
        n = N.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
        for sock, val in ((n.inputs[0], a), (n.inputs[1], b)):
            if val is None: continue
            if isinstance(val, (int, float)): sock.default_value = val
            else: L.new(val, sock)
        return n.outputs[0]

    def noise(scale, detail=6, vec=None, stretch=None):
        t = N.new("ShaderNodeTexNoise"); t.inputs["Scale"].default_value = scale; t.inputs["Detail"].default_value = detail
        src = coord.outputs["Object"]
        if stretch:
            mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = stretch
            L.new(src, mp.inputs["Vector"]); src = mp.outputs["Vector"]
        L.new(src, t.inputs["Vector"])
        return t.outputs["Fac"]

    def ramp(fac, a, b):
        # Blender does not re-sort stops: a falling ramp (a > b) needs ascending stops, swapped colours.
        r = N.new("ShaderNodeValToRGB")
        e0, e1 = r.color_ramp.elements
        if a <= b:
            e0.position, e1.position = a, b
        else:
            e0.position, e1.position = b, a
            e0.color, e1.color = (1, 1, 1, 1), (0, 0, 0, 1)
        L.new(fac, r.inputs["Fac"])
        return r.outputs["Color"]

    # Mottled base.
    col = mix(tuple(c * (1 - mottle) for c in color), tuple(c * (1 + mottle) for c in color), noise(70))

    # Scratches / worn edges: fine stretched noise + convex edges, lighter and greyer.
    if scratches > 0:
        scr = ramp(noise(160, 2, stretch=(1, 1, 18)), 0.62, 0.66)
        edges = ramp(geo.outputs["Pointiness"], 0.52, 0.58)
        wear = math_node('MULTIPLY', math_node('ADD', scr, edges), scratches)
        col = mix(col, tuple(min(1.0, c * 2.5 + 0.06) for c in color), wear)

    # Dust on faces pointing up, plus a thin overall film.
    if dust > 0:
        sep = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], sep.inputs["Vector"])
        up = math_node('MULTIPLY', ramp(sep.outputs["Z"], 0.3, 0.9), noise(12))
        film = math_node('ADD', math_node('MULTIPLY', up, 1.4), 0.12)
        col = mix(col, (0.20, 0.19, 0.17), math_node('MULTIPLY', film, dust))

    # Rain streaks and grime near the ground and in crevices (AO).
    if grime > 0:
        streak = ramp(noise(5, 4, stretch=(16, 16, 0.9)), 0.55, 0.8)
        sepp = N.new("ShaderNodeSeparateXYZ"); L.new(coord.outputs["Object"], sepp.inputs["Vector"])
        ground = ramp(sepp.outputs["Z"], 0.25, 0.0)   # 1 at the bottom, 0 above 25 cm
        ao = N.new("ShaderNodeAmbientOcclusion"); ao.samples = 16; ao.inputs["Distance"].default_value = 0.05
        crev = math_node('SUBTRACT', 1.0, ao.outputs["AO"])
        g = math_node('ADD', math_node('ADD', math_node('MULTIPLY', streak, streaks), ground), crev)
        col = mix(col, (0.035, 0.03, 0.022), math_node('MULTIPLY', g, grime))

    L.new(col, bsdf.inputs["Base Color"])
    return m


def flat(name, color, roughness=0.5):
    """Printed sticker / paint: mostly clean, a bit of dirt."""
    return material(name, color, roughness, dust=0.15, streaks=0.3, grime=0.25, scratches=0.15, mottle=0.04)


# ---------------------------------------------------------------- geometry helpers

def add_bevel(o, width, segments=3, angle=40):
    mod = o.modifiers.new("Bevel", 'BEVEL')
    mod.width = width; mod.segments = segments
    mod.limit_method = 'ANGLE'; mod.angle_limit = math.radians(angle)
    mod.harden_normals = False
    return o


def box(name, size, loc, mat, bevel=0.008, segments=2):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object; o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel: add_bevel(o, bevel, segments)
    return o


def cyl_x(name, r, length, loc, mat, verts=24, bevel=0.004):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=length, location=loc, rotation=(0, math.radians(90), 0))
    o = bpy.context.active_object; o.name = name
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    o.data.materials.append(mat)
    if bevel: add_bevel(o, bevel, 2)
    return o


def taper_t(z):
    return (z - Z0) / H


def front_y(z):
    return -(D / 2) * (TAPER + (1 - TAPER) * taper_t(z))


def side_x(z):
    return (W / 2) * (TAPER + (1 - TAPER) * taper_t(z))


FRONT_TILT = math.atan((1 - TAPER) * (D / 2) / H)   # front face leans forward (outwards) towards the top
SIDE_TILT = math.atan((1 - TAPER) * (W / 2) / H)


def text(name, body, loc, size, mat, extrude=0.0008):
    """Text lying on the front face (-Y), tilted like the tapered front."""
    bpy.ops.object.text_add(location=loc, rotation=(math.radians(90) + FRONT_TILT, 0, 0))
    t = bpy.context.active_object; t.name = name
    t.data.body = body
    t.data.align_x = 'CENTER'; t.data.align_y = 'CENTER'
    t.data.size = size; t.data.extrude = extrude
    t.data.materials.append(mat)
    return t


# ---------------------------------------------------------------- build

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.curves):
        for b in list(coll):
            if b.users == 0: coll.remove(b)


def build(variant):
    v = VARIANTS[variant]
    clear_scene()
    bright = max(v["body"]) > 0.5          # light plastics show dust as grey haze: keep it subtle
    BODY = material("body", v["body"], dust=0.12 if bright else 0.35, grime=0.35 if bright else 0.6)
    LID = material("lid", v["lid"], roughness=0.55, dust=0.12 if max(v["lid"]) > 0.5 else 0.35)
    RUBBER = material("rubber", (0.012, 0.012, 0.012), 0.9, dust=0.2, scratches=0.2, mottle=0.3)
    STEEL = material("steel", (0.25, 0.25, 0.26), 0.5, dust=0.2, scratches=0.3)
    LABEL_BG = flat("label_bg", v["label_bg"])
    LABEL_FG = flat("label_fg", v["label_fg"])
    WHITE = flat("white", (0.8, 0.8, 0.78))
    BLACK = flat("black", (0.01, 0.01, 0.01))
    SERVICE = flat("service_yellow", (0.85, 0.6, 0.0))

    top = Z0 + H

    # Body: tapered box with big rounded vertical edges.
    body = box("body", (W, D, H), (0, 0, Z0 + H / 2), BODY, bevel=0)
    bm = bmesh.new(); bm.from_mesh(body.data)
    for vert in bm.verts:
        if vert.co.z < 0:
            vert.co.x *= TAPER; vert.co.y *= TAPER
    bm.to_mesh(body.data); bm.free()
    add_bevel(body, 0.045, 4, 30)

    # Rim: wide collar overhanging the body, with reinforcing fins underneath on the sides and front.
    rim = box("rim", (W + 2 * RIM_OUT, D + 2 * RIM_OUT, RIM_H), (0, 0, top + RIM_H / 2 - 0.01), BODY, 0.012, 3)
    for side in (-1, 1):
        for fy in (-0.17, 0.0, 0.17):
            f = box(f"fin_side_{side}_{fy}", (RIM_OUT, 0.012, 0.09), (side * (W / 2 + RIM_OUT / 2 - 0.004), fy, top - 0.04), BODY, 0.003)
            f.rotation_euler.y = side * SIDE_TILT
    for fx in (-0.15, 0.15):
        f = box(f"fin_front_{fx}", (0.012, RIM_OUT, 0.09), (fx, -(D / 2 + RIM_OUT / 2 - 0.004), top - 0.04), BODY, 0.003)

    # Lid: slightly larger than the rim at the front (grip lip), raised centre panel, hinge at the back.
    lid_z = top + RIM_H - 0.01
    lid = box("lid", (W + 2 * RIM_OUT + 0.01, D + 2 * RIM_OUT + 0.03, 0.035), (0, -0.015, lid_z + 0.0175), LID, 0.01, 3)
    panel = box("lid_panel", (W - 0.04, D - 0.06, 0.018), (0, -0.01, lid_z + 0.035 + 0.009 - 0.004), LID, 0.008, 3)
    lip = box("lid_lip", (W * 0.55, 0.035, 0.04), (0, -(D / 2 + RIM_OUT + 0.03), lid_z + 0.005), LID, 0.008)
    for side in (-1, 1):
        cyl_x(f"hinge_{side}", 0.02, 0.09, (side * (W / 2 - 0.02), D / 2 + RIM_OUT + 0.01, lid_z), BODY)

    # Handle bar at the back between two arms coming out of the rim.
    hy = D / 2 + RIM_OUT + 0.055
    cyl_x("handle", 0.017, W * 0.75, (0, hy, top - 0.005), BODY, 20)
    for side in (-1, 1):
        box(f"handle_arm_{side}", (0.035, 0.07, 0.04), (side * W * 0.37, hy - 0.03, top - 0.005), BODY, 0.008)

    # Wheels on a steel axle at the back bottom, with mounting blocks.
    wy = D / 2 * TAPER + 0.02
    cyl_x("axle", 0.011, W * TAPER + 0.14, (0, wy, WHEEL_R), STEEL, 12)
    for side in (-1, 1):
        x = side * (W / 2 * TAPER + 0.045)
        cyl_x(f"tyre_{side}", WHEEL_R, 0.055, (x, wy, WHEEL_R), RUBBER, 32, 0.01)
        cyl_x(f"hub_{side}", WHEEL_R * 0.5, 0.06, (x, wy, WHEEL_R), BODY, 20, 0.004)
        box(f"wheel_block_{side}", (0.06, 0.1, 0.16), (side * (W / 2 * TAPER - 0.01), wy - 0.03, WHEEL_R + 0.03), BODY, 0.012)
    # Front foot so it stands level.
    box("foot", (W * 0.6, 0.06, 0.06), (0, front_y(0.05) + 0.04, 0.03), BODY, 0.01)

    # Front decals (positions on the tapered front face).
    def decal(name, size, z, mat, x=0.0, depth=0.002):
        o = box(name, (size[0], depth, size[1]), (x, front_y(z) - depth / 2 - 0.001, z), mat, 0)
        o.rotation_euler.x = FRONT_TILT
        return o

    zl = Z0 + H * 0.78
    decal("label", (0.26, 0.07), zl, LABEL_BG)
    t = text("label_text", v["label"], (0, front_y(zl) - 0.0035, zl), 0.042, LABEL_FG)
    zb = Z0 + H * 0.9
    decal("barcode_bg", (0.07, 0.035), zb, WHITE, x=-0.13)
    for i in range(9):
        decal(f"bar_{i}", (0.002 + 0.002 * (i % 3), 0.026), zb, BLACK, x=-0.155 + i * 0.0055, depth=0.003)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.022, depth=0.002,
                                        location=(0.1, front_y(zb) - 0.002, zb), rotation=(math.radians(90) + FRONT_TILT, 0, 0))
    s = bpy.context.active_object; s.name = "service_sticker"; s.data.materials.append(SERVICE)
    zn = Z0 + H * 0.45
    text("house_number", v["number"], (0, front_y(zn) - 0.0015, zn), 0.11, WHITE, extrude=0.0005)

    print("built", variant)


def finish_mesh(name):
    """Join everything into one mesh object, smooth by angle, one UV map."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = bpy.data.objects["body"]
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.join()
    obj = bpy.context.active_object; obj.name = name
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.006)
    bpy.ops.object.mode_set(mode='OBJECT')
    return obj


def bake_and_export(variant, res=1024):
    name = f"PROP_WheelieBin_120L_{variant}"
    obj = finish_mesh(name)
    scene = bpy.context.scene
    try:
        scene.render.engine = 'CYCLES'
    except TypeError as e:
        print("engine error", e)
    scene.cycles.samples = 32
    scene.cycles.device = 'CPU'

    def bake(kind, img_name):
        img = bpy.data.images.new(img_name, res, res)
        for slot in obj.material_slots:
            nt = slot.material.node_tree
            node = nt.nodes.new("ShaderNodeTexImage"); node.image = img; nt.nodes.active = node
        if kind == 'DIFFUSE':
            scene.render.bake.use_pass_direct = False
            scene.render.bake.use_pass_indirect = False
            scene.render.bake.use_pass_color = True
        scene.render.bake.margin = 6
        bpy.ops.object.bake(type=kind)
        for slot in obj.material_slots:
            nt = slot.material.node_tree
            for n in [n for n in nt.nodes if n.type == 'TEX_IMAGE' and n.image == img]:
                nt.nodes.remove(n)
        return img

    color = bake('DIFFUSE', name + "_color")
    ao = bake('AO', name + "_ao")
    c = np.array(color.pixels[:]).reshape(-1, 4)
    a = np.array(ao.pixels[:]).reshape(-1, 4)[:, :1]
    c[:, :3] *= 0.45 + 0.55 * a
    c[:, 3] = 1.0
    final = bpy.data.images.new(name, res, res)
    final.pixels[:] = c.ravel()
    final.filepath_raw = os.path.join(OUT, name + ".png"); final.file_format = 'PNG'
    final.save()

    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
    bpy.ops.wm.obj_export(filepath=os.path.join(OUT, name + ".obj"), export_selected_objects=True,
                          forward_axis='NEGATIVE_Z', up_axis='Y', export_triangulated_mesh=True,
                          export_normals=True, export_uv=True, export_materials=False,
                          apply_modifiers=True, global_scale=1.0)
    tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
    print("exported", name, "tris", tris, "dims", tuple(round(d, 3) for d in obj.dimensions))
