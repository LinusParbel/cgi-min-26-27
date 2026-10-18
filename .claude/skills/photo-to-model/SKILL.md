---
name: photo-to-model
description: Build a believable 3D model of a specific real object (vehicle, bin, tram, clock...) from free-licensed reference photos, measured by script and compared against the photos until the outline matches, then export OBJ + PNG for the runner game. Use for "model <real object> from photos", "make a new asset from reference photos", "photo-to-model", "build the Hannover wheelie bin / tram / Voi scooter from photos".
---

# photo-to-model

Repeatable workflow: reference photos -> measured `spec.json` -> headless Blender build -> photo/outline comparison -> shared-texture OBJ export -> engine check. Worked example: `RunnerGame/Art/assets/scooter_voi/` (register: `RunnerGame/Art/ASSETS.md`). Design: `docs/superpowers/specs/2026-10-17-photo-to-model-workflow-design.md`.

## 0. When to use

- Generic prop ("a bin / cone / barrier"), recognisability not critical -> sibling workflow `tools/asset-spike/WORKFLOW.md` (script-built, no photo measuring). Do not use this skill.
- Object that must look like a specific real thing (Voi scooter, Hannover tram, the Hannover bin, Kroepcke clock) -> this skill.
- No external 3D generators, no paid services, no photo pixels in textures.

All commands run from the repo root in Git Bash. Notation: `BL` = `"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup --python-exit-code 1`; `A` = `RunnerGame/Art/assets/<asset>` (e.g. `scooter_voi`); `python` = system Python (Pillow, numpy). Pass **absolute** output paths to Blender.

## 1. The 7 steps

**Step 1 - Reference pack.** Write `A/titles.txt` (one Commons title per line, `File:Name.jpg`). Find candidates with curl against the Commons API (low volume).
```
python RunnerGame/Art/lib/photo_tools.py fetch A A/titles.txt   # -> A/ref/NN.jpg (long side 1600, EXIF applied) + A/refs.json
python RunnerGame/Art/lib/photo_tools.py sheet A                # -> A/previews/ref_sheet.jpg (one contact sheet)
```
View ONLY the contact sheet. Edit `refs.json`: set `view` (`side_left`, `side_right`, `rear`, `rear_34`, `front_34`, `top`, `detail_<part>`) and `"key": true` on the key photos. Prune photos by deleting them from refs.json and titles.txt (numbering gaps are fine; a re-fetch keeps view/key/landmarks/camera by title). Add credits to `RunnerGame/CREDITS.md` (same format as the Voi section; a haiku agent can write the lines from refs.json).
**GATE A (user):** in ONE AskUserQuestion: (1) photo pack approved (right model/generation, a true side view, a rear 3/4);
(2) **detail level** — `backdrop` (outline only, ≤ 5k tris, 1024²), `medium` (main features, ≤ 12k, 1024²) or `replica`
(every visible feature of the key side, ≤ 25k, 2048²); (3) which side faces the player. Record the answers as
`detail_level`, `tri_budget`, `tex_res` in spec.json. Also set `"camera_z_range"` on each key photo from where it was
taken (standing on a street ≈ [1, 2]; across water ≈ [-4, 6]). Stop and wait.

**Step 2 - Sections, then measure -> `spec.json`.** Pick a ruler (known real size: wheel diameter, a published
facade length, a tower height). Split the key photo into **sections** (one per distinct part: tower, dome group,
gable, central block, wheel, handlebar...) and write them into that photo's refs.json entry as
`"sections": {"name": [x0, y0, x1, y1]}` (photo pixels). Then measure **each section on its own 1:1 grid**
(`--crop` = the section box, `--step 10`) BEFORE the first build. For every part record a **profile**, not one number:
the width at 4–6 heights from bottom to top (a gable, roof, spire, cap or tower is a list `[[z, width], ...]`), plus
the features on it (window axes x, rows z0–z1, arches, pediments with their own width). Read the printed LABELS, not
positions. Per key photo:
```
python RunnerGame/Art/lib/photo_tools.py grid A/ref/NN.jpg A/previews/grid_NN.png [--crop x0,y0,x1,y1] [--step 50]
python RunnerGame/Art/lib/photo_tools.py color A/ref/NN.jpg x0,y0,x1,y1          # median patch -> LINEAR rgb
python RunnerGame/Art/lib/photo_tools.py measure A ref/NN.jpg A/measure_NN.json   # prints metres per pair
```
Read pixel points from the grid image and write them into that photo's `landmarks` in refs.json (`{"name": [x, y]}`). `measure_NN.json` = `{"ruler": ["lm_a","lm_b",metres], "pairs": {"wheelbase": ["front_axle","rear_axle"], ...}}`. Write `A/spec.json`:
```
{"ruler": {"photo": "ref/17.jpg", "from": "lm", "to": "lm", "metres": 0.254, "note": "..."},
 "dims":   {"wheel_d": {"value": 0.254, "source": "ruler"}, ...},
 "colors": {"paint": {"linear": [r, g, b], "source": "ref/02.jpg box 740,500,760,550"}, ...}}
```
Every value needs a `source` (photo + landmarks, or "estimate; check in ref/NN"). Metres, degrees, linear colours.

**Step 3 - First build.** Give the builder agent the brief in `builder_brief.md` (this folder), filled in — it
carries the shape vocabulary (profiles → trapezoid stacks/lathes, flaring roofs, frontispieces, recessed windows)
that keeps first builds from turning into boxes and pyramids. `A/build.py` follows `scooter_voi/build.py`: `build(spec) -> dict[str, list[Object]]` (parts, e.g. `body`, `wheel_front`); read numbers only via `spec.d("name")` / `spec.c("name")`; use `import photo_lib as pl` (`pl.al` = `asset_lib`; helpers `pl.tube`, `pl.arc_shell`, `pl.landmark`); create an `LM_<name>` empty (`pl.landmark(name, loc)`) for every landmark in refs.json. Corrections = change a number in spec.json and rebuild, never hand-edit geometry. Smoke test:
```
BL --python A/build.py -- --preview /abs/path/A/previews/preview.png
```

**Step 4 - Comparison loop (key photos).** Needs a rough `camera` in that photo's refs.json entry: `{"loc":[x,y,z],"look_at":[x,y,z],"lens_mm":26,"roll_deg":0}`.
```
BL --python RunnerGame/Art/lib/compare.py -- A ref/NN.jpg --fit
```
`--fit` numerically fits the camera to the landmarks and saves it to refs.json (drop it on later rounds if the camera is fine). Output: landmark errors, RMS (px and % of photo width), and `A/previews/compare_NN_r<k>.png` (3-panel sheet, do not view) plus `compare_NN_r<k>_overlay.png` (cropped, the one image to view). Read the numbers first; view the overlay only if needed. Derive spec corrections, rebuild, repeat.
**Section loop (the standard from round 2 on):** `BL --python RunnerGame/Art/lib/compare.py -- A ref/NN.jpg --sections`
writes ONE image `compare_NN_r<k>_sections.png`: a row per section with photo | model in colour | 50/50 blend at
320 px height. View only that image. **Done** when no section shows a double image (ghost edge, offset window,
protruding step) — the landmark RMS is only a pre-check (it is partly circular and blind inside the silhouette).
For a ghost you cannot place, crop the model panel of the 3-panel sheet at that spot (model-only view).
Each round also writes `compare_NN_r<k>_blend.png` (photo and coloured model 50/50, same crop) — the outline cannot
see windows, gables or pinnacles inside the silhouette, the blend can (mismatches show as double images). For details
add `--zoom x0,y0,x1,y1` (photo pixels) → `_blend_zoom.png` at full resolution. If the fitted camera lands at an
impossible height, set `"camera_z_range": [lo, hi]` on that photo in refs.json.
**GATE B (user):** side + rear 3/4 outline approved. Stop and wait.

**Step 5 - Details**, in game-camera priority: rear (light, reflector, plate, fender), deck/top, handles/controls, stem/box. Front and underside stay simple. Same loop on `detail_*` photos; add each detail area as a section. Materials via `al.material` / `al.flat` / `al.emissive_look` with spec colours.

**Step 6 - Export (the only bake, 1024^2, 32 samples).**
```
BL --python A/build.py -- --export     # -> A/out/<PREFIX>_<part>.obj, <PREFIX>.png, <PREFIX>_parts.json
```
`build.py main()` handles `--export` as in the scooter: `pl.bake_shared_and_export(parts, pivots, str(out.resolve()), "<PREFIX>", res=1024, samples=32)` with pivots = `{"body": (0,0,0), "wheel_front": LM_front_axle location, ...}`. Body origin on the ground at its centre; moving parts have their origin on their axis. Check the triangle counts.

**Step 7 - Engine check.**
```
dotnet run --project tools/asset-viewer -- A/out/<PREFIX>_parts.json A/previews/engine game,0,90,180
```
Writes `A/previews/engine_<view>.png` (1280x720; `game` = behind/above preset, numbers = yaw degrees, 0 = front towards camera). `--show` instead of the prefix opens an interactive window.
**GATE C (user):** in-engine look approved. Then install:
```
mkdir -p RunnerGame/Assets/Models/<Category>/<Asset>
cp A/out/<PREFIX>* RunnerGame/Assets/Models/<Category>/<Asset>/
```
(Existing categories: `Fahrzeug`, `Baustelle`, `Mull`.) Then `dotnet build CgiMin.sln` (no new warnings), add a row to `RunnerGame/Art/ASSETS.md`, finish `RunnerGame/CREDITS.md`. Commit only when the user asks.

## 2. Roles, loops, review and stops

The main session is the **orchestrator**: it runs the steps below in order, hands work to the named agent, and
stops at every STOP. One asset at a time; at most 3 agents running at once. Agents never commit and never
approve anything; only the user approves.

| # | Step | Who | Model | Loop / limit | Images |
|---|---|---|---|---|---|
| 1 | search + `fetch` + `sheet` | script | – | – | 0 |
| 2 | tag views/keys, write credits (from refs.json titles) | helper agent | **haiku** | once | 0 (text only) |
| A | **STOP A** – photo pack | user | – | – | 1 (contact sheet) |
| 3 | sections, 1:1 grids, profiles, landmarks, `color`, `spec.json` | main session | user's model | once per section, before any build | 1 grid per section |
| 4 | first build from the filled-in `builder_brief.md` | builder agent | **sonnet** | until its Blender tests pass | 1 preview |
| 5 | `--fit` once, then section loop (`compare.py --sections`) | main session | user's model | until no section shows a double image (see loop rules) | 1 section sheet per round |
| B | **STOP B** – outline | user | – | – | the 2 final overlays |
| 6 | details, materials, `--export` | builder agent | **sonnet** | self-check by numbers (tris, bounds, tests); ≤ 2 rounds per detail photo | ≤ 4 |
| 7 | independent review against the photos | reviewer agent | **sonnet** | one review; **reads, never edits** | ≤ 4 (1 engine sheet + ≤ 3 refs) |
| 7b | fix the review findings | same builder (SendMessage) | **sonnet** | one fix batch + one re-export | ≤ 1 |
| C | **STOP C** – in-engine look | user | – | – | 1 engine-vs-photo sheet |
| 8 | install, `ASSETS.md`, `CREDITS.md`, `dotnet build` | main session | – | – | 0 |

**Reviewer checklist (step 7):** outline vs. key photos; real dimensions within ±10 % of spec.json; facing
(+Y vehicles / −Y props) and parts on their pivots in the engine sheet; no missing faces, floating or
intersecting parts; colours plausible in the engine sheet (not sunlit-bright); triangle and texture budgets;
no logos or photo pixels. Output: a numbered list, each item marked **must fix** or **could fix** with the
evidence (number or image). Must-fix items go to step 7b; could-fix items go to STOP C.

**At every STOP, present this and wait** (use AskUserQuestion when there are ≤ 4 decisions):
1. What matches the photos (one line each, with the number that shows it).
2. What still differs — one line each with the options **keep as is** / **fix**, and the cost of fixing
   (rounds, images, a re-bake).
3. Your recommendation, then stop. Never self-approve. Gate feedback = one fix batch + one re-export, then
   present again.

**Loop rules (never ask the user mid-loop):**
- Default limits: key photo ≤ 3 rounds, detail photo ≤ 2 rounds. Continue automatically while each round cuts
  the landmark RMS by > ~20 % or fixes something visible in the overlay.
- Stop early when a round brings no improvement (e.g. a leaning object, poor landmarks) – say why at the stop.
- At the limit, do not stop silently: every remaining difference goes into the next STOP as
  "keep as is / one more round (≈ 1 image)". The user decides there.
- Hard ceiling: 5 rounds per photo including user-granted extras – beyond that the photo is the problem.
- Review: one review + one fix batch. A second review only if must-fix items changed geometry, and only on
  those items (≤ 2 images). Anything still open goes to STOP C – no reviewer/builder ping-pong.
- Target: outline matches in the overlay and landmark RMS < ~1.5 % of photo width (a leaning object may stay
  higher – say so at the stop). Landmark RMS is partly circular; shapes (rounded fenders etc.) need the overlay.
Budgets: body ≤ 8,000 triangles, each moving part ≤ 1,000, one shared 1024² PNG.

**Token rules:** ≤ 4 reference photos in the loop (1 key side, 1 key rear 3/4, ≤ 2 details). View ONE image per
comparison round (the cropped `*_overlay.png`, ≤ 1000 px); never re-read images from earlier rounds; numbers
(landmark errors, `measure`, triangle counts) before pictures. Workbench previews for geometry; bake only for
`--export`. Briefs to agents name exact files, signatures, the image budget and "do not commit".

## 3. File layout and formats

```
RunnerGame/Art/lib/        photo_tools.py (system python, no bpy)  photo_lib.py (Blender, no PIL)  compare.py
RunnerGame/Art/assets/<asset>/   ref/NN.jpg  refs.json  spec.json  titles.txt  build.py  previews/  out/
RunnerGame/Assets/Models/<Category>/<Asset>/   runtime OBJ + PNG + parts.json only
```
- `refs.json`: `{"photos":[{file,title,author,licence,source_url,size:[w,h],view,key,landmarks:{name:[x,y]},camera}]}`.
- `spec.json`: see step 2; every value has a `source`.
- `<PREFIX>_parts.json`: `{"texture":"X.png","parts":[{"name","obj","pivot":[x,y,z]}]}`. Pivots are in **Blender coordinates**; engine translation = `(x, z, -y)`. Prefix like `VEH_ScooterVoi`.
- Conventions: Blender Z-up, 1 unit = 1 m; **vehicles face +Y in Blender** (they drive towards -Z in the engine), static props face -Y; OBJ export is forward -Z / up Y, triangulated (done by `bake_shared_and_export`); PNG sRGB, spec colours linear; look shader nodes up by type, never by name; the engine has no normal maps, do not brighten textures to compensate.

## 4. Mistakes that cost extra rounds (each happened)

| Mistake | Instead |
|---|---|
| Detail level never agreed → first model rejected as "not detailed enough" | Ask the detail level at GATE A |
| One number per part (top/bottom) → builder guesses the shape (pyramid, box steps, full-width pediment) | Profiles (width at 4–6 heights) per part, features with their own widths |
| Measured on medium-zoom grids, misread a band as an eave | 1:1 grid per section, labels only |
| Global RMS/outline "passed" while gables, towers, windows were wrong | Section sheet; done = no double image per section |
| Camera fit landed underground | `camera_z_range` from the shooting position at GATE A |
| A new test passed although the geometry was wrong (it filtered out what it should check; it only looked at vertices) | Main session breaks the BUILD code once per new test (scale a part, close an opening — mark the line `# MUTATION`), sees the test go RED, restores. Mutating spec.json proves nothing for build-equals-spec tests: the build follows the spec. Openings/gaps: test with a ray cast, not with vertices |
| Viewer/tool bug read as a model bug (far plane hid the dome) | When an engine view contradicts the blend, suspect the tool first; check with numbers (OBJ bounds, normals) |

## 5. Pitfalls

- Downloads: **curl, not urllib** (old cert store). Wikimedia: project User-Agent, >= 1 s between files, a non-JSON reply = rate limit, wait 60 s and retry (fetch does this; never hammer). Titles may be non-ASCII (`Bâle`, `ü`): keep them in UTF-8 files, never pass them as shell/curl arguments, and expect a garbled Windows console.
- EXIF: reference copies are already transposed; measure and mark landmarks on `ref/NN.jpg` only, never on originals.
- Blender: absolute output paths; headless only; do not use `mcp__blender__*` for builds (the live Blender is shared with other sessions).
- Grid images: read the printed LABELS (source px), not positions on the displayed image; zoom with `--crop` for small parts.
- Near-face perspective: widths/heights of near-side parts read from a side photo are too big; correct after the first compare. Widths invisible from the side are estimates - mark them so in `source`.
- Landmark RMS is partly circular (landmarks and fit use the same photo); the overlay outline is the real check.
- Sunlit colour samples are too light: sample flat shaded areas, darken after the engine check.
- Leaning or parked objects bias the camera fit; prefer upright photos as key views.
- A file open in an image viewer can be locked on Windows; close it or write a new name.
- Large objects: the viewer's clip planes scale with the model; for a photo-like engine view use `--pitch 5`.
- Tapering shapes (gables, spires): build trapezoids/frustums per measured segment, not stacked boxes (box corners show as ghosts).
- A band inside a gable is easily misread as an eave; confirm heights on the 1:1 blend zoom.
- Symmetric objects: measure one half and mirror; small left/right differences in the photo are perspective, not model errors.
- **Never edit** `tools/asset-spike/asset_lib.py` or `tools/asset-spike/SpikeViewer` (another session uses them; reach `asset_lib` only via `photo_lib`). Report library bugs instead of patching. Leave `tools/asset-viewer/` code alone unless the task is the viewer.
- No logos, wordmarks or QR codes (invent plate numbers). No photo pixels in textures; colours come from spec.json.
- Reference photos are CC BY / CC BY-SA: credit every one in `RunnerGame/CREDITS.md`. Only add assets we may share.
- Tests: `python -m unittest discover -s RunnerGame/Art/tests -p "test_*.py"`; Blender tests `blender_test_*.py` via the BL command.

## 6. Start checklist (e.g. Hannover wheelie bin)

1. `mkdir -p RunnerGame/Art/assets/bin_hannover/{ref,previews}`; search Commons with curl; write `titles.txt`.
2. `fetch`, `sheet`; view only the sheet; tag views and keys; credits → **Gate A** incl. detail level, facing side, camera_z_range.
3. Ruler; sections in refs.json; one 1:1 grid per section; profiles + features + landmarks + colours into `spec.json`.
4. Fill in `builder_brief.md` → sonnet builder (props face −Y; lid as its own part if it should move); prove its new tests can fail.
5. `compare.py --fit` once, then `--sections` rounds until no section shows a double image → **Gate B**.
