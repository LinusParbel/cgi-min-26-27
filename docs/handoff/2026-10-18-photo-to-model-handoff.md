# Handoff: photo-to-model workflow and the Kröpcke-Uhr (2026-10-18)

Context for a new session. Read this first, then `CLAUDE.md` and `.claude/skills/photo-to-model/SKILL.md`.

**How we work:** the real goal is the **skill** (`/photo-to-model`). We improve it by modelling real Hannover
objects with it: every model is a test run, and every mistake that costs extra rounds becomes a rule, a tool
feature or a test in the skill (see the "Mistakes that cost extra rounds" table in SKILL.md). So after each
model (or each lesson), update SKILL.md / `builder_brief.md` / the tools, then **commit and push** the branch.

## 1. Project and user

- Repo `cgi-min-26-27`: minimal C#/OpenTK course engine (`Engine/`) plus our uni game `RunnerGame/`
  ("Hannover Rush Hour", 3-lane endless runner). Team of 2 Blender beginners, deadline ~late Nov 2026.
  Grading includes our own 3D models; AI use is fully allowed.
- The user wants **realistic, recognisable Hannover models**, no external 3D generators or paid services,
  **token-cheap** work (right model per step, few images, ≤ 3 parallel agents), and is happy to say
  "loop until perfect" — but always show the result before installing.
- Branch: **`feature/photo-to-model`** (not merged; user said "keep the branch for now"). Commit only on request
  or at natural checkpoints as done so far; end commit messages with
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Another session owns `tools/asset-spike/` (`asset_lib.py`, `SpikeViewer`, `baustelle/`, `WORKFLOW.md`):
  **import, never edit**. We own `RunnerGame/Art/`, `tools/asset-viewer/`, `.claude/skills/photo-to-model/`.

## 2. What exists (all committed except the Kröpcke work in progress, see §5)

| Thing | Where |
|---|---|
| Design + plan | `docs/superpowers/specs/2026-10-17-photo-to-model-workflow-design.md`, `docs/superpowers/plans/2026-10-17-photo-to-model-workflow.md` |
| Skill (the workflow) | `.claude/skills/photo-to-model/SKILL.md` + `builder_brief.md` (shape vocabulary for the builder agent) |
| Photo tools (system Python + Pillow) | `RunnerGame/Art/lib/photo_tools.py` — `fetch` (Commons via curl, staged + retried, stable file names), `sheet`, `grid`, `color` (median → linear RGB), `measure` |
| Blender tools | `RunnerGame/Art/lib/photo_lib.py` — `Spec`, `landmark`, `tube`, `arc_shell`, `match_camera`, `project_landmarks`, `fit_camera(..., z_range, shift, level)`, `compare_image(..., zoom, sections)`, `bake_shared_and_export` |
| Compare CLI | `blender ... --python RunnerGame/Art/lib/compare.py -- <asset_dir> ref/NN.jpg [--fit] [--zoom x0,y0,x1,y1] [--sections]` → overlay, 50/50 blend, per-section sheet (photo · model · blend) |
| Engine viewer | `dotnet run --project tools/asset-viewer -- <parts.json> <prefix> game,0,35 [--pitch 5]` or `--show` (gamma-correct, clip planes scale with size) |
| Tests | `python -m unittest discover -s RunnerGame/Art/tests -p "test_*.py"` (13); Blender: `blender_test_photo_lib.py` (11), `blender_test_scooter.py` (10), `blender_test_rathaus.py` (13), `blender_test_kroepcke.py` (20) via `"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup --python-exit-code 1 --python <file>` |
| Register / credits | `RunnerGame/Art/ASSETS.md`, `RunnerGame/CREDITS.md` |
| Installed models | `RunnerGame/Assets/Models/Fahrzeug/ScooterVoi/` (body + 2 wheels), `RunnerGame/Assets/Models/Wahrzeichen/NeuesRathaus/` |

Assets so far: Voi scooter (done), Neues Rathaus Maschteich front (done, ~24.5k tris, 2048²),
**Kröpcke-Uhr (in progress)**. Build outputs `RunnerGame/Art/assets/*/out/` are git-ignored.

## 3. How the workflow runs (short)

1. Commons search → `fetch` → contact sheet → **Gate A** (photos, detail level backdrop/medium/replica, facing side, `camera_z_range`).
2. Sections in refs.json; measure **each section on a 1:1 grid**; profiles (width at several heights), features with own widths; every spec value has a `source`.
3. Sonnet **builder agent** writes `build.py` from the filled-in `builder_brief.md`; it never commits.
4. Main session **proves every new test can fail** by breaking the BUILD code (`# MUTATION` line, then restore) — mutating spec.json proves nothing; check the mutation actually reaches the geometry (e.g. a variable read before the mutation line).
5. `compare.py --fit` once, then `--sections` rounds (one image per round) on **both key photos** until no double images → **Gate B**.
6. Details → export → engine view → independent sonnet **reviewer** (read-only) → one fix batch → **Gate C** → install.

## 4. Lessons that cost rounds (keep applying them)

- One photo cannot tell a horizontal top surface from a slope, nor see parts set back above the camera (close photos from below hide domes and place ball/finials too low). **Always loop on ≥ 2 key photos from different angles.**
- Read coarse grids carefully; the "tall dome" and "8 legs" were misreadings — zoom 1:1 on the part before modelling.
- Colours: overcast photos give usable samples; sunlit ones are too bright; horizontal metal tops look lighter (sky sheen) → separate `iron_top` colour. Verify with the baked texture median vs the photo (numbers, no image).
- Camera fit wanders to a far telephoto when measurements were made assuming no perspective; `level=True` + `shift=True` exist for shift-corrected photos. **Open idea: a joint fit** (solve key dims + both cameras together) — proposed twice, not built; the user preferred hand corrections.
- A reviewer can be wrong (e.g. called a measured table "too wide") and right (sloped table top) — weigh findings against the measurements.

## 5. Current task: Kröpcke-Uhr (`RunnerGame/Art/assets/kroepcke_uhr/`)

- Photos: `ref/04.jpg` (straight front, key, shift-corrected, cut off at the bottom), `ref/01.jpg` (3/4 view, key),
  `ref/02.jpg` (head detail), `ref/05.jpg` (people, used for the scale). Credits are in `RunnerGame/CREDITS.md`.
- Detail level **replica** (≤ 25k tris, 2048²), front faces −Y, square plan, four identical faces.
- Prefix `PRP_KroepckeUhr`, single part `body`; build with
  `"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup --python RunnerGame/Art/assets/kroepcke_uhr/build.py -- --export`.
- Current model (~18.2k tris, height 6.11 m): stone slab + moulded iron plinth, **4 corner legs** (square, waisted,
  ribbed), apron, table fascia + slope (`iron_top`), body with pilaster figures/stars, stepped showcase frame,
  medallions, flared brackets, four dials with stepped hood rings, head box, cornice + frieze (lattice, swags, stars,
  ribbed corner blocks), **square ribbed cloister-vault dome** with hip ropes and volutes, neck, banded ball,
  two crossed medallion rings with gold trefoil, beaded rod.
- Committed with this handoff: base re-proportioned from ref/01 (legs 0.42–1.05 m, table to 1.46 m,
  body foot 1.635 m), everything above lifted +0.31 m, cooler glass colour, two tests made spec-driven
  (`test_four_corner_legs_waisted`, `test_showcase_frame_steps`). All 20 Kröpcke tests green; both rewritten tests
  verified RED with a build mutation and GREEN after restore. Engine sheet: `previews/current_state_4.png`.
- The user's last verdict: "looks good, go on with the rest" (legs and base accepted).

### Next steps
1. (Done) The Kröpcke changes are committed.
2. Run `compare.py --fit --sections` on ref/04 **and** ref/01; fix remaining double images (body width vs the slender
   glass case in ref/01, dome height, head height) — numbers first, one sheet per round.
3. Show the user `previews/` engine-vs-photo sheet (open it with `cmd //c start "" "<path>"`), then independent review, Gate C.
4. Install to `RunnerGame/Assets/Models/Wahrzeichen/KroepckeUhr/`, add a row to `RunnerGame/Art/ASSETS.md`,
   `dotnet build CgiMin.sln` (one pre-existing warning in `RunnerGame/Program.cs` is not ours).
5. Update the skill with the Kröpcke lessons (§4): two key photos in every round, close-from-below photos hide set-back
   upper parts, slope vs top surface, check that mutations reach the geometry.
6. Still open from earlier: the branch merge decision (keep / merge / PR) — ask the user.
