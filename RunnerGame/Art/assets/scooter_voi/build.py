"""Voi-style e-scooter (2022 generation), built from spec.json.

Blender Z-up, metres. The scooter faces +Y; the origin is on the ground midway between the axles.
Rider's left = -X. Every number comes from spec.json; fix measurements there, never here.

Headless:  blender --background --factory-startup --python RunnerGame/Art/assets/scooter_voi/build.py -- [--preview out.png]
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
    mat = {name: al.flat(name, c(name)) for name in spec.colors}
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
    body(al.box("front_fender", (d("wheel_w") + 0.03, R * 1.4, 0.015), front + Vector((0, -0.01, R + 0.025)), mat["fender"]))

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
    head_centre = Vector((0, bar_y - d("head_len") / 2 + 0.03, d("head_top_h") - d("head_h") / 2))
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

    # rear fender hood over the top half of the rear wheel
    fender_end = deck_rear - d("rear_fender_len")
    body(al.box("rear_fender", (d("wheel_w") + 0.05, d("rear_fender_len"), d("fender_top_h") - R),
                (0, (deck_rear + fender_end) / 2, (d("fender_top_h") + R) / 2), mat["fender"], bevel=0.02))

    # landmarks (names match refs.json)
    head_front_y = head_centre.y + d("head_len") / 2
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
    if "--preview" in argv:
        objs = [o for group in parts.values() for o in group]
        out = str(Path(argv[argv.index("--preview") + 1]).resolve())   # Blender resolves relative paths oddly
        al.render_previews(objs[0], out, extra_objects=objs[1:])


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
