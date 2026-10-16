# Photo-to-Model Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A repeatable photo → measured spec → model → photo-comparison → OBJ/PNG workflow, proven on a
Voi-style e-scooter (2022 generation) and packaged as a project skill.

**Architecture:** Two small Python helper modules: `photo_tools.py` (system Python + Pillow: references,
grids, colour sampling, measuring) and `photo_lib.py` (Blender: spec loading, landmarks, camera match,
comparison images, shared bake/export, built on the existing `asset_lib.py`). A per-asset folder
holds photos, `refs.json`, `spec.json` and `build.py`. A new C# `AssetViewer` renders the multi-part
result in the course engine with gamma-correct lighting. A project skill ties the steps together.

**Tech Stack:** Python 3.10 (`C:\Python310\python.exe`, Pillow 10.3, stdlib `unittest`), Blender 5.2.2
headless (bundled Python 3.13 + numpy, **no Pillow**), curl, C#/.NET 10 + course `Engine`.

**Spec:** `docs/superpowers/specs/2026-10-17-photo-to-model-workflow-design.md`

## Global Constraints

- Blender: `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup --python-exit-code 1 --python <script> -- <args>`. Headless only; do not use the `mcp__blender__*` tools during implementation (the live Blender is shared with another session).
- **Never edit** `tools/asset-spike/asset_lib.py`, `tools/asset-spike/SpikeViewer/` or anything in `tools/asset-spike/baustelle/` or `tools/asset-spike/out/baustelle/` (another session is using them). Import `asset_lib` via `sys.path.insert(0, <repo>/tools/asset-spike)`.
- `photo_tools.py` must not import `bpy`; `photo_lib.py` must not import `PIL`.
- Downloads go through `curl` (the system Python's certificate store is outdated). Wikimedia requests send the User-Agent `HannoverRushHour-student-project/0.1 (university course; low-volume reference lookup)` and are paced (≥1 s between files, retry after 60 s on a non-JSON reply).
- Blender modelling: Z-up, 1 unit = 1 m. **The scooter faces +Y** (it drives towards −Z in the engine). Look shader nodes up by type, never by name.
- OBJ export settings exactly as in `asset_lib.bake_and_export`: `forward_axis='NEGATIVE_Z', up_axis='Y', export_triangulated_mesh=True, export_normals=True, export_uv=True, export_materials=False, apply_modifiers=True, global_scale=1.0`.
- Budgets: body ≤ 8,000 triangles, each wheel ≤ 1,000; one shared 1024² PNG.
- Colours in `spec.json` are **linear** RGB; PNGs are stored sRGB-encoded (normal PNG).
- No Voi logo, wordmark or QR code; no photo pixels in textures. Reference photos are CC BY / CC BY-SA and get credited.
- Python tests: `python -m unittest discover -s RunnerGame/Art/tests -p "test_*.py" -v`. Blender tests: files named `blender_test_*.py` in the same folder, run with the Blender command above.
- Work on branch `feature/photo-to-model`; commit only this plan's files (the working tree contains other sessions' untracked files).
- Gates A, B and C: stop and wait for the user's approval; never self-approve.

## Review Focus

- Commons titles with non-ASCII characters (`Bâle`, `Électrique`, `ü`) must survive fetching and land in `refs.json` unchanged → test in Task 1.
- Wikimedia rate limiting (empty or HTML reply instead of JSON) must lead to a wait and retry, not a crash or a silently empty pack → test in Task 1.
- Photos with an EXIF orientation tag: pixel coordinates measured in Pillow must match the image Blender loads (Blender ignores EXIF) → transpose and strip EXIF when saving, test in Task 1.
- Portrait photos: the camera match must respect the photo's aspect, so landmarks project correctly for 1000×1500 as well as 1500×1000 → test in Task 4.
- Landmarks outside the frame (a 3/4 photo that cuts off a wheel) must be reported as off-frame and skipped in the error, not crash the comparison → test in Task 4.

## File Structure

```
RunnerGame/Art/
  lib/photo_tools.py          refs fetch/sheet/credits, grid, colour sample, measure (system Python)
  lib/photo_lib.py            spec, landmarks, camera match, compare image, shared bake/export (Blender)
  lib/compare.py              Blender entry: build asset + render comparison for one photo
  tests/test_photo_tools.py   unittest
  tests/blender_test_photo_lib.py
  tests/blender_test_scooter.py
  assets/scooter_voi/
    titles.txt  ref/NN.jpg  refs.json  spec.json  build.py  previews/  out/
  ASSETS.md
tools/asset-viewer/           AssetViewer.csproj, Program.cs, GammaLit/ (material + 2 GLSL files)
.claude/skills/photo-to-model/SKILL.md
RunnerGame/CREDITS.md
RunnerGame/Assets/VEH_ScooterVoi_*.obj, VEH_ScooterVoi.png, VEH_ScooterVoi_parts.json
```

---

### Task 1: Reference pack (fetch, sheet, credits) → Gate A

**Files:**
- Create: `RunnerGame/Art/lib/photo_tools.py`, `RunnerGame/Art/tests/test_photo_tools.py`
- Create: `RunnerGame/Art/assets/scooter_voi/titles.txt`, `ref/`, `refs.json`, `previews/ref_sheet.jpg`
- Create: `RunnerGame/CREDITS.md`

**Interfaces:**
- Produces:
  - `parse_imageinfo(api: dict) -> list[dict]`: one dict per page: `title` (without the `File:` prefix), `author` (HTML stripped), `licence`, `source_url` (descriptionurl), `image_url` (thumburl). Raises `RateLimited` if `api` has no `query` key.
  - `save_normalised(src: Path, dst: Path, max_side: int = 1600) -> tuple[int, int]`: applies `ImageOps.exif_transpose`, shrinks so the long side is ≤ `max_side`, saves JPEG quality 90 without EXIF, returns (w, h).
  - `fetch_pack(asset_dir: Path, titles: list[str], width: int = 1600, run=subprocess.run, sleep=time.sleep) -> list[dict]`: one API request for all titles (`titles=` joined with `|`, `prop=imageinfo`, `iiprop=url|extmetadata`, `iiurlwidth=width`) via curl, up to 3 attempts with `sleep(60)` on `RateLimited`. Downloads each image to `ref/NN.jpg` (01-based, in `titles` order), normalises it and writes `refs.json` = `{"photos": [{"file": "ref/01.jpg", "title", "author", "licence", "source_url", "size": [w, h], "view": null, "landmarks": {}, "camera": null}]}`. Existing `view`/`landmarks`/`camera` values for the same title are kept.
  - `contact_sheet(asset_dir: Path, out: Path) -> None`: numbered thumbnails (photo index + `view` label).
  - `credits_lines(photos: list[dict]) -> list[str]`, format: `- ref/01.jpg: "Title" by Author, CC BY-SA 4.0, <source_url>`.
  - CLI: `python RunnerGame/Art/lib/photo_tools.py fetch <asset_dir> <titles.txt>` and `... sheet <asset_dir>`.

- [ ] **Step 1: Write the failing tests** in `test_photo_tools.py`:
  - `test_parse_imageinfo_fields`: a fixture dict with a page titled `File:Trottinette électrique Voi Elsässerstrasse - Bâle.jpg`, Artist `<a href="//x">Jane Doe</a>`, LicenseShortName `CC BY-SA 4.0` → title equals `Trottinette électrique Voi Elsässerstrasse - Bâle.jpg`, author `Jane Doe`, licence `CC BY-SA 4.0`.
  - `test_parse_rate_limited`: `parse_imageinfo({})` raises `RateLimited`.
  - `test_fetch_retries_on_rate_limit`: a fake `run` returns non-JSON once, then the fixture JSON; the fake `sleep` records `[60]`; result has 1 entry.
  - `test_save_normalised_exif_rotation`: a 200×100 JPEG with EXIF Orientation=6 → `save_normalised` returns `(100, 200)` and the saved file has no Orientation tag.
  - `test_credits_line_format`: the exact string from the format above.
- [ ] **Step 2: Run them, expect failures** (`ModuleNotFoundError: photo_tools`).
- [ ] **Step 3: Implement** the functions and the CLI. Call curl with a list of arguments (`--data-urlencode` per parameter) so non-ASCII titles pass through unchanged.
- [ ] **Step 4: Run the tests, expect PASS.**
- [ ] **Step 5: Real fetch.** Write `titles.txt` (one Commons title per line) with these 2022-generation candidates:
  ```
  File:VOI.Hannover-2022.jpg
  File:VOI.in-Hannover-2022.jpg
  File:Voi scooter in Liverpool 20221101 085349.jpg
  File:Voi scooter in Liverpool 20221101 085614.jpg
  File:Voi scooter in Liverpool 20221101 085618.jpg
  File:Voi scooter in Liverpool 20221101 085924.jpg
  File:Voi scooter in Liverpool 20221101 085926.jpg
  File:Voi scooter in Liverpool 20221101 124530.jpg
  File:Voi scooter in Liverpool 20221101 163930.jpg
  File:Voi. Scooter.jpg
  File:Frankfurt, Germany - Electric rental kick scooter handlebars.jpg
  File:Frankfurt, Germany - Electric rental kick scooter rear.jpg
  File:Frankfurt, Germany - Electric rental kick scooters.jpg
  File:E-Scooter HL Germany.jpg
  File:Voi e-scooter used as part of the Portsmouth official 2021 Voi rental trial.jpg
  File:Electric scooter controls (Voi Portsmoiuth 2021).jpg
  ```
  Run `fetch`, then `sheet`. Expected: 16 files in `ref/`, all with a licence in `refs.json`.
- [ ] **Step 6: Tag and prune.** Look at the sheet and the photos. Set `view` per photo (`side_left`, `side_right`, `rear`, `rear_34`, `front_34`, `top`, `detail_<part>`). Remove photos that show another generation (e.g. no black box on the stem) and their files. Mark one `side_*` photo and one `rear_34` photo as `"key": true`. Re-run `sheet`.
- [ ] **Step 7: Credits.** Create `RunnerGame/CREDITS.md` with a `## Reference photos (not shipped in the game)` section built from `credits_lines`.
- [ ] **Step 8: Commit** `photo_tools.py`, the tests, the `scooter_voi` reference files and `CREDITS.md`.
- [ ] **Step 9: GATE A.** Show the user `previews/ref_sheet.jpg` with the tags and key photos. Wait for approval.

### Task 2: Grid, colour sampling and measuring

**Files:**
- Modify: `RunnerGame/Art/lib/photo_tools.py`, `RunnerGame/Art/tests/test_photo_tools.py`

**Interfaces:**
- Produces:
  - `grid_positions(crop: tuple[int,int,int,int], step: int, scale: float) -> tuple[list[tuple[int,float]], list[tuple[int,float]]]`: (source px, output px) for each vertical and horizontal grid line inside the crop, source values that are multiples of `step`.
  - `grid_image(src: Path, out: Path, crop=None, step: int = 50, out_width: int = 1200) -> None`: crop (default: whole photo), scale to `out_width`, draw grid lines with **source-pixel** labels every line, a stronger line every 5 lines.
  - `srgb_to_linear(c: float) -> float` (IEC 61966-2-1 formula).
  - `sample_color(src: Path, box: tuple[int,int,int,int]) -> tuple[float,float,float]`: per-channel median in sRGB over the box, returned as linear RGB.
  - `measure(landmarks: dict[str, list[float]], ruler: tuple[str, str, float], pairs: dict[str, tuple[str, str]]) -> dict[str, float]`: metres per pixel from the ruler's two landmarks and its length in metres, then the distance for each named pair.
  - CLI: `grid <photo> <out> [--crop x0,y0,x1,y1] [--step N]`, `color <photo> x0,y0,x1,y1`, `measure <asset_dir> <ref/NN.jpg> <pairs.json>` (reads landmarks from `refs.json`; `pairs.json` = `{"ruler": ["a","b",0.254], "pairs": {"wheelbase": ["front_axle","rear_axle"]}}`).

- [ ] **Step 1: Write the failing tests:**
  - `test_grid_positions`: crop `(100, 200, 500, 600)`, step 50, scale 2.0 → first vertical line `(100, 0.0)`, line at source 150 → output 100.0, 9 vertical lines.
  - `test_sample_color_linear`: solid `(128,128,128)` image → each channel `0.2158 ± 0.001`.
  - `test_measure_ruler`: landmarks `a=(0,0)`, `b=(254,0)`, `c=(0,0)`, `d=(0,1000)`, ruler `("a","b",0.254)`, pairs `{"x": ("c","d")}` → `{"x": 1.0 ± 1e-6}`.
- [ ] **Step 2: Run, expect FAIL.**
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run, expect PASS.** Then make a grid image of one key photo and Read it to check the labels are legible.
- [ ] **Step 5: Commit.**

### Task 3: Spec sheet and rough scooter model

**Files:**
- Create: `RunnerGame/Art/lib/photo_lib.py`, `RunnerGame/Art/assets/scooter_voi/spec.json`, `RunnerGame/Art/assets/scooter_voi/build.py`, `RunnerGame/Art/tests/blender_test_scooter.py`
- Modify: `RunnerGame/Art/assets/scooter_voi/refs.json` (landmarks)

**Interfaces:**
- Consumes: `grid_image`, `measure`, `sample_color` (Task 2); `asset_lib.clear_scene`, `material`, `flat`, `box`, `cyl` (existing).
- Produces:
  - `spec.json` format: `{"ruler": {"photo": "ref/NN.jpg", "from": "front_axle_top", "to": "front_axle_bottom", "metres": 0.254}, "dims": {"<name>": {"value": <float>, "source": "<photo + note>"}}, "colors": {"<name>": {"linear": [r,g,b], "source": "<photo + box>"}}}`. Required dims: `wheel_d, wheel_w, wheelbase, deck_len, deck_w, deck_top_h, deck_thick, stem_tilt_deg` (from vertical, top leaning back towards the rider is positive), `stem_d, bar_h, bar_w, box_w, box_d, box_h, box_bottom_h, rear_fender_len`. Required colours: `paint, deck, tyre, grip, box, metal`.
  - `photo_lib.Spec(path)` with `.d(name) -> float`, `.c(name) -> tuple[float,float,float]`; a missing name raises `KeyError` naming the key.
  - `photo_lib.landmark(name: str, loc: tuple[float,float,float]) -> bpy.types.Object`: an empty named `LM_<name>`.
  - `build.py`: `build(spec: Spec) -> dict[str, list[bpy.types.Object]]` with keys `body`, `wheel_front`, `wheel_rear`. Origin convention: ground (z = 0) midway between the two axles in Y; front axle at `+wheelbase/2`. Landmarks at least: `front_axle, rear_axle, front_axle_top, front_axle_bottom, bar_left, bar_right, stem_top, deck_front, deck_rear, rear_light`. Running `build.py` headless with `-- --preview <png>` writes `asset_lib.render_previews` output.

- [ ] **Step 1: Measure.** Make grid images of the key side photo (whole + zoomed crops). Enter the landmark pixel positions in `refs.json` → `landmarks`. Run `measure` with the ruler `front_axle_top → front_axle_bottom = 0.254 m` (10-inch wheel). Sample colours from clean patches with `color`. Write `spec.json` with a `source` for every value. Plausibility check: overall length ≈ 1.1–1.3 m and handlebar height ≈ 1.1–1.3 m; investigate before continuing if outside.
- [ ] **Step 2: Write the failing Blender test** `blender_test_scooter.py`: build from `spec.json`, then assert:
  - `|LM_front_axle - LM_rear_axle| == wheelbase ± 0.001`
  - `LM_front_axle.y > 0`
  - `(LM_bar_left.z + LM_bar_right.z)/2 == bar_h ± 0.01`
  - lowest vertex over all parts at `z == 0 ± 0.002`
  - `|LM_bar_left.x - LM_bar_right.x| == bar_w ± 0.005`
- [ ] **Step 3: Run it, expect FAIL** (no `build.py`).
- [ ] **Step 4: Implement** `photo_lib.Spec`, `photo_lib.landmark` and `build.py` (blockout: simple parts with flat spec colours, no detail yet).
- [ ] **Step 5: Run it, expect PASS.** Render the preview and Read it.
- [ ] **Step 6: Commit.**

### Task 4: Camera match and comparison images → Gate B

**Files:**
- Modify: `RunnerGame/Art/lib/photo_lib.py`
- Create: `RunnerGame/Art/lib/compare.py`, `RunnerGame/Art/tests/blender_test_photo_lib.py`

**Interfaces:**
- Consumes: `build(spec)`, `Spec`, landmarks (Task 3); `refs.json` `landmarks` and `camera`.
- Produces:
  - `camera` format in `refs.json`: `{"loc": [x,y,z], "look_at": [x,y,z], "lens_mm": 28.0, "roll_deg": 0.0}` (Blender world coordinates, sensor width 36 mm, `sensor_fit='AUTO'`).
  - `match_camera(photo_size: tuple[int,int], cam: dict) -> bpy.types.Object`: creates and activates the camera and sets the render resolution to the photo size.
  - `project_landmarks(cam_obj) -> dict[str, tuple[float,float] | None]`: pixel coordinates (origin top left) for every `LM_*` empty, `None` when outside the frame or behind the camera.
  - `landmark_errors(projected: dict, photo: dict[str, list[float]]) -> tuple[dict[str, float], float | None]`: per-landmark pixel distance for names present in both and on-frame, plus the RMS (or `None` if no pairs).
  - `compare_image(photo_path: str, cam: dict, out_png: str, photo_landmarks: dict) -> float | None`: Workbench render with transparent film; writes one PNG with three panels (photo | render | overlay). The overlay is the photo with the render's silhouette edge in magenta, photo landmarks in green, projected landmarks in red, joined by lines. Returns the RMS. Composited with numpy on `bpy.data.images` (no Pillow).
  - `compare.py` CLI: `blender ... --python RunnerGame/Art/lib/compare.py -- <asset_dir> <ref/NN.jpg>`. Imports the asset's `build.py`, builds, reads that photo's `camera` and `landmarks`, writes `previews/compare_<NN>_r<round>.png` (round = next free number) and prints `RMS <value> px` plus each landmark's error.

- [ ] **Step 1: Write the failing Blender tests:**
  - `test_projection_centre_and_offset`: landmarks at `(0,0,0)` and `(0.5,0,0)`, camera `loc (0,-5,0)`, `look_at (0,0,0)`, lens 50, photo 1000×1000 → `(500, 500) ± 0.5` and `(638.9, 500) ± 0.5`.
  - `test_projection_portrait`: same scene, photo 1000×1500 → origin at `(500, 750) ± 0.5`; the offset landmark lies right of centre with y = `750 ± 0.5`.
  - `test_off_frame_is_none`: a landmark at `(50, 0, 0)` → `None`; `landmark_errors` ignores it.
  - `test_errors_rms`: projected `{a: (0,0), b: (3,4)}`, photo `{a: [0,0], b: [0,0]}` → errors `{a: 0, b: 5}`, RMS `3.5355 ± 1e-3`.
  - `test_compare_image_size`: a 1-m cube and a 300×200 grey test photo (written by the test) → the output PNG is 900×200.
- [ ] **Step 2: Run, expect FAIL.**
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run, expect PASS.**
- [ ] **Step 5: Comparison loop on the key photos.** For each key photo:
  1. Mark landmarks with the grid helper.
  2. Set a first `camera` by hand: estimate from the photo, then adjust until wheels and deck line up (Read the compare image each time).
  3. Read the overlay, list concrete differences, and correct `spec.json` (with a source note).
  4. Rebuild and compare again.

  Stop when no difference is visible at game distance and the RMS is below 1.5 % of the photo width, or after 5 rounds per photo. Record the final RMS per photo in `ASSETS.md`.
- [ ] **Step 6: Commit** (code, tests, `spec.json`, `refs.json`, the final compare images).
- [ ] **Step 7: GATE B.** Show the user the final side and rear-3/4 compare images. Wait for approval. The user decides the time box and fallback at this point (spec, section 3).

### Task 5: Details, materials, shared bake and three-part export

**Files:**
- Modify: `RunnerGame/Art/lib/photo_lib.py`, `RunnerGame/Art/assets/scooter_voi/build.py`, `spec.json`, `RunnerGame/Art/tests/blender_test_scooter.py`
- Output: `RunnerGame/Art/assets/scooter_voi/out/`

**Interfaces:**
- Consumes: `asset_lib.join_all`, `asset_lib.bake_and_export(..., keep_origin=True)`, `asset_lib.material` (existing).
- Produces:
  - `export_obj(obj, path: str) -> None` with the export settings from Global Constraints.
  - `bake_shared_and_export(parts: dict[str, list[Object]], pivots: dict[str, tuple[float,float,float]], out_dir: str, name: str, res: int = 1024, samples: int = 32) -> dict`. It joins all parts into one object, keeping a vertex group per part, and runs `asset_lib.bake_and_export(joined, tmp_dir, name, res, samples=samples, keep_origin=True)` with the joined object's origin at the world origin. It then separates by vertex group and moves each part's origin to its pivot (body `(0,0,0)`, wheels at their axle landmarks). It exports `<name>_<part>.obj` for each part, copies `<name>.png` to `out_dir`, and writes `<name>_parts.json` = `{"texture": "<name>.png", "parts": [{"name": "body", "obj": "<name>_body.obj", "pivot": [x,y,z]}, ...]}` with pivots in **Blender coordinates** (same convention as the construction-site `mounts.json`). It returns that dict.
  - `build.py -- --export` runs `build` then `bake_shared_and_export(..., name="VEH_ScooterVoi")`.

- [ ] **Step 1: Extend the failing test.** After `--export` with `res=128, samples=1` into a temp dir:
  - 3 OBJs, 1 PNG and the parts.json exist
  - re-imported wheel OBJs have their bounding-box centre at the origin `± 0.002`
  - parts.json pivots equal `LM_front_axle` / `LM_rear_axle` `± 0.001`
  - body triangles ≤ 8000, each wheel ≤ 1000
- [ ] **Step 2: Run, expect FAIL.**
- [ ] **Step 3: Implement** `export_obj` and `bake_shared_and_export`.
- [ ] **Step 4: Run, expect PASS.**
- [ ] **Step 5: Detail pass** in camera priority (rear light, reflector, insurance plate with a made-up number in the colour shown in the reference photo, rear fender, deck grip and rails, handlebar grips/levers/display block, stem box, kickstand folded up). Materials via `asset_lib.material` with spec colours and light weathering (used rental scooter). Re-run the comparison loop on one `detail_*` photo per area, max 3 rounds each. Keep the Task 3 test green.
- [ ] **Step 6: Export** at full quality (`res=1024, samples=32`). Read the preview.
- [ ] **Step 7: Commit.**

### Task 6: AssetViewer (multi-part, gamma-correct, game camera)

**Files:**
- Create: `tools/asset-viewer/AssetViewer.csproj` (same references as `SpikeViewer.csproj`, but with a relative `..\..\Engine\Engine.csproj` path, and `<EmbeddedResource Include="GammaLit\*.glsl" />`)
- Create: `tools/asset-viewer/Program.cs`, `tools/asset-viewer/GammaLit/GammaLitMaterial.cs`, `GammaLit/gamma_lit.vert.glsl`, `GammaLit/gamma_lit.frag.glsl`

**Interfaces:**
- Consumes: `<name>_parts.json` (Task 5).
- Produces: CLI `dotnet run --project tools/asset-viewer -- <parts.json> <out_prefix> <views>`, where `<views>` is a comma list of `game` and/or yaw angles in degrees (0 = front towards the camera). It writes `<out_prefix>_<view>.png` (1280×720) and exits. With `--show` instead of `<out_prefix>` it opens an interactive window (arrow keys orbit, as in SpikeViewer).
  - Part placement: Blender pivot `(x, y, z)` → engine translation `(x, z, -y)`; parts share one texture.
  - `game` preset (my call until the real gameplay camera exists): eye `(0, 1.8, 3.2)`, target `(0, 0.9, -2.0)` in engine coordinates, scooter at the origin facing −Z, FOV 50°.
  - `GammaLitMaterial`: the same uniforms as `LitTextureMaterial` (`uTexture, uTint, uAmbientStrength, uSpecularStrength, uShininess`). The fragment shader converts the texture to linear (`pow(c, vec3(2.2))`), lights in linear space and outputs `pow(color, vec3(1.0/2.2))`. Override with `protected override` (the base members are `protected internal` in another assembly).

- [ ] **Step 1: Implement** the project.
- [ ] **Step 2: Build:** `dotnet build tools/asset-viewer/AssetViewer.csproj`. Expected: `0 Warning(s)`, `0 Error(s)`.
- [ ] **Step 3: Verify** with `out/VEH_ScooterVoi_parts.json`, views `game,0,90,215`. Read the images and check that the wheels sit in their fenders (not floating, not offset), the scooter faces away from the camera in `game`, and no faces are missing.
- [ ] **Step 4: Commit.**

### Task 7: Engine check → Gate C → install

**Files:**
- Create: `RunnerGame/Art/ASSETS.md`; copy into `RunnerGame/Assets/`: `VEH_ScooterVoi_body.obj`, `_wheel_front.obj`, `_wheel_rear.obj`, `VEH_ScooterVoi.png`, `VEH_ScooterVoi_parts.json`

- [ ] **Step 1:** Render `game` plus yaw angles matching the key photos. Build `previews/engine_vs_photo.png` (each engine shot next to its photo; Pillow, system Python).
- [ ] **Step 2: GATE C.** Show the user the side-by-side. Wait for approval. On change requests, go back to Task 5 step 5.
- [ ] **Step 3: Install** the files into `RunnerGame/Assets/`. Write `ASSETS.md`: one row with asset name, files, triangles per part, texture size, final RMS per key photo, approval date.
- [ ] **Step 4:** `dotnet build CgiMin.sln` → 0 warnings (the assets are copied to the output).
- [ ] **Step 5: Commit.**

### Task 8: Project skill

**Files:**
- Create: `.claude/skills/photo-to-model/SKILL.md`

- [ ] **Step 1: Write the skill.** Frontmatter `name: photo-to-model`, with a description that triggers on "model <real object> from photos", "new asset from reference photos", and similar. The body covers:
  - the 7 steps from the spec with the exact commands from Tasks 1–7
  - the three gates (never self-approve)
  - stop rules (RMS < 1.5 % of photo width or 5 rounds; 3 rounds for details)
  - the file layout, `refs.json`/`spec.json`/`parts.json` formats, and the conventions (+Y facing for vehicles, −Y for props; linear colours; budgets)
  - the pitfalls: curl for downloads, EXIF, non-ASCII titles, rate limits, node lookup by type, no logos, no photo pixels in textures, don't edit `asset_lib.py`/`SpikeViewer`
  - the lessons learned from the scooter run (take them from `ASSETS.md` and the compare rounds)
- [ ] **Step 2: Dry-run check.** In a fresh subagent, ask: "Using only the photo-to-model skill, list the commands you would run to start a model of a Hannover wheelie bin". The answer must follow steps 1–3 with correct paths. Fix the skill where it doesn't.
- [ ] **Step 3: Commit.**
