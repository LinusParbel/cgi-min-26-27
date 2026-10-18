"""Blender tests for photo_lib's camera match and comparison images. Run from the repo root:
"C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" --background --factory-startup
    --python-exit-code 1 --python RunnerGame/Art/tests/blender_test_photo_lib.py
"""
import sys
import tempfile
import unittest
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import photo_lib  # noqa: E402

CAM = {"loc": [0, -5, 0], "look_at": [0, 0, 0], "lens_mm": 50, "roll_deg": 0}


def scene_with_landmarks():
    photo_lib.al.clear_scene()
    for o in [o for o in bpy.data.objects if o.name.startswith("LM_")]:
        bpy.data.objects.remove(o)
    photo_lib.landmark("o", (0, 0, 0))
    photo_lib.landmark("x", (0.5, 0, 0))
    photo_lib.landmark("far", (50, 0, 0))


class ProjectionTest(unittest.TestCase):
    def setUp(self):
        scene_with_landmarks()

    def test_projection_centre_and_offset(self):
        p = photo_lib.project_landmarks(photo_lib.match_camera((1000, 1000), CAM))
        self.assertAlmostEqual(p["o"][0], 500, delta=0.5)
        self.assertAlmostEqual(p["o"][1], 500, delta=0.5)
        self.assertAlmostEqual(p["x"][0], 638.9, delta=0.5)
        self.assertAlmostEqual(p["x"][1], 500, delta=0.5)

    def test_projection_portrait(self):
        p = photo_lib.project_landmarks(photo_lib.match_camera((1000, 1500), CAM))
        self.assertAlmostEqual(p["o"][0], 500, delta=0.5)
        self.assertAlmostEqual(p["o"][1], 750, delta=0.5)
        self.assertGreater(p["x"][0], 500)
        self.assertAlmostEqual(p["x"][1], 750, delta=0.5)

    def test_off_frame_is_none(self):
        p = photo_lib.project_landmarks(photo_lib.match_camera((1000, 1000), CAM))
        self.assertIsNone(p["far"])
        errors, rms = photo_lib.landmark_errors(p, {"far": [10, 10], "o": [500, 500]})
        self.assertNotIn("far", errors)
        self.assertAlmostEqual(rms, 0.0, delta=0.5)


class FitCameraTest(unittest.TestCase):
    def test_fit_recovers_camera(self):
        photo_lib.al.clear_scene()
        for name, loc in {"a": (0, 0, 0), "b": (0.5, 0.2, 0.1), "c": (-0.3, 0.4, 0.9), "d": (0.2, -0.5, 0.5),
                          "e": (-0.4, -0.3, 0.2), "f": (0.1, 0.6, 1.1)}.items():
            photo_lib.landmark(name, loc)
        true = {"loc": [-1.2, -2.0, 1.4], "look_at": [0, 0, 0.5], "lens_mm": 30, "roll_deg": 0}
        target = photo_lib.project_landmarks(photo_lib.match_camera((1200, 900), true))
        start = {"loc": [-1.0, -2.4, 1.1], "look_at": [0.1, 0.1, 0.4], "lens_mm": 26, "roll_deg": 0}
        cam, rms = photo_lib.fit_camera((1200, 900), start, {k: list(v) for k, v in target.items()})
        self.assertLess(rms, 1.0)


class ErrorsTest(unittest.TestCase):
    def test_errors_rms(self):
        errors, rms = photo_lib.landmark_errors({"a": (0, 0), "b": (3, 4)}, {"a": [0, 0], "b": [0, 0]})
        self.assertEqual(errors, {"a": 0.0, "b": 5.0})
        self.assertAlmostEqual(rms, 3.5355, delta=1e-3)

    def test_no_pairs_gives_none(self):
        self.assertEqual(photo_lib.landmark_errors({"a": (0, 0)}, {}), ({}, None))


class CompareImageTest(unittest.TestCase):
    def test_compare_image_size(self):
        scene_with_landmarks()
        photo_lib.al.box("cube", (1, 1, 1), (0, 0, 0), None)
        with tempfile.TemporaryDirectory() as d:
            photo = str(Path(d) / "photo.png")
            img = bpy.data.images.new("__test_photo", 300, 200)
            img.pixels[:] = [0.5] * (300 * 200 * 4)
            img.filepath_raw = photo
            img.file_format = 'PNG'
            img.save()
            out = str(Path(d) / "compare.png")
            rms = photo_lib.compare_image(photo, CAM, out, {"o": [150, 100]})
            result = bpy.data.images.load(out)
            self.assertEqual(tuple(result.size), (900, 200))
            self.assertIsNotNone(rms)
            overlay = bpy.data.images.load(str(Path(d) / "compare_overlay.png"))
            self.assertLessEqual(max(overlay.size), 1000)
            self.assertLessEqual(overlay.size[0], 300)   # cropped to the model, never wider than the photo


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    if not result.wasSuccessful():
        raise SystemExit(1)
