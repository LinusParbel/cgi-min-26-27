"""Photo helpers for the photo-to-model workflow (system Python + Pillow, never inside Blender).

Reference packs: fetch free-licensed photos from Wikimedia Commons into <asset_dir>/ref/ and keep their
licence data in <asset_dir>/refs.json. Downloads use curl because the system Python's certificate store
is outdated.

CLI (from the repo root):
    python RunnerGame/Art/lib/photo_tools.py fetch <asset_dir> <titles.txt>
    python RunnerGame/Art/lib/photo_tools.py sheet <asset_dir>
"""
import html
import json
import re
import subprocess
import sys
import time
import unicodedata
import urllib.parse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

API = "https://commons.wikimedia.org/w/api.php"
UA = "HannoverRushHour-student-project/0.1 (university course; low-volume reference lookup)"
KEEP_KEYS = ("view", "key", "landmarks", "camera")   # hand-made values that survive a re-fetch


class RateLimited(Exception):
    """Wikimedia answered with something other than an API result (usually a rate-limit page)."""


# ---------------------------------------------------------------- reference packs

def _norm_title(title):
    t = title[5:] if title.startswith("File:") else title
    return unicodedata.normalize("NFC", t.replace("_", " "))


def parse_imageinfo(api):
    """Turn an imageinfo API reply into one dict per photo (title without 'File:', HTML-free author)."""
    if "query" not in api:
        raise RateLimited(str(api)[:200])
    photos = []
    for page in api["query"].get("pages", {}).values():
        if "imageinfo" not in page:
            continue
        ii = page["imageinfo"][0]
        meta = ii.get("extmetadata", {})
        author = html.unescape(re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "unknown"))).strip()
        photos.append({
            "title": _norm_title(page["title"]),
            "author": author,
            "licence": meta.get("LicenseShortName", {}).get("value", "unknown"),
            "source_url": ii.get("descriptionurl", ""),
            "image_url": ii.get("thumburl") or ii.get("url", ""),
        })
    return photos


def save_normalised(src, dst, max_side=1600):
    """Apply the EXIF orientation (Blender ignores it), shrink to max_side and save without EXIF."""
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((max_side, max_side), Image.LANCZOS)
        im.save(dst, "JPEG", quality=90)
        return im.size


def _api_query(titles, width, run, sleep):
    params = {"action": "query", "format": "json", "prop": "imageinfo", "iiprop": "url|extmetadata",
              "iiextmetadatafilter": "Artist|LicenseShortName", "iiurlwidth": str(width),
              "titles": "|".join(titles)}
    # Percent-encode here so curl only ever sees ASCII (non-ASCII argv is unreliable on Windows).
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(3):
        out = run(["curl", "-s", "-A", UA, url], capture_output=True).stdout
        try:
            return parse_imageinfo(json.loads(out))
        except (ValueError, RateLimited):
            if attempt == 2:
                raise RateLimited("no API result after 3 attempts")
            print("rate limited, waiting 60 s", file=sys.stderr)
            sleep(60)


def fetch_pack(asset_dir, titles, width=1600, run=subprocess.run, sleep=time.sleep):
    """Download the given Commons titles to <asset_dir>/ref/NN.jpg and write refs.json."""
    asset_dir = Path(asset_dir)
    ref_dir = asset_dir / "ref"
    ref_dir.mkdir(parents=True, exist_ok=True)
    if len(titles) > 50:
        raise ValueError("the API takes at most 50 titles per request")
    found = {p["title"]: p for p in _api_query(titles, width, run, sleep)}
    missing = [t for t in titles if _norm_title(t) not in found]
    if missing:
        raise ValueError(f"not found on Commons: {missing}")

    refs_path = asset_dir / "refs.json"
    old = {}
    if refs_path.exists():
        old = {p["title"]: p for p in json.loads(refs_path.read_text(encoding="utf-8"))["photos"]}

    # Known titles keep their file name (spec.json, landmarks and commands refer to it); new ones get the next number.
    used = [int(p["file"][4:6]) for p in old.values() if re.fullmatch(r"ref/\d\d\.jpg", p.get("file", ""))]
    used += [int(f.stem) for f in ref_dir.glob("[0-9][0-9].jpg")]
    next_no = max(used, default=0) + 1

    # Download everything into a staging folder first, so a failure leaves the old pack untouched.
    stage = ref_dir / ".fetch"
    stage.mkdir(exist_ok=True)
    photos = []
    try:
        for title in titles:
            meta = found[_norm_title(title)]
            rel = old.get(meta["title"], {}).get("file")
            if not rel:
                rel, next_no = f"ref/{next_no:02d}.jpg", next_no + 1
            tmp = stage / (Path(rel).stem + ".download")
            for attempt in range(3):
                result = run(["curl", "-s", "-f", "-A", UA, "-o", str(tmp), meta["image_url"]], capture_output=True)
                if result.returncode == 0 and tmp.exists():
                    break
                if attempt == 2:
                    raise RuntimeError(f"download failed for {meta['title']}")
                print("download failed, waiting 60 s", file=sys.stderr)
                sleep(60)
            size = save_normalised(tmp, stage / Path(rel).name)
            tmp.unlink()
            photo = {"file": rel, "title": meta["title"], "author": meta["author"], "licence": meta["licence"],
                     "source_url": meta["source_url"], "size": list(size),
                     "view": None, "key": False, "landmarks": {}, "camera": None}
            for k in KEEP_KEYS:
                if k in old.get(meta["title"], {}):
                    photo[k] = old[meta["title"]][k]
            photos.append(photo)
            print(f"{rel}  {size[0]}x{size[1]}  {meta['licence']}  {meta['title']}")
            sleep(1)
        for p in photos:
            (stage / Path(p["file"]).name).replace(asset_dir / p["file"])
    finally:
        for f in stage.iterdir():
            f.unlink()
        stage.rmdir()

    refs_path.write_text(json.dumps({"photos": photos}, indent=1, ensure_ascii=False), encoding="utf-8")
    return photos


def load_refs(asset_dir):
    return json.loads((Path(asset_dir) / "refs.json").read_text(encoding="utf-8"))


def contact_sheet(asset_dir, out, cell=320, cols=4):
    """Numbered thumbnails of all reference photos, labelled with their view tag (* = key photo)."""
    asset_dir = Path(asset_dir)
    photos = load_refs(asset_dir)["photos"]
    rows = (len(photos) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell, rows * cell), "white")
    draw = ImageDraw.Draw(sheet)
    for i, p in enumerate(photos):
        with Image.open(asset_dir / p["file"]) as im:
            im.thumbnail((cell - 8, cell - 24))
            x, y = (i % cols) * cell, (i // cols) * cell
            sheet.paste(im, (x + 4, y + 20))
        label = f"{Path(p['file']).stem}  {p.get('view') or '?'}{' *' if p.get('key') else ''}"
        draw.text((x + 4, y + 4), label, fill="red")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=88)


def credits_lines(photos):
    return [f'- {p["file"]}: "{p["title"]}" by {p["author"]}, {p["licence"]}, {p["source_url"]}' for p in photos]


# ---------------------------------------------------------------- reading photos

def grid_positions(crop, step, scale):
    """(source px, output px) of every grid line inside the crop; source values are multiples of step."""
    x0, y0, x1, y1 = crop

    def lines(lo, hi):
        first = -(-lo // step) * step
        return [(s, (s - lo) * scale) for s in range(first, hi + 1, step)]

    return lines(x0, x1), lines(y0, y1)


def grid_image(src, out, crop=None, step=50, out_width=1200):
    """Crop + scale a photo and draw a grid labelled in SOURCE pixels, so points can be read off it."""
    with Image.open(src) as im:
        crop = crop or (0, 0, im.width, im.height)
        scale = out_width / (crop[2] - crop[0])
        img = im.convert("RGB").crop(crop).resize((out_width, round((crop[3] - crop[1]) * scale)), Image.LANCZOS)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=13)
    xs, ys = grid_positions(crop, step, scale)
    for vertical, positions in ((True, xs), (False, ys)):
        for s, o in positions:
            strong = s % (5 * step) == 0
            colour = (255, 255, 0) if strong else (0, 255, 255)
            line = [(o, 0), (o, img.height)] if vertical else [(0, o), (img.width, o)]
            draw.line(line, fill=colour, width=2 if strong else 1)
            pos = (o + 2, 2) if vertical else (2, o + 2)
            box = draw.textbbox(pos, str(s), font=font)
            draw.rectangle(box, fill=(0, 0, 0))
            draw.text(pos, str(s), fill=colour, font=font)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    img.save(out)


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def sample_color(src, box):
    """Median colour of a photo region (x0, y0, x1, y1), returned as linear RGB for Blender materials."""
    with Image.open(src) as im:
        region = im.convert("RGB").crop(box)
    channels = list(zip(*region.getdata()))
    medians = [sorted(ch)[len(ch) // 2] / 255 for ch in channels]
    return tuple(round(srgb_to_linear(c), 4) for c in medians)


def measure(landmarks, ruler, pairs):
    """Distances in metres between named landmark pixels, scaled by a ruler (name_a, name_b, metres)."""
    def dist(a, b):
        (ax, ay), (bx, by) = landmarks[a], landmarks[b]
        return ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5

    m_per_px = ruler[2] / dist(ruler[0], ruler[1])
    return {name: dist(a, b) * m_per_px for name, (a, b) in pairs.items()}


# ---------------------------------------------------------------- CLI

def _box(text):
    return tuple(int(v) for v in text.split(","))


def main(argv):
    sys.stdout.reconfigure(errors="replace")   # Commons titles may not fit the console code page
    cmd = argv[0]
    if cmd == "grid":
        crop = _box(argv[argv.index("--crop") + 1]) if "--crop" in argv else None
        step = int(argv[argv.index("--step") + 1]) if "--step" in argv else 50
        grid_image(argv[1], argv[2], crop=crop, step=step)
        print("grid", argv[2])
    elif cmd == "color":
        print("linear", list(sample_color(argv[1], _box(argv[2]))))
    elif cmd == "measure":
        asset_dir, photo_file, pairs_file = Path(argv[1]), argv[2], Path(argv[3])
        photo = next(p for p in load_refs(asset_dir)["photos"] if p["file"] == photo_file)
        spec = json.loads(pairs_file.read_text(encoding="utf-8"))
        for name, metres in measure(photo["landmarks"], tuple(spec["ruler"]), spec["pairs"]).items():
            print(f"{name:20s} {metres:.3f} m")
    elif cmd == "fetch":
        asset_dir, titles_file = Path(argv[1]), Path(argv[2])
        titles = [t.strip() for t in titles_file.read_text(encoding="utf-8").splitlines() if t.strip()]
        fetch_pack(asset_dir, titles)
    elif cmd == "sheet":
        out = Path(argv[1]) / "previews" / "ref_sheet.jpg"
        contact_sheet(argv[1], out)
        print("sheet", out)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
