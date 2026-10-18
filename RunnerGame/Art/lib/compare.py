"""Build an asset and compare it with one reference photo (one round of the comparison loop).

blender --background --factory-startup --python RunnerGame/Art/lib/compare.py -- <asset_dir> <ref/NN.jpg> [--fit] [--zoom x0,y0,x1,y1] [--sections]

--sections writes ONE sheet (<out>_sections.png) with a row per entry of the photo's "sections" in refs.json
({"name": [x0, y0, x1, y1]}): photo | model in colour | 50/50 blend, each at 320 px height.

--fit first fits the camera to the photo's landmarks (numerically, no images) and saves it to refs.json.

Reads the photo's "camera" and "landmarks" from <asset_dir>/refs.json, imports <asset_dir>/build.py,
writes <asset_dir>/previews/compare_<NN>_r<round>.png and prints the landmark errors.
"""
import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import photo_lib as pl  # noqa: E402


def main(argv):
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
                                     z_range=tuple(photo["camera_z_range"]) if photo.get("camera_z_range") else None)
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
