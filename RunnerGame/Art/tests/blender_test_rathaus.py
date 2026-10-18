"""Blender tests for the Rathaus build. Run from the repo root:
"C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" --background --factory-startup
    --python-exit-code 1 --python RunnerGame/Art/tests/blender_test_rathaus.py
"""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

import bpy

ART = Path(__file__).resolve().parents[1]
ASSET = ART / "assets" / "rathaus_hannover"
sys.path.insert(0, str(ART / "lib"))
import photo_lib  # noqa: E402


def load_build():
    spec = importlib.util.spec_from_file_location("rathaus_build", ASSET / "build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def lm(name):
    return bpy.data.objects["LM_" + name].matrix_world.translation


class RathausBuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        photo_lib.al.clear_scene()
        cls.spec = photo_lib.Spec(ASSET / "spec.json")
        cls.module = load_build()
        cls.parts = cls.module.build(cls.spec)
        cls.objs = [o for objs in cls.parts.values() for o in objs]

    def test_one_part(self):
        self.assertEqual(set(self.parts), {"body"})

    def test_facade_width(self):
        self.assertAlmostEqual((lm("facade_left_base") - lm("facade_right_base")).length, self.spec.d("width"), delta=0.01)

    def test_spire_height(self):
        self.assertAlmostEqual(lm("spire_tip").z, self.spec.d("spire_tip_h"), delta=0.05)

    def test_stands_on_ground(self):
        lowest = min((o.matrix_world @ v.co).z for o in self.objs for v in o.data.vertices)
        self.assertAlmostEqual(lowest, 0.0, delta=0.01)

    def test_faces_minus_y(self):
        self.assertLess(lm("facade_left_base").y, 0)
        self.assertLess(lm("facade_right_base").y, 0)

    def test_dome_group_faces_point_outward(self):
        axis = (0.0, self.spec.d("dome_y"))
        for name in ("dome", "dome_cap"):
            me = bpy.data.objects[name].data
            checked = 0
            for p in me.polygons:
                if abs(p.normal.z) > 0.99:
                    continue                                   # flat caps
                dx, dy = p.center.x - axis[0], p.center.y - axis[1]
                if dx * dx + dy * dy < 1e-4:
                    continue
                checked += 1
                self.assertGreater(p.normal.x * dx + p.normal.y * dy, 0, f"{name} face {p.index} points inward")
            self.assertGreater(checked, 0, name)

    def test_all_ref01_landmarks_exist(self):
        refs = json.loads((ASSET / "refs.json").read_text(encoding="utf-8"))
        names = next(p for p in refs["photos"] if p["file"] == "ref/01.jpg")["landmarks"]
        missing = [n for n in names if "LM_" + n not in bpy.data.objects]
        self.assertEqual(missing, [])
        for n in names:                                        # all on the front (-Y) side
            self.assertLessEqual(lm(n).y, self.spec.d("dome_y") + 1e-6, n)

    def test_towers_and_dome_symmetric(self):
        for a, b in (("tower_l_tip", "tower_r_tip"), ("pav_l_gable", "pav_r_gable"), ("center_corner_l", "center_corner_r")):
            self.assertAlmostEqual(lm(a).x, -lm(b).x, delta=0.01)
            self.assertAlmostEqual(lm(a).z, lm(b).z, delta=0.01)

    def test_front_window_count_matches_front_layout(self):
        fl = self.spec.d("front_layout")
        bays = [x for x in fl["central_bays"]["x"]]
        bay_xs = {round(x, 2) for x in bays} | {round(-x, 2) for x in bays}
        n = len(bay_xs) * (2 + len(fl["central_bays"]["attic_windows"]["dx"]))   # entrance, big window, attics

        def mirrored(xs):
            return len({round(x, 2) for x in xs} | {round(-x, 2) for x in xs})
        mw = fl["middle_wing"]
        n += mirrored(mw["x"]) * (len(mw["rows"]) + 1)                           # rows + dormer window
        for key in ("tower_body", "wing_end", "pavilion"):
            n += mirrored(fl[key]["x"]) * len(fl[key]["rows"])
        n += 2                                                                   # pavilion gable windows
        self.assertEqual(len(self.module.FRONT_OPENINGS), n)

    def test_tracery_windows_at_layout_x(self):
        fl = self.spec.d("front_layout")["central_bays"]
        expect = sorted({round(x, 2) for x in fl["x"]} | {round(-x, 2) for x in fl["x"]})
        got = sorted(o["x"] for o in self.module.FRONT_OPENINGS if o["shape"] == "tracery")
        self.assertEqual(len(got), len(expect))
        for g, e in zip(got, expect):
            self.assertAlmostEqual(g, e, delta=0.05)

    def test_dome_base_pediment_is_small(self):
        dd = self.spec.d("domebase_detail")
        fz = self.spec.d("dome_y") - self.spec.d("domebase_w") / 2
        xs = [(o.matrix_world @ v.co).x for o in self.objs for v in o.data.vertices
              if dd["frontispiece"]["z1"] - 0.01 <= (o.matrix_world @ v.co).z <= dd["pediment"]["z1"] + 0.01
              and (o.matrix_world @ v.co).y < fz + 0.1 and abs((o.matrix_world @ v.co).x) < 20]
        self.assertGreater(len(xs), 0)
        self.assertLessEqual(max(xs) - min(xs), dd["frontispiece"]["w"] + 0.5)

    def test_corner_tower_roof_flares(self):
        ctd = self.spec.d("corner_tower_detail")
        tx = self.spec.d("tower_x")
        prof = ctd["roof"]["profile"]

        def width(z):
            xs = [(o.matrix_world @ v.co).x for o in self.objs if o.name == "copper" for v in o.data.vertices
                  if abs((o.matrix_world @ v.co).z - z) < 0.02 and abs((o.matrix_world @ v.co).x + tx) < 6]
            self.assertGreater(len(xs), 0, z)
            return max(xs) - min(xs)
        base, top = width(prof[0][0]), width(prof[-1][0])
        self.assertGreater(base, top + 2.0)
        mid = width(prof[2][0])                                # concave: narrower than the straight line base-top
        lin = base + (top - base) * (prof[2][0] - prof[0][0]) / (prof[-1][0] - prof[0][0])
        self.assertLess(mid, lin)

    def test_triangle_budget(self):
        deps = bpy.context.evaluated_depsgraph_get()
        tris = 0
        for o in self.objs:
            me = o.evaluated_get(deps).to_mesh()
            me.calc_loop_triangles()
            tris += len(me.loop_triangles)
        print("TRIANGLES", tris)
        self.assertLessEqual(tris, self.spec.d("tri_budget"))


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    if not result.wasSuccessful():
        raise SystemExit(1)
