"""Shared helpers for scripted Hannover Rush Hour props (run inside Blender 5.2, headless or via MCP).

Conventions (see also tools/asset-spike/baustelle/BRIEF.md):
- Blender is Z-up, 1 unit = 1 m. The FRONT of a prop faces -Y (it ends up facing the runner camera).
- Final asset = ONE mesh object with ONE baked base-colour texture (colour x AO) -> OBJ + PNG.
- Origin at the bottom centre, object at the world origin before export.

Typical use in a generator script:
    import sys; sys.path.insert(0, r"...\\tools\\asset-spike"); import asset_lib as al
    al.clear_scene()
    RED = al.material("red", (0.5, 0.02, 0.02))
    al.box("board", (1.0, 0.02, 0.25), (0, 0, 0.6), RED)
    obj = al.join_all("PROP_Example")
    al.bake_and_export(obj, out_dir, "PROP_Example", res=1024)
    al.render_previews(obj, out_dir + "/PROP_Example_preview.png")
"""
import bpy, bmesh, os, math
import numpy as np
from mathutils import Vector

SRC_UV = "src"     # UV layer that image-based materials read from
BAKE_UV = "bake"   # UV layer the final texture is baked into (the only one exported)


# ---------------------------------------------------------------- scene

def clear_scene():
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.curves,
                 bpy.data.cameras, bpy.data.lights):
        for b in list(coll):
            if b.users == 0:
                coll.remove(b)


# ---------------------------------------------------------------- materials

def material(name, color, roughness=0.6, dust=0.35, streaks=0.5, grime=0.6, scratches=0.4, mottle=0.2,
             image=None, image_strength=1.0, dirt_color=(0.035, 0.03, 0.022), dust_color=(0.20, 0.19, 0.17)):
    """Weathered material. Base colour is `color` (linear RGB) or, if `image` is a file path, that image
    read through the 'src' UV layer (use image_plane()/set_src_uv() to create it).
    Weathering: mottling, scratches + worn convex edges (lighter), dust on upward faces, vertical rain
    streaks, grime near the ground (object Z < 0.25 m) and in crevices (AO). Only Base Color is baked."""
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
        if isinstance(fac, (int, float)): n.inputs[0].default_value = fac
        else: L.new(fac, n.inputs[0])
        return n.outputs[2]

    def math_node(op, a, b=None, clamp=True):
        n = N.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
        for sock, val in ((n.inputs[0], a), (n.inputs[1], b)):
            if val is None: continue
            if isinstance(val, (int, float)): sock.default_value = val
            else: L.new(val, sock)
        return n.outputs[0]

    def noise(scale, detail=6, stretch=None):
        t = N.new("ShaderNodeTexNoise"); t.inputs["Scale"].default_value = scale; t.inputs["Detail"].default_value = detail
        src = coord.outputs["Object"]
        if stretch:
            mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = stretch
            L.new(src, mp.inputs["Vector"]); src = mp.outputs["Vector"]
        L.new(src, t.inputs["Vector"])
        return t.outputs["Fac"]

    def ramp(fac, a, b):
        """0 at fac=a, 1 at fac=b. Blender does not re-sort colour-ramp stops, so a > b (falling ramp)
        must be built as ascending stops with swapped colours."""
        r = N.new("ShaderNodeValToRGB")
        e0, e1 = r.color_ramp.elements
        if a <= b:
            e0.position, e1.position = a, b
        else:
            e0.position, e1.position = b, a
            e0.color, e1.color = (1, 1, 1, 1), (0, 0, 0, 1)
        L.new(fac, r.inputs["Fac"])
        return r.outputs["Color"]

    if image:
        uvn = N.new("ShaderNodeUVMap"); uvn.uv_map = SRC_UV
        tex = N.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(image, check_existing=True)
        tex.extension = 'CLIP'
        L.new(uvn.outputs["UV"], tex.inputs["Vector"])
        base = tex.outputs["Color"]
        if image_strength < 1.0:
            base = mix((*color,)[:3], base, image_strength)
        col = mix(base, base, 0.0)  # pass-through so later mixes have a socket
        # gentle mottling on top of the image
        mot = N.new("ShaderNodeMix"); mot.data_type = 'RGBA'; mot.blend_type = 'MULTIPLY'; mot.clamp_factor = True
        L.new(col, mot.inputs[6]); mot.inputs[7].default_value = (1 - mottle, 1 - mottle, 1 - mottle, 1)
        L.new(noise(70), mot.inputs[0])
        col = mot.outputs[2]
        light = (0.85, 0.85, 0.85)
    else:
        col = mix(tuple(c * (1 - mottle) for c in color), tuple(c * (1 + mottle) for c in color), noise(70))
        light = tuple(min(1.0, c * 2.5 + 0.06) for c in color)

    if scratches > 0:
        scr = ramp(noise(160, 2, stretch=(1, 1, 18)), 0.62, 0.66)
        edges = ramp(geo.outputs["Pointiness"], 0.52, 0.58)
        wear = math_node('MULTIPLY', math_node('ADD', scr, edges), scratches)
        col = mix(col, light, wear)

    if dust > 0:
        sep = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], sep.inputs["Vector"])
        up = math_node('MULTIPLY', ramp(sep.outputs["Z"], 0.3, 0.9), noise(12))
        film = math_node('ADD', math_node('MULTIPLY', up, 1.4), 0.12)
        col = mix(col, dust_color, math_node('MULTIPLY', film, dust))

    if grime > 0:
        streak = ramp(noise(5, 4, stretch=(16, 16, 0.9)), 0.55, 0.8)
        sepp = N.new("ShaderNodeSeparateXYZ"); L.new(coord.outputs["Object"], sepp.inputs["Vector"])
        ground = ramp(sepp.outputs["Z"], 0.25, 0.0)
        ao = N.new("ShaderNodeAmbientOcclusion"); ao.samples = 16; ao.inputs["Distance"].default_value = 0.05
        crev = math_node('SUBTRACT', 1.0, ao.outputs["AO"])
        g = math_node('ADD', math_node('ADD', math_node('MULTIPLY', streak, streaks), ground), crev)
        col = mix(col, dirt_color, math_node('MULTIPLY', g, grime))

    L.new(col, bsdf.inputs["Base Color"])
    return m


def flat(name, color, roughness=0.5, image=None):
    """Printed/painted surface (stickers, reflective sheeting): clean with a little dirt."""
    return material(name, color, roughness, dust=0.15, streaks=0.3, grime=0.25, scratches=0.15, mottle=0.04, image=image)


def emissive_look(name, color, glow=0.35):
    """Lens / light: baked colour is brightened so it reads as 'lit' in an engine without emission."""
    c = tuple(min(1.0, x * (1 + glow) + glow * 0.15) for x in color)
    return material(name, c, 0.2, dust=0.1, streaks=0.2, grime=0.2, scratches=0.05, mottle=0.08)


# ---------------------------------------------------------------- geometry

def add_bevel(o, width, segments=3, angle=40):
    mod = o.modifiers.new("Bevel", 'BEVEL')
    mod.width = width; mod.segments = segments
    mod.limit_method = 'ANGLE'; mod.angle_limit = math.radians(angle)
    return o


def _finish_primitive(name, mat, bevel, segments):
    o = bpy.context.active_object
    o.name = name
    if mat is not None:
        o.data.materials.append(mat)
    if bevel:
        add_bevel(o, bevel, segments)
    return o


def box(name, size, loc, mat, bevel=0.008, segments=2):
    """Axis-aligned box of `size` (x, y, z) centred at `loc`. Scale is applied, location/rotation are NOT
    (so rotation_euler set afterwards rotates around the box centre)."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return _finish_primitive(name, mat, bevel, segments)


def cyl(name, r, length, loc, mat, axis='Z', verts=24, bevel=0.004, segments=2, r2=None):
    """Cylinder (or cone/frustum if r2 is given = top radius) along `axis`, centred at `loc`."""
    rot = {'X': (0, math.radians(90), 0), 'Y': (math.radians(90), 0, 0), 'Z': (0, 0, 0)}[axis]
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=length, location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=length, location=loc, rotation=rot)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    return _finish_primitive(name, mat, bevel, segments)


def set_src_uv(obj, func):
    """Create/overwrite the 'src' UV layer: func(world_co: Vector, face_normal: Vector) -> (u, v)."""
    me = obj.data
    uv = me.uv_layers.get(SRC_UV) or me.uv_layers.new(name=SRC_UV)
    mw = obj.matrix_world
    for poly in me.polygons:
        n = (mw.to_3x3() @ poly.normal).normalized()
        for li in poly.loop_indices:
            co = mw @ me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv = func(co, n)


def image_plane(name, image_path, width, height, loc, rot=(math.radians(90), 0, 0), thickness=0.0,
                mat_kwargs=None):
    """Rectangle showing an image, 1:1 UV mapped. Default rotation stands it up facing -Y.
    thickness > 0 adds a solid back (Solidify) whose faces get the edge colour of the image."""
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.scale = (width, height, 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    uv = o.data.uv_layers[0]; uv.name = SRC_UV
    for li, loop in enumerate(o.data.loops):
        co = o.data.vertices[loop.vertex_index].co
        uv.data[li].uv = (co.x / width + 0.5, co.y / height + 0.5)
    o.data.materials.append(flat(name + "_mat", (0.8, 0.8, 0.8), image=image_path, **(mat_kwargs or {})))
    if thickness:
        s = o.modifiers.new("Solidify", 'SOLIDIFY'); s.thickness = thickness; s.offset = 1.0
    return o


def join_all(name, smooth_angle=35, objects=None):
    """Convert (applies modifiers) and join all mesh/text/curve objects into one mesh object."""
    objs = objects or [o for o in bpy.data.objects if o.type in ('MESH', 'FONT', 'CURVE')]
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.convert(target='MESH')
    if len(objs) > 1:
        bpy.ops.object.join()
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = name
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(smooth_angle))
    return obj


def place_bottom_centre_at_origin(obj):
    """Apply transforms, move origin to the bottom centre of the bounding box and the object to (0,0,0)."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    vs = [v.co for v in obj.data.vertices]
    lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
    hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
    pivot = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    for v in obj.data.vertices:
        v.co -= pivot
    obj.location = (0, 0, 0)
    return pivot


def tri_count(obj):
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


# ---------------------------------------------------------------- bake + export

def bake_and_export(obj, out_dir, name, res=1024, ao_strength=0.55, samples=32, margin=16, uv_margin=0.006,
                    keep_origin=False):
    """Bake base colour (incl. procedural weathering and images) x AO into one PNG on a fresh 'bake' UV
    layer, then export OBJ (+PNG) with engine settings. Returns (obj_path, png_path).
    keep_origin=True keeps the object's current origin instead of moving it to the bottom centre
    (use for parts with a defined pivot, e.g. a lamp's mount point)."""
    os.makedirs(out_dir, exist_ok=True)
    if not keep_origin:
        place_bottom_centre_at_origin(obj)
    me = obj.data
    bake_uv = me.uv_layers.get(BAKE_UV) or me.uv_layers.new(name=BAKE_UV)
    me.uv_layers.active = bake_uv
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    # correct_aspect=False: otherwise the unwrap squashes islands to the aspect ratio of whatever image
    # texture node is active in the material (e.g. a 1:4 sign graphic).
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=uv_margin, correct_aspect=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    scene = bpy.context.scene
    try:
        scene.render.engine = 'CYCLES'
    except TypeError as e:
        raise RuntimeError(f"Cycles not available: {e}")
    scene.cycles.samples = samples
    scene.cycles.device = 'CPU'

    def bake(kind):
        # Transparent start so unbaked texels can be found afterwards (alpha stays 0 there).
        img = bpy.data.images.new(f"{name}_{kind}", res, res, alpha=True)
        img.generated_color = (0, 0, 0, 0)
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
    # Fill texels outside all UV islands (+margin) with the average colour, so lower mip levels don't
    # bleed black into island edges at a distance.
    empty = c[:, 3] < 0.5
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

    # Keep only the bake UV layer and a single preview material that shows the baked texture.
    for layer in [l for l in me.uv_layers if l.name != BAKE_UV]:
        me.uv_layers.remove(layer)
    preview = bpy.data.materials.new(name + "_baked")
    preview.use_nodes = True
    pn = preview.node_tree.nodes
    t = pn.new("ShaderNodeTexImage"); t.image = final
    preview.node_tree.links.new(t.outputs["Color"], next(n for n in pn if n.type == "BSDF_PRINCIPLED").inputs["Base Color"])
    pn.active = t
    me.materials.clear(); me.materials.append(preview)

    path = os.path.join(out_dir, name + ".obj")
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
    bpy.ops.wm.obj_export(filepath=path, export_selected_objects=True, forward_axis='NEGATIVE_Z', up_axis='Y',
                          export_triangulated_mesh=True, export_normals=True, export_uv=True,
                          export_materials=False, apply_modifiers=True, global_scale=1.0)
    print(f"exported {name}: tris {tri_count(obj)}, dims {tuple(round(d, 3) for d in obj.dimensions)}, {path}")
    return path, png


# ---------------------------------------------------------------- previews

def render_previews(obj, out_png, views=("front", "three_quarter", "side", "back"), size=512, extra_objects=()):
    """Workbench render of the (baked) object from several views, stitched side by side into one PNG.
    Views: front (from -Y), back (+Y), side (from +X), three_quarter, top, or an (x, y, z) direction."""
    dirs = {"front": (0, -1, 0.15), "back": (0, 1, 0.15), "side": (1, 0, 0.15), "left": (-1, 0, 0.15),
            "three_quarter": (0.7, -0.9, 0.45), "top": (0, -0.01, 1)}
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'TEXTURE'
    scene.display.shading.show_cavity = False
    scene.render.resolution_x = scene.render.resolution_y = size
    scene.render.film_transparent = False
    scene.world = scene.world or bpy.data.worlds.new("World")
    targets = [obj, *extra_objects]
    pts = [o.matrix_world @ Vector(c) for o in targets for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    centre, radius = (lo + hi) / 2, (hi - lo).length / 2
    cam_data = bpy.data.cameras.new("__preview_cam"); cam_data.lens = 50
    cam = bpy.data.objects.new("__preview_cam", cam_data); scene.collection.objects.link(cam)
    scene.camera = cam
    tiles = []
    tmp = out_png + ".tmp.png"
    for v in views:
        d = Vector(dirs[v] if isinstance(v, str) else v).normalized()
        cam.location = centre + d * radius * 3.2
        cam.rotation_euler = (centre - cam.location).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = tmp
        bpy.ops.render.render(write_still=True)
        img = bpy.data.images.load(tmp)
        tiles.append(np.array(img.pixels[:]).reshape(size, size, 4))
        bpy.data.images.remove(img)
    os.remove(tmp)
    sheet = np.concatenate(tiles, axis=1)
    out = bpy.data.images.new("__sheet", size * len(tiles), size)
    out.pixels[:] = sheet.ravel()
    out.filepath_raw = out_png; out.file_format = 'PNG'; out.save()
    bpy.data.images.remove(out)
    bpy.data.objects.remove(cam); bpy.data.cameras.remove(cam_data)
    print("preview", out_png)
    return out_png


def import_obj(path, png, name=None):
    """Import an exported OBJ + PNG (e.g. to preview a prop together with a mounted part)."""
    bpy.ops.wm.obj_import(filepath=path, forward_axis='NEGATIVE_Z', up_axis='Y')
    o = bpy.context.selected_objects[0]
    if name: o.name = name
    m = bpy.data.materials.new((name or o.name) + "_mat"); m.use_nodes = True
    t = m.node_tree.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(png, check_existing=True)
    m.node_tree.links.new(t.outputs["Color"], next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"])
    m.node_tree.nodes.active = t
    o.data.materials.clear(); o.data.materials.append(m)
    return o
