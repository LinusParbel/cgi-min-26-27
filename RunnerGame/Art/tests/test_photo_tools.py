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


if __name__ == "__main__":
    unittest.main()
