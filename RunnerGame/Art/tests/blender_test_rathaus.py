"""Blender tests for the Rathaus build. Run from the repo root:
"C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" --background --factory-startup
    --python-exit-code 1 --python RunnerGame/Art/tests/blender_test_rathaus.py
"""
import importlib.util
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
        cls.parts = load_build().build(cls.spec)
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
        for name in ("drum", "dome", "lantern"):
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

    def test_triangle_budget(self):
        deps = bpy.context.evaluated_depsgraph_get()
        tris = 0
        for o in self.objs:
            me = o.evaluated_get(deps).to_mesh()
            me.calc_loop_triangles()
            tris += len(me.loop_triangles)
        print("TRIANGLES", tris)
        self.assertLessEqual(tris, 8000)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    if not result.wasSuccessful():
        raise SystemExit(1)
