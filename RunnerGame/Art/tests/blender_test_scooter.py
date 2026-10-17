"""Blender tests for the scooter build. Run from the repo root:
"C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" --background --factory-startup
    --python-exit-code 1 --python RunnerGame/Art/tests/blender_test_scooter.py
"""
import importlib.util
import sys
import unittest
from pathlib import Path

import bpy

ART = Path(__file__).resolve().parents[1]
ASSET = ART / "assets" / "scooter_voi"
sys.path.insert(0, str(ART / "lib"))
import photo_lib  # noqa: E402


def load_build():
    spec = importlib.util.spec_from_file_location("scooter_build", ASSET / "build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def lm(name):
    return bpy.data.objects["LM_" + name].matrix_world.translation


class ScooterBuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        photo_lib.al.clear_scene()
        cls.spec = photo_lib.Spec(ASSET / "spec.json")
        cls.parts = load_build().build(cls.spec)

    def test_parts(self):
        self.assertEqual(set(self.parts), {"body", "wheel_front", "wheel_rear"})
        for objs in self.parts.values():
            self.assertTrue(objs)

    def test_wheelbase(self):
        self.assertAlmostEqual((lm("front_axle") - lm("rear_axle")).length, self.spec.d("wheelbase"), delta=0.001)

    def test_faces_plus_y(self):
        self.assertGreater(lm("front_axle").y, 0)

    def test_bar_height(self):
        self.assertAlmostEqual((lm("bar_left").z + lm("bar_right").z) / 2, self.spec.d("bar_h"), delta=0.01)

    def test_bar_width(self):
        self.assertAlmostEqual(abs(lm("bar_left").x - lm("bar_right").x), self.spec.d("bar_w"), delta=0.005)

    def test_stands_on_ground(self):
        lowest = min((o.matrix_world @ v.co).z for objs in self.parts.values() for o in objs
                     if o.type == 'MESH' for v in o.data.vertices)
        self.assertAlmostEqual(lowest, 0.0, delta=0.002)


class TubeTest(unittest.TestCase):
    def test_tube_spans_its_end_points(self):
        o = photo_lib.tube("__t", (0.1, 0.2, 0.0), (0.1, 0.5, 0.4), 0.02, None)
        ends = [o.matrix_world @ v.co for v in o.data.vertices]
        self.assertAlmostEqual(min(v.z for v in ends), 0.0, delta=0.021)
        self.assertAlmostEqual(max(v.z for v in ends), 0.4, delta=0.021)
        self.assertAlmostEqual(sum(v.y for v in ends) / len(ends), 0.35, delta=0.001)
        bpy.data.objects.remove(o)


class SpecTest(unittest.TestCase):
    def test_missing_key_names_it(self):
        spec = photo_lib.Spec(ASSET / "spec.json")
        with self.assertRaisesRegex(KeyError, "no_such_dim"):
            spec.d("no_such_dim")


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    if not result.wasSuccessful():
        raise SystemExit(1)
