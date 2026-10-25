"""Blender tests for photo_lib's camera match and comparison images. Run from the repo root:
"C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" --background --factory-startup
    --python-exit-code 1 --python RunnerGame/Art/tests/blender_test_photo_lib.py
"""
import sys
import tempfile
import unittest
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import geom_probe  # noqa: E402
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

    def test_fit_respects_height_range(self):
        photo_lib.al.clear_scene()
        for name, loc in {"a": (0, 0, 0), "b": (0.5, 0.2, 0.1), "c": (-0.3, 0.4, 0.9), "d": (0.2, -0.5, 0.5),
                          "e": (-0.4, -0.3, 0.2), "f": (0.1, 0.6, 1.1)}.items():
            photo_lib.landmark(name, loc)
        true = {"loc": [-1.2, -2.0, -0.6], "look_at": [0, 0, 0.5], "lens_mm": 30, "roll_deg": 0}
        target = photo_lib.project_landmarks(photo_lib.match_camera((1200, 900), true))
        start = {"loc": [-1.0, -2.4, 1.1], "look_at": [0.1, 0.1, 0.4], "lens_mm": 26, "roll_deg": 0}
        cam, _ = photo_lib.fit_camera((1200, 900), start, {k: list(v) for k, v in target.items()}, z_range=(0.0, 3.0))
        self.assertGreaterEqual(cam["loc"][2], 0.0)
        self.assertLessEqual(cam["loc"][2], 3.0)


class LensShiftTest(unittest.TestCase):
    def test_projection_with_shift_matches_blender(self):
        scene_with_landmarks()
        cam = {"loc": [0.3, -5, 1.6], "look_at": [0.3, 0, 1.6], "lens_mm": 24, "roll_deg": 0, "shift_x": 0.05, "shift_y": 0.1}
        size = (1000, 1500)
        blender = photo_lib.project_landmarks(photo_lib.match_camera(size, cam))
        unshifted = photo_lib.project_landmarks(photo_lib.match_camera(size, {**cam, "shift_x": 0, "shift_y": 0}))
        self.assertAlmostEqual(blender["o"][1] - unshifted["o"][1], 0.1 * 1500, delta=1.0)   # shift_y up -> image moves down
        self.assertAlmostEqual(blender["o"][0] - unshifted["o"][0], -0.05 * 1500, delta=1.0)
        names = ["o", "x"]
        pts = np.array([bpy.data.objects["LM_" + n].matrix_world.translation for n in names])
        vec = np.array([*cam["loc"], *cam["look_at"], cam["lens_mm"], cam["roll_deg"], cam["shift_x"], cam["shift_y"]])
        px, py = photo_lib._project_np(vec, pts, size)
        for i, n in enumerate(names):
            self.assertAlmostEqual(px[i], blender[n][0], delta=0.5)
            self.assertAlmostEqual(py[i], blender[n][1], delta=0.5)

    def test_fit_recovers_shifted_level_camera(self):
        photo_lib.al.clear_scene()
        for name, loc in {"a": (0, 0, 0), "b": (0.5, 0.2, 0.1), "c": (-0.3, 0.4, 2.9), "d": (0.2, -0.5, 1.5),
                          "e": (-0.4, -0.3, 0.2), "f": (0.1, 0.6, 3.6), "g": (0.5, 0.0, 3.0)}.items():
            photo_lib.landmark(name, loc)
        true = {"loc": [0.4, -6.0, 1.6], "look_at": [0.4, 0.0, 1.6], "lens_mm": 24, "roll_deg": 0, "shift_x": 0.0, "shift_y": 0.25}
        target = photo_lib.project_landmarks(photo_lib.match_camera((1000, 1500), true))
        start = {"loc": [0.0, -7.0, 1.5], "look_at": [0.0, 0.0, 1.8], "lens_mm": 30, "roll_deg": 0}
        cam, rms = photo_lib.fit_camera((1000, 1500), start, {k: list(v) for k, v in target.items()},
                                        z_range=(1.0, 2.0), shift=True)
        self.assertLess(rms, 1.0)
        self.assertGreater(cam["shift_y"], 0.1)

    def test_level_fit_keeps_the_view_horizontal(self):
        photo_lib.al.clear_scene()
        for name, loc in {"a": (0, 0, 0), "b": (0.5, 0.2, 0.1), "c": (-0.3, 0.4, 2.9), "d": (0.2, -0.5, 1.5),
                          "e": (-0.4, -0.3, 0.2), "f": (0.1, 0.6, 3.6), "g": (0.5, 0.0, 3.0)}.items():
            photo_lib.landmark(name, loc)
        true = {"loc": [0.4, -6.0, 1.6], "look_at": [0.4, 0.0, 1.6], "lens_mm": 24, "roll_deg": 0, "shift_x": 0.0, "shift_y": 0.25}
        target = photo_lib.project_landmarks(photo_lib.match_camera((1000, 1500), true))
        start = {"loc": [0.0, -7.0, 1.5], "look_at": [0.0, 0.0, 1.0], "lens_mm": 30, "roll_deg": 0}
        cam, rms = photo_lib.fit_camera((1000, 1500), start, {k: list(v) for k, v in target.items()},
                                        z_range=(1.0, 2.0), shift=True, level=True)
        self.assertAlmostEqual(cam["look_at"][2], cam["loc"][2], delta=1e-6)
        self.assertEqual(cam["roll_deg"], 0.0)
        self.assertLess(rms, 1.0)


class PartSheetTest(unittest.TestCase):
    def test_part_sheet_has_one_row_per_photo(self):
        scene_with_landmarks()
        photo_lib.al.box("cube", (1, 1, 1), (0, 0, 0), None)
        with tempfile.TemporaryDirectory() as d:
            photos = []
            for i, (w, h) in enumerate(((300, 200), (200, 300))):
                path = str(Path(d) / f"p{i}.png")
                img = bpy.data.images.new(f"__p{i}", w, h)
                img.pixels[:] = [0.5] * (w * h * 4)
                img.filepath_raw = path
                img.file_format = 'PNG'
                img.save()
                photos.append((path, CAM, (0, 0, 100, 50), {"o": [w / 2, h / 2]}))
            out = str(Path(d) / "part.png")
            photo_lib.part_sheet(photos, out)
            sheet = bpy.data.images.load(out)
            self.assertEqual(sheet.size[1], 2 * photo_lib.SECTION_ROW_H)
            self.assertEqual(sheet.size[0], 3 * 2 * photo_lib.SECTION_ROW_H)


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
            blend = bpy.data.images.load(str(Path(d) / "compare_blend.png"))
            self.assertEqual(tuple(blend.size), tuple(overlay.size))
            out2 = str(Path(d) / "zoomed.png")
            photo_lib.compare_image(photo, CAM, out2, {"o": [150, 100]}, zoom=(10, 20, 110, 70))
            z = bpy.data.images.load(str(Path(d) / "zoomed_blend_zoom.png"))
            self.assertEqual(tuple(z.size), (100, 50))
            out3 = str(Path(d) / "sec.png")
            photo_lib.compare_image(photo, CAM, out3, {"o": [150, 100]},
                                    sections=[("a", (0, 0, 100, 50)), ("b", (100, 100, 300, 200))])
            sheet = bpy.data.images.load(str(Path(d) / "sec_sections.png"))
            self.assertEqual(sheet.size[1], 2 * photo_lib.SECTION_ROW_H)       # one row per section
            self.assertEqual(sheet.size[0], 3 * 2 * photo_lib.SECTION_ROW_H)    # widest row: 3 panels of a 2:1 section



class GeomProbeTest(unittest.TestCase):
    def setUp(self):
        photo_lib.al.clear_scene()
        bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))      # x,y in [-1, 1], z in [0, 2]
        self.parts = {"cube": [bpy.context.object]}

    def test_counts_and_slice(self):
        self.assertEqual(geom_probe.tri_count(self.parts), 12)
        self.assertAlmostEqual(geom_probe.width_at(self.parts, 1.0), 2.0, delta=1e-6)
        self.assertEqual(geom_probe.bounds(self.parts)[1][2], 2.0)

    def test_ray_hits_surface_and_misses_gap(self):
        hit = geom_probe.ray_hit((0, -5, 1), (0, 1, 0))
        self.assertAlmostEqual(hit.y, -1.0, delta=1e-6)
        self.assertIsNone(geom_probe.ray_hit((3, -5, 1), (0, 1, 0)))

    def test_fingerprint_changes_with_geometry(self):
        before = geom_probe.fingerprint(self.parts)
        self.parts["cube"][0].data.vertices[0].co.x -= 0.1
        self.assertNotEqual(before, geom_probe.fingerprint(self.parts))


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    if not result.wasSuccessful():
        raise SystemExit(1)
