# German Leitkegel (traffic cone, StVO Zeichen 610) in two sizes, 500 mm and 750 mm.
#
# References (viewing only, see tools/asset-spike/ref/leitkegel/de/index.tsv and ref/signs/sources.tsv):
# - ref/signs/z610.png: official graphic "Zeichen 610-40 bis 43 - Leitkegel" (one drawing for all sizes):
#   truncated cone on a black base line, 5 equal zones red / white / red / white / red.
# - ref/leitkegel/de/02.jpg, 03.jpg, 05.jpg (Berlin): leuchtrot cones, 2 white retroreflective bands,
#   black square rubber base with chamfered corners, small capped top. Measured from the photos:
#   bands ~ equal fifths of the body height, bottom diameter ~ 0.38 x body height, top ~ 0.06 x.
# - ref/leitkegel/de/04.jpg (Leipzig), 08.jpg, ref/baustelle/13.jpg: smaller one-piece PVC cones whose
#   square base is moulded in the same red-orange, 2 (13: 1) white bands, open top with a hole.
#
# Variants: "75" = 750 mm on a black rubber base (400 x 400 mm), "50" = 500 mm one-piece PVC (300 x 300 mm).
# Both use the 2-white-band layout of the official graphic (it is the same drawing for 610-40...43, and
# every German photo shows 2 white bands regardless of size).
#
# Blender Z-up, 1 unit = 1 m, front (a base edge) faces -Y.
# Usage (headless):
#   blender --background --factory-startup --python gen_leitkegel.py            -> both variants
#   blender --background --factory-startup --python gen_leitkegel.py -- 75       -> one variant
import bpy, bmesh, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPIKE = os.path.dirname(HERE)
sys.path.insert(0, SPIKE)
import asset_lib as al

OUT = os.path.join(SPIKE, "out", "baustelle", "leitkegel")
SEGS = 32

# Colours are linear RGB. Leuchtrot sampled from the photos (overcast ~ sRGB 160/30/22, flash ~ 240/58/51):
# target albedo sRGB ~ (230, 52, 34) for the TL cone; the one-piece PVC cone (04.jpg ~ 222/57/63, 13.jpg ~ 240/58/51)
# gets a slightly brighter fluorescent red ~ (238, 60, 44).
RED_TL = (0.79, 0.034, 0.016)
RED_PVC = (0.86, 0.046, 0.026)
WHITE_RETRO = (0.77, 0.77, 0.75)     # retroreflective sheeting, slightly silvery
RUBBER = (0.018, 0.018, 0.019)       # recycled rubber base
HOLE = (0.03, 0.012, 0.01)

VARIANTS = {
    # H total height; bw base width; bh base edge height; btop base height at the collar; chamf corner cut;
    # inset = width of the sloped rim on the base top; rb/rt cone radius at the bottom/top; hole radius;
    # collar radius/height (ring where the cone enters the base); lip = height of the top cap, bead = how far
    # the cap stands out over the cone (the small knob seen on the photos).
    "75": dict(H=0.75, bw=0.40, bh=0.030, btop=0.040, chamf=0.065, inset=0.035, rb=0.140, rt=0.024,
               hole=0.015, cr=0.154, ch=0.020, lip=0.018, bead=0.005, red=RED_TL, base="rubber"),
    "50": dict(H=0.50, bw=0.30, bh=0.014, btop=0.020, chamf=0.050, inset=0.025, rb=0.105, rt=0.020,
               hole=0.012, cr=0.113, ch=0.012, lip=0.013, bead=0.004, red=RED_PVC, base="pvc"),
}


# ---------------------------------------------------------------- helpers (local, asset_lib is shared)

def lathe(name, profile, mats, segs=SEGS):
    """Surface of revolution around Z. profile = [(r, z, slot), ...]; slot = material index of the strip from
    this point to the next. Walk outside-up, over the top, down into the hole: normals then point outwards
    (and into the hole's open side). A point with r == 0 closes the surface with a triangle fan."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    angs = [2 * math.pi * i / segs + math.pi / segs for i in range(segs)]
    rings = []
    for r, z, _ in profile:
        if r <= 1e-9:
            rings.append([bm.verts.new((0, 0, z))])
        else:
            rings.append([bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for a in angs])
    for k in range(len(profile) - 1):
        A, B, slot = rings[k], rings[k + 1], profile[k][2]
        for i in range(segs):
            j = (i + 1) % segs
            f = bm.faces.new((A[i], A[j], B[0]) if len(B) == 1 else (A[i], A[j], B[j], B[i]))
            f.material_index = slot
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    for m in mats:
        me.materials.append(m)
    return o


def base_plate(name, v, mat):
    """Square base with chamfered corners; the top slopes up from the edge (bh) to an inner plateau (btop)."""
    a, c, d = v["bw"] / 2, v["chamf"], v["inset"]

    def octagon(half, cut, z):
        pts = [(half - cut, -half), (half, -half + cut), (half, half - cut), (half - cut, half),
               (-half + cut, half), (-half, half - cut), (-half, -half + cut), (-half + cut, -half)]
        return [bm.verts.new((x, y, z)) for x, y in pts]

    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bot = octagon(a, c, 0.0)
    top = octagon(a, c, v["bh"])
    inner = octagon(a - d, c * 0.6, v["btop"])
    bm.faces.new(list(reversed(bot)))
    for ring_a, ring_b in ((bot, top), (top, inner)):
        for i in range(8):
            j = (i + 1) % 8
            bm.faces.new((ring_a[i], ring_a[j], ring_b[j], ring_b[i]))
    bm.faces.new(inner)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    me.materials.append(mat)
    al.add_bevel(o, min(0.006, v["bh"] * 0.3), segments=2, angle=30)
    return o


def add_overlay(m, color, amount, z_hi, z_lo=0.0, scale=(3.0, 3.0, 14.0), lo=0.55, hi=0.66, detail=8, offset=0.0):
    """Mix `color` into the material's Base Color in noisy patches, fading out from z_lo (full) to z_hi (none),
    object space. Used for tyre/kick scuffs and abrasion near the foot of the cone."""
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    bsdf = next(n for n in N if n.type == "BSDF_PRINCIPLED")
    src = bsdf.inputs["Base Color"].links[0].from_socket
    coord = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = scale
    mp.inputs["Location"].default_value = (offset, offset * 0.7, 0)
    L.new(coord.outputs["Object"], mp.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 1.0
    nz.inputs["Detail"].default_value = detail
    L.new(mp.outputs["Vector"], nz.inputs["Vector"])
    rp = N.new("ShaderNodeValToRGB")
    rp.color_ramp.elements[0].position = lo
    rp.color_ramp.elements[1].position = hi
    L.new(nz.outputs["Fac"], rp.inputs["Fac"])
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(coord.outputs["Object"], sep.inputs["Vector"])
    mr = N.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = z_hi
    mr.inputs["From Max"].default_value = z_lo
    mr.clamp = True
    L.new(sep.outputs["Z"], mr.inputs["Value"])
    mul = N.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'; mul.use_clamp = True
    L.new(rp.outputs["Color"], mul.inputs[0]); L.new(mr.outputs["Result"], mul.inputs[1])
    mul2 = N.new("ShaderNodeMath"); mul2.operation = 'MULTIPLY'; mul2.use_clamp = True
    L.new(mul.outputs[0], mul2.inputs[0]); mul2.inputs[1].default_value = amount
    mix = N.new("ShaderNodeMix"); mix.data_type = 'RGBA'; mix.clamp_factor = True
    L.new(mul2.outputs[0], mix.inputs[0]); L.new(src, mix.inputs[6]); mix.inputs[7].default_value = (*color, 1)
    L.new(mix.outputs[2], bsdf.inputs["Base Color"])
    return m


# ---------------------------------------------------------------- build

def build(key):
    v = VARIANTS[key]
    al.clear_scene()
    H, zb = v["H"], v["btop"]

    red = al.material("red_pvc", v["red"], roughness=0.45, dust=0.22, streaks=0.3, grime=0.3, scratches=0.3, mottle=0.07)
    white = al.material("retro_white", WHITE_RETRO, roughness=0.3, dust=0.25, streaks=0.35, grime=0.3, scratches=0.12,
                        mottle=0.05)
    hole = al.material("hole", HOLE, dust=0.0, streaks=0.0, grime=0.0, scratches=0.0, mottle=0.1)
    if v["base"] == "rubber":
        base = al.material("rubber_base", RUBBER, roughness=0.9, dust=0.15, streaks=0.2, grime=0.2, scratches=0.18,
                           mottle=0.3)
    else:
        # One-piece PVC: the base must stay as saturated as the body (13.jpg, de/08.jpg) -> little, dark dust.
        base = al.material("pvc_base", v["red"], roughness=0.5, dust=0.08, streaks=0.25, grime=0.22, scratches=0.08,
                           mottle=0.08, dust_color=(0.09, 0.07, 0.05))
    # Scuffs near the foot: dark tyre/shoe marks and grey abrasion; fades out ~ 30 % up the cone.
    zs = 0.30 * H
    for m in (red, white):
        add_overlay(m, (0.02, 0.018, 0.016), 0.5, zs, scale=(5.0, 5.0, 26.0), lo=0.58, hi=0.66, offset=1.3)
        add_overlay(m, (0.35, 0.33, 0.31), 0.2, zs * 0.8, scale=(9.0, 9.0, 30.0), lo=0.6, hi=0.68, offset=4.1)
    if v["base"] == "rubber":
        add_overlay(base, (0.13, 0.125, 0.12), 0.35, 0.06, scale=(5.0, 5.0, 5.0), lo=0.6, hi=0.7, offset=2.7)
    else:
        add_overlay(base, (0.05, 0.045, 0.04), 0.18, 0.06, scale=(5.0, 5.0, 5.0), lo=0.62, hi=0.7, offset=2.7)

    def r_at(z):  # cone radius between the base top (zb) and the top cap (H - lip)
        zt = H - v["lip"]
        return v["rb"] + (v["rt"] - v["rb"]) * (z - zb) / (zt - zb)

    RED, WHITE, BASE, HOLE_ = 0, 1, 2, 3
    zone = (H - zb) / 5.0                         # official graphic: 5 equal zones R/W/R/W/R
    zc = zb + v["ch"]                             # top of the collar
    zt = H - v["lip"]
    cr, rt, ho, bd = v["cr"], v["rt"], v["hole"], v["bead"]
    e = min(0.004, v["ch"] * 0.3)
    prof = [
        (cr, zb - 0.008, BASE),                   # collar: starts inside the base plateau
        (cr, zc - e, BASE),
        (cr - e, zc, BASE),                       # rounded collar top edge
        (r_at(zc) + 0.001, zc, RED),              # end of the flat ring on the collar; cone starts here
        (r_at(zb + zone), zb + zone, WHITE),
        (r_at(zb + 2 * zone), zb + 2 * zone, RED),
        (r_at(zb + 3 * zone), zb + 3 * zone, WHITE),
        (r_at(zb + 4 * zone), zb + 4 * zone, RED),
        (rt, zt, RED),                            # top cap: bead underside, bead side (rounded in), top ring,
        (rt + bd, zt + bd, RED),                  # 1.5 cm deep hole -> 4 strips + fan (288 tris)
        (rt + bd - 0.003, H, RED),
        (ho, H, HOLE_),
        (ho, H - 0.015, HOLE_),
        (0.0, H - 0.015, HOLE_),
    ]
    cone = lathe("cone", prof, [red, white, base, hole])
    base_plate("base", v, base)
    obj = al.join_all(f"PROP_Leitkegel_{key}")
    return obj


def run(key):
    name = f"PROP_Leitkegel_{key}"
    obj = build(key)
    obj_path, png = al.bake_and_export(obj, OUT, name, res=1024)
    al.render_previews(obj, os.path.join(OUT, name + "_preview.png"), views=("front", "three_quarter", "side", "top"))
    print("TRIS", name, al.tri_count(obj), "DIMS", tuple(round(d, 4) for d in obj.dimensions))


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    for k in (argv or ["50", "75"]):
        run(k)
