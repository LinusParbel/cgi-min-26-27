# German mobile road-works barrier gate ("Absperrschrankengitter"), yellow plastic frame with
# red/white Zeichen-600-style reflective bands at top and bottom, vertical slats in between, a blank
# owner plate in the centre, lamp pegs on the top rail and two flat plastic feet.
# Reference: tools/asset-spike/ref/baustelle/10.jpg (measured from the photo: element 2.0 m x ~1.0 m,
# top band ~0.24 m, bottom band ~0.10 m, stripe width ~0.19 m = 1/10 of the band length, slat groups
# centred under the stripes, openings under the stripe borders, lamps on the 3rd/7th peg).
#
# Front faces -Y. One mesh, one baked PNG (colour x AO), OBJ export via asset_lib.
# Run headless:
#   blender --background --factory-startup --python gen_absperrschranke.py -- gelb [rotweiss]
import sys, os, math, json
import bpy, bmesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import asset_lib as al

OUT = os.path.join(os.path.dirname(HERE), "out", "baustelle", "absperrschranke")

# ---------------------------------------------------------------- dimensions (metres)
L = 2.0                    # frame length, outer edge of post to outer edge of post
POST_R = 0.027             # vertical end tubes
POST_X = L / 2 - POST_R    # post centre
INNER = POST_X - POST_R    # inner face of the posts (= end of the bands)
N_STRIPES = 10             # half red + 9 full + half red
S = 2 * INNER / N_STRIPES  # stripe width (~0.189)

RAIL_D = 0.050             # depth (Y) of the horizontal rails
BAND_D = 0.032             # depth of the striped panels (recessed behind the rails)
SLAT_D = 0.036             # depth of the vertical slats
WEB_D = 0.030              # web between the slats of one group (shallow grooves, not see-through)

# vertical layout (z of bottom, top)
FOOT_H = 0.055
HUMP_H = 0.100
BOT_RAIL = (0.110, 0.145)
BOT_BAND = (0.145, 0.245)
MID_RAIL1 = (0.245, 0.277)
SLATS = (0.277, 0.638)
MID_RAIL2 = (0.638, 0.670)
TOP_BAND = (0.670, 0.905)
TOP_RAIL = (0.905, 0.940)
POST_TOP = 0.990
PEG_H = 0.030
PEG_R = 0.018

OPEN_W = 0.068             # see-through opening under each stripe border
GROUP_W = S - OPEN_W       # slat group under each stripe
LAMP_PEGS = (-2, 2)
TAB_W, TAB_T, TAB_H = 0.12, 0.022, 0.040   # lamp tabs replacing the pegs at LAMP_PEGS        # lamps sit on the pegs above the 3rd and 7th full stripe

# ---------------------------------------------------------------- colours (linear RGB)
TRAFFIC_YELLOW = (0.95, 0.63, 0.010)   # RAL 1023-ish (photo: G/R ~ 0.85)
FILM_RED = (0.58, 0.012, 0.018)        # RAL 3020-ish retroreflective film
FILM_WHITE = (0.90, 0.90, 0.88)
FRAME_RED = (0.40, 0.012, 0.014)       # red plastic frame, darker than the film so the stripes stay readable
RUBBER = (0.030, 0.030, 0.032)         # recycled-rubber feet

VARIANTS = {
    "gelb": dict(body=TRAFFIC_YELLOW, foot=(0.74, 0.46, 0.008), body_dust=0.08, body_grime=0.18, foot_dust=0.5),
    "rotweiss": dict(body=FRAME_RED, foot=RUBBER, body_dust=0.15, body_grime=0.25, foot_dust=0.22),
}


def zc(rng):
    return (rng[0] + rng[1]) / 2


def zh(rng):
    return rng[1] - rng[0]


def tapered_box(name, size, loc, mat, top_x=1.0, top_y=1.0, bevel=0.006, segments=1):
    """Box whose top face is scaled by (top_x, top_y) -> sloped sides (feet, sockets)."""
    o = al.box(name, size, loc, mat, bevel=0)
    bm = bmesh.new(); bm.from_mesh(o.data)
    for v in bm.verts:
        if v.co.z > 0:
            v.co.x *= top_x; v.co.y *= top_y
    bm.to_mesh(o.data); bm.free()
    if bevel:
        al.add_bevel(o, bevel, segments, 30)
    return o


def only_y_faces(o):
    """Delete all faces of a (non-bevelled) box except front/back: the rest is hidden inside rails,
    posts or neighbouring boxes and would only waste texture space."""
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if abs(f.normal.y) < 0.5], context='FACES')
    bm.to_mesh(o.data); bm.free()
    return o


def build(variant):
    v = VARIANTS[variant]
    al.clear_scene()
    BODY = al.material("body", v["body"], roughness=0.45, dust=v["body_dust"], streaks=0.3,
                       grime=v["body_grime"], scratches=0.15, mottle=0.05)
    FOOT = al.material("foot", v["foot"], roughness=0.6, dust=v["foot_dust"], streaks=0.4, grime=0.45,
                       scratches=0.3, mottle=0.12)
    film = dict(roughness=0.35, dust=0.08, streaks=0.2, grime=0.12, scratches=0.06, mottle=0.03)
    RED = al.material("film_red", FILM_RED, **film)
    WHITE = al.material("film_white", FILM_WHITE, **film)
    LABEL = al.material("label_white", (0.85, 0.86, 0.86), **film)
    LABEL_BLUE = al.material("label_blue", (0.05, 0.30, 0.62), **film)

    # --- posts (round tubes, rounded top), standing in the foot sockets
    for sx in (-1, 1):
        h = POST_TOP - 0.06
        al.cyl(f"post_{sx}", POST_R, h, (sx * POST_X, 0, 0.06 + h / 2), BODY, 'Z', verts=16, bevel=0.012, segments=2)

    # --- horizontal rails (run into the posts)
    for name, rng in (("rail_bot", BOT_RAIL), ("rail_mid1", MID_RAIL1), ("rail_mid2", MID_RAIL2), ("rail_top", TOP_RAIL)):
        al.box(name, (2 * POST_X, RAIL_D, zh(rng)), (0, 0, zc(rng)), BODY, bevel=0.007, segments=2)

    # --- red/white bands: one box per stripe, so colour borders follow the geometry (always crisp)
    for bname, rng in (("band_top", TOP_BAND), ("band_bot", BOT_BAND)):
        edges = [-INNER - 0.01] + [-INNER + S * (k + 0.5) for k in range(N_STRIPES)] + [INNER + 0.01]
        for k in range(len(edges) - 1):
            x0, x1 = edges[k], edges[k + 1]
            mat = RED if k % 2 == 0 else WHITE
            only_y_faces(al.box(f"{bname}_{k}", (x1 - x0, BAND_D, zh(rng) + 0.004), ((x0 + x1) / 2, 0, zc(rng)), mat, bevel=0))

    # small inventory sticker on the front of a red stripe (as in the photo); embedded decal boxes,
    # front face 2 mm in front of the film
    sx_, sz_ = 3 * S, TOP_BAND[1] - 0.085
    al.box("sticker", (0.12, 0.0045, 0.07), (sx_, -BAND_D / 2 - 0.00025, sz_), LABEL, bevel=0)      # front 2.5 mm out
    al.box("sticker_field", (0.10, 0.0060, 0.042), (sx_, -BAND_D / 2 - 0.0010, sz_), LABEL_BLUE, bevel=0)  # +1.5 mm

    # --- slat field: groups of three slats under every stripe, openings under the stripe borders
    sz = (SLATS[0] - 0.006, SLATS[1] + 0.006)
    gap = 0.005

    def slat_group(name, x0, x1, n, z=sz):
        w = (x1 - x0 - (n - 1) * gap) / n
        for j in range(n):
            xs = x0 + j * (w + gap) + w / 2
            al.box(f"{name}_s{j}", (w, SLAT_D, zh(z)), (xs, 0, zc(z)), BODY, bevel=0.005, segments=1)
        if n > 1:
            only_y_faces(al.box(f"{name}_web", (x1 - x0 - 0.004, WEB_D, zh(z)), ((x0 + x1) / 2, 0, zc(z)), BODY, bevel=0))

    px = 0.74 * S                              # half width of the centre plate (photo: ~1.48 stripes wide)
    for i in range(-4, 5):
        if i == 0:
            continue
        x0, x1 = i * S - GROUP_W / 2, i * S + GROUP_W / 2
        if i == 1: x0 = px + 0.002            # groups next to the plate are a bit narrower
        if i == -1: x1 = -px - 0.002
        slat_group(f"grp{i}", x0, x1, 3)
    for sx in (-1, 1):   # narrow part between the post and the first opening
        a, b = INNER - 0.004, 4.5 * S + OPEN_W / 2
        slat_group(f"grp_end{sx}", min(sx * a, sx * b), max(sx * a, sx * b), 2)

    # centre: blank owner plate with a raised rim, a slat group below it, a divider above it
    plate = (0.352, 0.549)
    al.box("plate", (2 * px + 0.004, 0.030, zh(plate)), (0, 0, zc(plate)), BODY, bevel=0.004, segments=1)
    rim, rim_d = 0.014, SLAT_D + 0.002         # rim 1 mm proud of the slats -> no coplanar overlaps
    for name, size, loc in (
            ("plate_rim_t", (2 * px, rim_d, rim), (0, 0, plate[1] - rim / 2)),
            ("plate_rim_b", (2 * px, rim_d, rim), (0, 0, plate[0] + rim / 2)),
            # side rims fit between top and bottom rim -> no overlapping coplanar corner faces
            ("plate_rim_l", (rim, rim_d, zh(plate) - 2 * rim), (-px + rim / 2, 0, zc(plate))),
            ("plate_rim_r", (rim, rim_d, zh(plate) - 2 * rim), (px - rim / 2, 0, zc(plate)))):
        al.box(name, size, loc, BODY, bevel=0.004, segments=1)
    slat_group("grp_below", -0.052, 0.052, 3, z=(sz[0], plate[0] + 0.004))
    al.box("divider_above", (0.016, SLAT_D, sz[1] - plate[1] + 0.004), (0, 0, (plate[1] + sz[1]) / 2 - 0.002),
           BODY, bevel=0.004, segments=1)

    # --- lamp pegs on the top rail, one above the centre of every full stripe
    for i in range(-4, 5):
        if i in LAMP_PEGS:
            # flat tab like a Leitbake board edge: the Warnleuchte jaw (28 mm gap) straddles it
            al.box(f"lamp_tab{i}", (TAB_W, TAB_T, TAB_H + 0.002), (i * S, 0, TOP_RAIL[1] + TAB_H / 2 - 0.001), BODY,
                   bevel=0.003, segments=1)
            continue
        al.cyl(f"peg{i}", PEG_R, PEG_H + 0.004, (i * S, 0, TOP_RAIL[1] + PEG_H / 2 - 0.002), BODY, 'Z',
               verts=12, bevel=0.005, segments=1)

    # --- feet: flat plastic blocks perpendicular to the gate, socket hump around the post, ribs
    for sx in (-1, 1):
        x = sx * POST_X
        tapered_box(f"foot_{sx}", (0.24, 0.66, FOOT_H), (x, 0, FOOT_H / 2), FOOT, top_x=0.86, top_y=0.80, bevel=0.008)
        tapered_box(f"socket_{sx}", (0.15, 0.22, HUMP_H - FOOT_H + 0.004), (x, 0, (FOOT_H + HUMP_H) / 2 - 0.002), FOOT,
                    top_x=0.72, top_y=0.72, bevel=0.008)
        for fy in (-0.20, 0.20):
            al.box(f"rib_{sx}_{fy}", (0.17, 0.022, 0.016), (x, fy, FOOT_H + 0.004), FOOT, bevel=0.004, segments=1)

    obj = al.join_all(f"PROP_Absperrschranke_{variant}")
    print("built", variant, "tris", al.tri_count(obj))
    return obj


def export(variant, res=1024):
    name = f"PROP_Absperrschranke_{variant}"
    obj = build(variant)
    pivot = al.place_bottom_centre_at_origin(obj)
    obj_path, png = al.bake_and_export(obj, OUT, name, res=res, samples=48, keep_origin=True, ao_strength=0.4)
    mounts = [{"x": round(i * S - pivot.x, 4), "y": round(0.0 - pivot.y, 4), "z": round(TOP_RAIL[1] + TAB_H - pivot.z, 4)}
              for i in LAMP_PEGS]
    with open(os.path.join(OUT, "mounts.json"), "w") as f:   # same geometry -> one file for all variants
        json.dump({"mounts": mounts}, f, indent=2)
    al.render_previews(obj, os.path.join(OUT, name + "_preview.png"),
                       views=("front", "three_quarter", "side", "back", "top"))
    print("DONE", name, "tris", al.tri_count(obj), "dims", tuple(round(d, 3) for d in obj.dimensions),
          "pivot", tuple(round(c, 4) for c in pivot), "mounts", mounts)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["gelb"]
    for var in args:
        export(var)
