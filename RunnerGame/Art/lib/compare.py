"""Build an asset and compare it with one reference photo (one round of the comparison loop).

blender --background --factory-startup --python RunnerGame/Art/lib/compare.py -- <asset_dir> <ref/NN.jpg> [--fit] [--zoom x0,y0,x1,y1] [--sections]
blender ... --python RunnerGame/Art/lib/compare.py -- <asset_dir> --part <name>   # one part, all key photos, one image

--sections writes ONE sheet (<out>_sections.png) with a row per entry of the photo's "sections" in refs.json
({"name": [x0, y0, x1, y1]}): photo | model in colour | 50/50 blend, each at 320 px height.

blender ... --python RunnerGame/Art/lib/compare.py -- <asset_dir> <ref/NN.jpg> --errors [--starts]   # numbers only: signed landmark errors, no image

--fit first fits the camera (with lens shift if the photo has "lens_shift": true) to the photo's landmarks (numerically, no images) and saves it to refs.json.

Reads the photo's "camera" and "landmarks" from <asset_dir>/refs.json, imports <asset_dir>/build.py,
writes <asset_dir>/previews/compare_<NN>_r<round>.png and prints the landmark errors.
"""
import importlib.util
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import photo_lib as pl  # noqa: E402


def part_main(asset_dir, name):
    """--part NAME: build once, render that part in every key photo that has it, one stacked image."""
    refs = json.loads((asset_dir / "refs.json").read_text(encoding="utf-8"))
    spec = importlib.util.spec_from_file_location("asset_build", asset_dir / "build.py")
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    pl.al.clear_scene()
    build.build(pl.Spec(asset_dir / "spec.json"))
    photos = [(str(asset_dir / p["file"]), p["camera"], p["sections"][name], p.get("landmarks", {}))
              for p in refs["photos"] if p.get("key") and p.get("camera") and name in p.get("sections", {})]
    if not photos:
        raise SystemExit(f"no key photo with a camera has a section '{name}'")
    previews = asset_dir / "previews"
    previews.mkdir(exist_ok=True)
    rnd = 1
    while (previews / f"part_{name}_r{rnd}.png").exists():
        rnd += 1
    out = previews / f"part_{name}_r{rnd}.png"
    pl.part_sheet(photos, str(out))
    print("wrote", out)


def errors_main(asset_dir, photo_file, starts):
    """--errors [--starts]: numbers only, no image. Fits the camera (level + shift for shift photos) and prints the
    SIGNED landmark errors (model minus photo, px; +dx = model too far right, +dy = model too low), worst first.
    --starts tries a grid of start cameras around the model (use when a fit lands on a far telephoto)."""
    refs = json.loads((asset_dir / "refs.json").read_text(encoding="utf-8"))
    photo = next(p for p in refs["photos"] if p["file"] == photo_file)
    spec = importlib.util.spec_from_file_location("asset_build", asset_dir / "build.py")
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    pl.al.clear_scene()
    build.build(pl.Spec(asset_dir / "spec.json"))
    size, marks = tuple(photo["size"]), photo["landmarks"]
    z_range = tuple(photo["camera_z_range"]) if photo.get("camera_z_range") else None
    shift = bool(photo.get("lens_shift"))
    starts_list = [photo["camera"]] if photo.get("camera") and not starts else []
    if starts:
        lms = [bpy_obj.matrix_world.translation for n in marks if (bpy_obj := pl.bpy.data.objects.get("LM_" + n))]
        centre = [sum(v[i] for v in lms) / len(lms) for i in range(3)]
        height = sum(z_range) / 2 if z_range else 1.6
        for dist in (5, 8, 12):
            for ang in (0, 45):
                for lens in (28, 50):
                    a = math.radians(ang)
                    starts_list.append({"loc": [centre[0] + dist * math.sin(a), centre[1] - dist * math.cos(a), height],
                                        "look_at": centre, "lens_mm": lens, "roll_deg": 0})
    best = None
    for cam0 in starts_list:
        cam, rms = pl.fit_camera(size, cam0, marks, z_range=z_range, shift=shift, level=shift)
        if rms is not None and (best is None or rms < best[1]):
            best = (cam, rms)
    if best is None:
        raise SystemExit("no fit (landmarks off frame?)")
    cam, rms = best
    print("CAM", json.dumps(cam), f"RMS {rms:.1f} px ({100 * rms / size[0]:.2f} % of width)")
    proj = pl.project_landmarks(pl.match_camera(size, cam))
    rows = [(n, proj[n][0] - x, proj[n][1] - y) for n, (x, y) in marks.items() if proj.get(n)]
    for n, dx, dy in sorted(rows, key=lambda r: -(r[1] ** 2 + r[2] ** 2)):
        print(f"ERR {n:24s} dx {dx:+6.1f}  dy {dy:+6.1f}")
    if starts:
        print("copy CAM into refs.json (or rerun with --fit) if it is plausible")


def main(argv):
    if argv[1] == "--part":
        return part_main(Path(argv[0]).resolve(), argv[2])
    if "--errors" in argv:
        return errors_main(Path(argv[0]).resolve(), argv[1], "--starts" in argv)
    asset_dir, photo_file = Path(argv[0]).resolve(), argv[1]
    refs = json.loads((asset_dir / "refs.json").read_text(encoding="utf-8"))
    photo = next((p for p in refs["photos"] if p["file"] == photo_file), None)
    if photo is None:
        raise SystemExit(f"{photo_file} is not in refs.json (files: {[p['file'] for p in refs['photos']]})")
    if not photo.get("camera"):
        raise SystemExit(f"{photo_file} has no 'camera' in refs.json yet")

    spec = importlib.util.spec_from_file_location("asset_build", asset_dir / "build.py")
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    pl.al.clear_scene()
    build.build(pl.Spec(asset_dir / "spec.json"))

    if "--fit" in argv:
        cam, fit_rms = pl.fit_camera(tuple(photo["size"]), photo["camera"], photo["landmarks"],
                                     z_range=tuple(photo["camera_z_range"]) if photo.get("camera_z_range") else None,
                                     shift=bool(photo.get("lens_shift")), level=bool(photo.get("lens_shift")))
        photo["camera"] = cam
        (asset_dir / "refs.json").write_text(json.dumps(refs, indent=1, ensure_ascii=False), encoding="utf-8")
        print("fitted camera", cam, f"RMS {fit_rms:.1f} px")

    stem = Path(photo_file).stem
    previews = asset_dir / "previews"
    previews.mkdir(exist_ok=True)
    rnd = 1
    while (previews / f"compare_{stem}_r{rnd}.png").exists():
        rnd += 1
    out = previews / f"compare_{stem}_r{rnd}.png"
    zoom = tuple(int(v) for v in argv[argv.index("--zoom") + 1].split(",")) if "--zoom" in argv else None
    sections = list(photo.get("sections", {}).items()) if "--sections" in argv else None
    if "--sections" in argv and not sections:
        raise SystemExit(f"{photo_file} has no 'sections' in refs.json")
    rms = pl.compare_image(str(asset_dir / photo_file), photo["camera"], str(out), photo.get("landmarks", {}),
                           zoom=zoom, sections=sections)
    width = photo["size"][0]
    print(f"RMS {rms:.1f} px ({100 * rms / width:.2f} % of width)" if rms is not None else "RMS n/a (no landmark pairs)")
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:])
