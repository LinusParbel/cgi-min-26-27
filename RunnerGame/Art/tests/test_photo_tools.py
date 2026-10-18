"""Tests for photo_tools (system Python + Pillow). Run from the repo root:
python -m unittest discover -s RunnerGame/Art/tests -p "test_*.py" -v
"""
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import photo_tools as pt  # noqa: E402

BALE = "Trottinette électrique Voi Elsässerstrasse - Bâle.jpg"

API_FIXTURE = {
    "query": {
        "pages": {
            "-1": {
                "title": "File:" + BALE,
                "imageinfo": [{
                    "thumburl": "https://upload.wikimedia.org/thumb/bale.jpg",
                    "descriptionurl": "https://commons.wikimedia.org/wiki/File:Bale.jpg",
                    "extmetadata": {
                        "Artist": {"value": '<a href="//commons.wikimedia.org/wiki/User:Jane">Jane Doe</a>'},
                        "LicenseShortName": {"value": "CC BY-SA 4.0"},
                    },
                }],
            }
        }
    }
}


def jpeg_bytes(w, h, exif=None):
    buf = io.BytesIO()
    img = Image.new("RGB", (w, h), (200, 80, 60))
    if exif is not None:
        img.save(buf, "JPEG", exif=exif.tobytes())
    else:
        img.save(buf, "JPEG")
    return buf.getvalue()


class ParseImageinfoTest(unittest.TestCase):
    def test_parse_imageinfo_fields(self):
        [p] = pt.parse_imageinfo(API_FIXTURE)
        self.assertEqual(p["title"], BALE)
        self.assertEqual(p["author"], "Jane Doe")
        self.assertEqual(p["licence"], "CC BY-SA 4.0")
        self.assertEqual(p["source_url"], "https://commons.wikimedia.org/wiki/File:Bale.jpg")
        self.assertEqual(p["image_url"], "https://upload.wikimedia.org/thumb/bale.jpg")

    def test_parse_rate_limited(self):
        with self.assertRaises(pt.RateLimited):
            pt.parse_imageinfo({})


class FetchPackTest(unittest.TestCase):
    def test_fetch_retries_on_rate_limit(self):
        api_replies = [b"<html>Too many requests</html>", json.dumps(API_FIXTURE).encode("utf-8")]
        sleeps = []

        def fake_run(args, **kwargs):
            if "-o" in args:
                Path(args[args.index("-o") + 1]).write_bytes(jpeg_bytes(64, 48))
                return subprocess.CompletedProcess(args, 0, stdout=b"")
            return subprocess.CompletedProcess(args, 0, stdout=api_replies.pop(0))

        with tempfile.TemporaryDirectory() as d:
            photos = pt.fetch_pack(Path(d), ["File:" + BALE], run=fake_run, sleep=sleeps.append)
            refs = json.loads((Path(d) / "refs.json").read_text(encoding="utf-8"))
            self.assertTrue((Path(d) / "ref" / "01.jpg").exists())
        self.assertEqual(len(photos), 1)
        self.assertEqual(sleeps.count(60), 1)
        self.assertEqual(refs["photos"][0]["title"], BALE)
        self.assertEqual(refs["photos"][0]["file"], "ref/01.jpg")
        self.assertEqual(refs["photos"][0]["size"], [64, 48])


def two_page_fixture():
    api = json.loads(json.dumps(API_FIXTURE))
    page = json.loads(json.dumps(api["query"]["pages"]["-1"]))
    page["title"] = "File:Second.jpg"
    api["query"]["pages"]["-2"] = page
    return api


class FetchRobustnessTest(unittest.TestCase):
    def test_existing_titles_keep_their_file_names(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "refs.json").write_text(json.dumps({"photos": [
                {"file": "ref/17.jpg", "title": BALE, "view": "side_left", "key": True,
                 "landmarks": {"a": [1, 2]}, "camera": None}]}), encoding="utf-8")

            def fake_run(args, **kwargs):
                if "-o" in args:
                    Path(args[args.index("-o") + 1]).write_bytes(jpeg_bytes(64, 48))
                    return subprocess.CompletedProcess(args, 0, stdout=b"")
                return subprocess.CompletedProcess(args, 0, stdout=json.dumps(two_page_fixture()).encode())

            photos = pt.fetch_pack(Path(d), ["File:" + BALE, "File:Second.jpg"], run=fake_run, sleep=lambda s: None)
            files = {p["title"]: p["file"] for p in photos}
            self.assertEqual(files[BALE], "ref/17.jpg")
            self.assertEqual(files["Second.jpg"], "ref/18.jpg")
            self.assertEqual(photos[0]["landmarks"], {"a": [1, 2]})

    def test_download_retried_after_failure(self):
        sleeps, fails = [], [1]

        def fake_run(args, **kwargs):
            if "-o" in args:
                if fails:
                    fails.pop()
                    return subprocess.CompletedProcess(args, 22, stdout=b"")
                Path(args[args.index("-o") + 1]).write_bytes(jpeg_bytes(64, 48))
                return subprocess.CompletedProcess(args, 0, stdout=b"")
            return subprocess.CompletedProcess(args, 0, stdout=json.dumps(API_FIXTURE).encode())

        with tempfile.TemporaryDirectory() as d:
            pt.fetch_pack(Path(d), ["File:" + BALE], run=fake_run, sleep=sleeps.append)
            self.assertTrue((Path(d) / "ref" / "01.jpg").exists())
        self.assertIn(60, sleeps)

    def test_failed_download_leaves_old_pack_untouched(self):
        def fake_run(args, **kwargs):
            if "-o" in args:
                return subprocess.CompletedProcess(args, 22, stdout=b"")
            return subprocess.CompletedProcess(args, 0, stdout=json.dumps(two_page_fixture()).encode())

        with tempfile.TemporaryDirectory() as d:
            ref = Path(d) / "ref"
            ref.mkdir()
            (ref / "01.jpg").write_bytes(b"old")
            refs = json.dumps({"photos": [{"file": "ref/01.jpg", "title": BALE}]})
            (Path(d) / "refs.json").write_text(refs, encoding="utf-8")
            with self.assertRaises(RuntimeError):
                pt.fetch_pack(Path(d), ["File:" + BALE, "File:Second.jpg"], run=fake_run, sleep=lambda s: None)
            self.assertEqual((ref / "01.jpg").read_bytes(), b"old")
            self.assertEqual((Path(d) / "refs.json").read_text(encoding="utf-8"), refs)


class PartCropsTest(unittest.TestCase):
    def test_crops_per_part_and_photo(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "ref").mkdir()
            Image.new("RGB", (400, 300), (10, 20, 30)).save(d / "ref" / "01.jpg")
            Image.new("RGB", (300, 400), (40, 50, 60)).save(d / "ref" / "04.jpg")
            refs = {"photos": [
                {"file": "ref/01.jpg", "key": True, "sections": {"top": [10, 10, 110, 60], "legs": [0, 200, 200, 300]}},
                {"file": "ref/04.jpg", "key": True, "sections": {"top": [50, 0, 150, 100]}},
                {"file": "ref/09.jpg", "key": False, "sections": {"top": [0, 0, 10, 10]}}]}
            (d / "refs.json").write_text(json.dumps(refs), encoding="utf-8")
            written = pt.part_crops(d, scale=2)
            names = sorted(p.name for p in written)
            self.assertEqual(names, ["crop_legs_01.png", "crop_top_01.png", "crop_top_04.png"])
            with Image.open(d / "previews" / "crops" / "crop_top_01.png") as im:
                self.assertEqual(im.size, (200, 100))


class SaveNormalisedTest(unittest.TestCase):
    def test_save_normalised_exif_rotation(self):
        exif = Image.Exif()
        exif[0x0112] = 6  # rotate 90° clockwise when displayed
        with tempfile.TemporaryDirectory() as d:
            src, dst = Path(d) / "src.jpg", Path(d) / "dst.jpg"
            src.write_bytes(jpeg_bytes(200, 100, exif))
            self.assertEqual(pt.save_normalised(src, dst), (100, 200))
            with Image.open(dst) as out:
                self.assertEqual(out.size, (100, 200))
                self.assertIsNone(out.getexif().get(0x0112))

    def test_save_normalised_limits_long_side(self):
        with tempfile.TemporaryDirectory() as d:
            src, dst = Path(d) / "src.jpg", Path(d) / "dst.jpg"
            src.write_bytes(jpeg_bytes(1000, 2000))
            self.assertEqual(pt.save_normalised(src, dst, max_side=1600), (800, 1600))


class CreditsTest(unittest.TestCase):
    def test_credits_line_format(self):
        photo = {"file": "ref/01.jpg", "title": "Title", "author": "Author", "licence": "CC BY-SA 4.0",
                 "source_url": "https://commons.wikimedia.org/wiki/File:Title"}
        self.assertEqual(pt.credits_lines([photo]),
                         ['- ref/01.jpg: "Title" by Author, CC BY-SA 4.0, https://commons.wikimedia.org/wiki/File:Title'])


class GridTest(unittest.TestCase):
    def test_grid_positions(self):
        xs, ys = pt.grid_positions((100, 200, 500, 600), 50, 2.0)
        self.assertEqual(xs[0], (100, 0.0))
        self.assertIn((150, 100.0), xs)
        self.assertEqual(len(xs), 9)
        self.assertEqual(ys[0], (200, 0.0))
        self.assertEqual(len(ys), 9)

    def test_grid_image_size(self):
        with tempfile.TemporaryDirectory() as d:
            src, out = Path(d) / "src.jpg", Path(d) / "grid.png"
            src.write_bytes(jpeg_bytes(600, 400))
            pt.grid_image(src, out, crop=(100, 100, 300, 200), out_width=800)
            with Image.open(out) as im:
                self.assertEqual(im.size, (800, 400))


class ColorTest(unittest.TestCase):
    def test_sample_color_linear(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "grey.png"
            Image.new("RGB", (40, 40), (128, 128, 128)).save(src)
            for c in pt.sample_color(src, (5, 5, 30, 30)):
                self.assertAlmostEqual(c, 0.2158, delta=0.001)


class MeasureTest(unittest.TestCase):
    def test_measure_ruler(self):
        lm = {"a": [0, 0], "b": [254, 0], "c": [0, 0], "d": [0, 1000]}
        result = pt.measure(lm, ("a", "b", 0.254), {"x": ("c", "d")})
        self.assertAlmostEqual(result["x"], 1.0, delta=1e-6)


if __name__ == "__main__":
    unittest.main()
