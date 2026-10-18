"""Voi-style e-scooter (2022 generation), built from spec.json.

Blender Z-up, metres. The scooter faces +Y; the origin is on the ground midway between the axles.
Rider's left = -X. Every number comes from spec.json; fix measurements there, never here.

Headless:  blender --background --factory-startup --python RunnerGame/Art/assets/scooter_voi/build.py -- [--preview out.png | --export]
"""
import math
import sys
from pathlib import Path

from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "lib"))
import photo_lib as pl  # noqa: E402

al = pl.al
PX = 0.254 / 156          # metres per pixel in ref/17.jpg (ruler), for photo-only landmark positions


def build(spec):
    d, c = spec.d, spec.c
    # painted/printed/lit surfaces stay clean; everything else is a lightly weathered used rental scooter
    mat = {}
    for name in spec.colors:
        if name in ("plate", "plate_ink", "reflector"):
            mat[name] = al.flat(name, c(name))
        elif name == "light_red":
            mat[name] = al.emissive_look(name, c(name))
        else:
            mat[name] = al.material(name, c(name), dust=0.2, streaks=0.3, grime=0.4, scratches=0.3, mottle=0.15)
    parts = {"body": [], "wheel_front": [], "wheel_rear": []}
    body = parts["body"].append

    R = d("wheel_d") / 2
    front = Vector((0, d("wheelbase") / 2, R))
    rear = Vector((0, -d("wheelbase") / 2, R))
    tilt = math.radians(d("stem_tilt_deg"))
    up = Vector((0, -math.sin(tilt), math.cos(tilt)))                    # stem axis, top leans back
    stem_b = Vector((0, front.y - d("stem_axle_off"), d("stem_b_h")))

    def on_stem(z):
        return stem_b + up * ((z - stem_b.z) / math.cos(tilt))

    # wheels: tyre + hub, axis along X
    for key, centre in (("wheel_front", front), ("wheel_rear", rear)):
        parts[key].append(al.cyl(key + "_tyre", R, d("wheel_w"), centre, mat["tyre"], axis='X', verts=32, bevel=0.012))
        parts[key].append(al.cyl(key + "_hub", R * 0.55, d("wheel_w") + 0.01, centre, mat["metal"], axis='X', verts=24))

    # fork: two legs from the crown down to the front axle, plus a small front mudguard
    crown = on_stem(d("crown_h"))
    leg_x = d("wheel_w") / 2 + 0.014
    for side in (-1, 1):
        body(pl.tube(f"fork_{side}", (side * leg_x, crown.y, crown.z), (side * leg_x, front.y, front.z), 0.014, mat["metal"]))
    body(al.box("fork_crown", (2 * leg_x + 0.03, 0.05, 0.04), crown, mat["band"]))
    body(pl.arc_shell("front_fender", front, R + 0.015, d("wheel_w") + 0.025, 70, 165, 0.01, mat["fender"]))

    # stem, black band, number-plate holder
    head_bottom = d("head_top_h") - d("head_h")
    body(pl.tube("stem", crown, on_stem(head_bottom), d("stem_d") / 2, mat["paint"]))
    body(pl.tube("stem_band", on_stem(0.50), on_stem(0.55), d("stem_d") / 2 + 0.003, mat["band"]))
    plate_centre = on_stem(d("box_bottom_h") + d("box_h") / 2) + Vector((0, d("box_fwd"), 0))
    plate = al.box("plate_holder", (d("box_w"), d("box_d"), d("box_h")), plate_centre, mat["box"])
    plate.rotation_euler.x = tilt
    body(plate)

    # head block on top of the stem, handlebar at its front edge
    bar_y = on_stem(d("bar_h")).y + d("bar_fwd")
    head_front_y = on_stem(d("head_top_h")).y + d("head_fwd")
    head_centre = Vector((0, head_front_y - d("head_len") / 2, d("head_top_h") - d("head_h") / 2))
    head = al.box("head", (0.075, d("head_len"), d("head_h")), head_centre, mat["box"], bevel=0.015)
    head.rotation_euler.x = math.radians(15)
    body(head)
    half = d("bar_w") / 2
    body(pl.tube("bar", (-half + 0.13, bar_y, d("bar_h")), (half - 0.13, bar_y, d("bar_h")), 0.012, mat["band"]))
    for side in (-1, 1):
        body(pl.tube(f"grip_{side}", (side * (half - 0.13), bar_y, d("bar_h")), (side * half, bar_y, d("bar_h")), 0.018, mat["grip"]))

    # deck: red body with the grip surface on top, down tube to the stem
    deck_front = front.y - d("deck_front_off")
    deck_rear = deck_front - d("deck_len")
    deck_mid = (deck_front + deck_rear) / 2
    skirt_h = d("deck_thick") - 0.01
    body(al.box("deck", (d("deck_w"), d("deck_len"), skirt_h), (0, deck_mid, d("deck_top_h") - 0.01 - skirt_h / 2), mat["paint"]))
    body(al.box("deck_grip", (d("deck_w") - 0.02, d("deck_len") - 0.02, 0.01), (0, deck_mid, d("deck_top_h") - 0.005), mat["deck"]))
    body(pl.tube("down_tube", crown + Vector((0, -0.02, 0)), (0, deck_front + 0.03, d("deck_top_h") - 0.03), 0.035, mat["paint"]))

    # rear fender hood: a solid sector over the rear wheel, from the deck end over the top down to axle height
    fender_end = deck_rear - d("rear_fender_len")
    hood_r = d("fender_top_h") - R
    body(pl.arc_shell("rear_fender", rear, 0.06, d("wheel_w") + 0.05, 20, 185, hood_r + 0.01 - 0.06, mat["fender"]))

    # --- details, in camera priority: rear light, plate, reflectors, rails, levers, display, kickstand
    hood_out = hood_r + 0.01                                  # outer radius of the rear hood around the rear axle

    def on_hood(name, size, angle_deg, mat_, lift=0.0, bevel=0.004):
        a = math.radians(angle_deg)
        n = Vector((0, math.cos(a), math.sin(a)))
        o = al.box(name, size, rear + n * (hood_out + size[1] / 2 + lift), mat_, bevel=bevel)
        o.rotation_euler.x = a
        body(o)
        return o, n

    on_hood("rear_light", (d("light_w"), d("light_t"), d("light_h")), d("light_angle_deg"), mat["light_red"], bevel=0.006)
    plate, n = on_hood("plate", (d("plate_w"), d("plate_t"), d("plate_h")), d("plate_angle_deg"), mat["plate"], lift=0.006, bevel=0.002)
    t_axis = Vector((0, -n.z, n.y))                           # tangent, upward along the plate
    for row in (0, 1):                                        # made-up number: 3 + 3 character blocks
        for i in range(3):
            p = rear + n * (hood_out + d("plate_t") + 0.008) + t_axis * (0.022 - row * 0.045) + Vector(((i - 1) * 0.038, 0, 0))
            ch = al.box(f"plate_char_{row}{i}", (0.022, 0.002, 0.032), p, mat["plate_ink"], bevel=0.0005, segments=1)
            ch.rotation_euler.x = math.radians(d("plate_angle_deg"))
            body(ch)

    for side in (-1, 1):
        x = side * (d("deck_w") / 2 + 0.001)
        body(al.box(f"reflector_{side}", (0.004, d("reflector_len"), d("reflector_h")), (x, deck_mid, d("deck_top_h") - 0.045), mat["reflector"], bevel=0.0015, segments=1))
        rx = side * (d("deck_w") / 2 - d("rail_w") / 2)
        body(al.box(f"rail_{side}", (d("rail_w"), d("deck_len"), d("rail_h")), (rx, deck_mid, d("deck_top_h") + d("rail_h") / 2 - 0.008), mat["paint"], bevel=0.003))

    half_bar = d("bar_w") / 2
    for side in (-1, 1):
        root = (side * (half_bar - d("lever_in")), bar_y - 0.015, d("bar_h") - 0.005)
        tip = (side * (half_bar - d("lever_in") + 0.03), bar_y - 0.015 - d("lever_len") * 0.9, d("bar_h") - 0.04)
        body(pl.tube(f"lever_{side}", root, tip, d("lever_r"), mat["band"], verts=8))
    tilt_head = math.radians(15)
    head_top = head_centre + Vector((0, -math.sin(tilt_head), math.cos(tilt_head))) * (d("head_h") / 2 + d("display_h") / 2 - 0.002)
    display = al.box("display", (d("display_w"), d("display_d"), d("display_h")), head_top, mat["band"], bevel=0.004)
    display.rotation_euler.x = tilt_head
    body(display)

    kx = -(d("deck_w") / 2 + d("kick_r") + 0.004)             # folded kickstand on the rider's left (-X)
    k0 = (kx, deck_mid - d("kick_len") / 2, d("kick_z"))
    k1 = (kx, deck_mid + d("kick_len") / 2, d("kick_z") + 0.01)
    body(pl.tube("kickstand", k0, k1, d("kick_r"), mat["metal"], verts=8))
    body(al.box("kickstand_foot", (0.03, 0.045, 0.014), (kx, k0[1] - 0.01, d("kick_z")), mat["band"], bevel=0.003))

    # landmarks (names match refs.json)
    for name, loc in {
        "front_axle": front, "rear_axle": rear,
        "front_axle_top": front + Vector((0, 0, R)), "front_axle_bottom": front - Vector((0, 0, R)),
        "rear_axle_bottom": rear - Vector((0, 0, R)), "front_tyre_front": front + Vector((0, R, 0)),
        "bar_left": (-half, bar_y, d("bar_h")), "bar_right": (half, bar_y, d("bar_h")),
        "stem_top": on_stem(head_bottom), "stem_a": on_stem(0.900), "stem_b": stem_b,
        "head_top_front": (0, head_front_y, d("head_top_h")),
        "head_top_rear": (0, head_front_y - d("head_len"), d("head_top_h") - d("head_len") * math.tan(math.radians(15))),
        "plate_top": plate_centre + Vector((0, 0, d("box_h") / 2)), "plate_bottom": plate_centre - Vector((0, 0, d("box_h") / 2)),
        "deck_front": (0, deck_front, d("deck_top_h")), "deck_rear": (0, deck_rear, d("deck_top_h")),
        "deck_skirt_bottom": (0, front.y - (1000 - 606) * PX, d("deck_top_h") - d("deck_thick")),
        "fender_top": (0, front.y - (1130 - 606) * PX, d("fender_top_h")),
        "fender_end": (0, fender_end, 0.208), "rear_light": (0, fender_end, 0.208),
    }.items():
        pl.landmark(name, loc)
    return parts


def main(argv):
    al.clear_scene()
    parts = build(pl.Spec(HERE / "spec.json"))
    if "--export" in argv:
        out = HERE / "out"
        pivots = {"body": (0, 0, 0), "wheel_front": tuple(Vector(pl.bpy.data.objects["LM_front_axle"].location)),
                  "wheel_rear": tuple(Vector(pl.bpy.data.objects["LM_rear_axle"].location))}
        pl.bake_shared_and_export(parts, pivots, str(out.resolve()), "VEH_ScooterVoi", res=1024, samples=32)
        return
    if "--preview" in argv:
        objs = [o for group in parts.values() for o in group]
        out = str(Path(argv[argv.index("--preview") + 1]).resolve())   # Blender resolves relative paths oddly
        al.render_previews(objs[0], out, extra_objects=objs[1:])


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
