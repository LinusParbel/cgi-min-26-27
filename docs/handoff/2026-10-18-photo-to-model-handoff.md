# Handoff: the photo-to-model skill and how it was developed (as of 2026-10-21)

Read this first, then `CLAUDE.md` and `.claude/skills/photo-to-model/SKILL.md` (+ `builder_brief.md`).

## 1. How we work

- **The real product is the skill** `/photo-to-model`. We improve it by **modelling real Hannover objects with it**:
  every model is a test run, and every mistake that costs extra rounds becomes a rule, a tool feature or a test.
  After each lesson: update SKILL.md / `builder_brief.md` / tools → run the tests → commit (and push when possible).
- The user judges the look; Claude measures, builds, tests. Three user gates per model: A (photos + detail level),
  B (outline), C (engine look). The user often says "loop until perfect, don't ask" — then loop without asking,
  but show the result (open the image with `cmd //c start "" "<path>"`) before installing.
- Token rules: scripts for mechanical work, **haiku** for text-only sorting, **sonnet** builder/reviewer subagents,
  the main session measures and judges. One image per comparison round, ≤ 3 parallel agents, numbers before pictures.
- No external 3D generators, no paid services, no photo pixels in textures, no logos. Photos from Wikimedia Commons
  (CC BY / BY-SA, credited in `RunnerGame/CREDITS.md`).

## 2. Project facts

- Repo: C#/OpenTK course engine + our runner game "Hannover Rush Hour". Team of 2 Blender beginners, deadline ~late Nov 2026.
- Branch **`feature/photo-to-model`**, not merged. **Not pushed**: GitHub refused (account `Ar000sh` has no write access to
  `LinusParbel/cgi-min-26-27`) and Claude Code's safety check blocks pushes by Claude. The user has to get access / a fork
  and run `! git push -u origin feature/photo-to-model` themselves.
- Another session owns `tools/asset-spike/` (`asset_lib.py`, SpikeViewer, construction-site props) and is currently working
  on `RunnerGame/Art/assets/ordnungsamt_pursuer/` and `.model-research/` — import/leave alone, don't commit their WIP.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## 3. The toolchain (all tested)

| Tool | Purpose |
|---|---|
| `RunnerGame/Art/lib/photo_tools.py` | `fetch` (Commons via curl; staged, retried, stable file names), `sheet`, `grid` (1:1 labelled grid), `color` (median → linear RGB), `measure`, **`crops`** (2× reference crop per part and key photo) |
| `RunnerGame/Art/lib/photo_lib.py` | `Spec`, `landmark`, `tube`, `arc_shell`, `match_camera`, `fit_camera(z_range, shift, level)`, `compare_image(zoom, sections)`, **`part_sheet`**, `bake_shared_and_export` |
| `RunnerGame/Art/lib/compare.py` | `-- A ref/NN.jpg [--fit] [--zoom] [--sections]`; **`-- A --part <name>`** = one part in all key photos, one image (photo · model colour · 50/50 blend) |
| `tools/asset-viewer` | engine render/viewer: `-- <parts.json> <prefix> 0,35 --pitch 5` or `--show` |
| Tests | `python -m unittest discover -s RunnerGame/Art/tests -p "test_*.py"` (14); Blender `blender_test_photo_lib.py` (12), `_scooter` (10), `_rathaus` (13), `_kroepcke` (26) |

Blender: `"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup --python-exit-code 1 --python <file>`.

## 4. How the skill evolved — run by run

**Run 1: Voi scooter** (installed, `Models/Fahrzeug/ScooterVoi`). First version of the workflow: photo pack → spec.json
with a source per value → parametric `build.py` → outline overlay loop → bake/export → engine check.
- Went wrong: no true side view in the first photo pack; perspective made near-face readings too big; sunlit colour
  samples too light (fenders); a far-plane bug in the viewer.
- Fixes: search again for a real side view; camera fit instead of hand-fitting; "colours from shaded areas"; viewer clip
  planes scale with model size. User asked for **token savings** → model routing, one image per round.
- User asked for **review and loops by agents** → sonnet builder + read-only sonnet reviewer, one fix batch, fixed
  stop format (matches / differs with keep-or-fix / recommendation), adaptive loop rules (stop when no improvement,
  extensions decided at the gate, hard ceiling 5 rounds).

**Run 2: Neues Rathaus** (installed, `Models/Wahrzeichen/NeuesRathaus`, Maschteich front).
- Went wrong: user rejected the first model ("not detailed enough") — the detail level was never agreed; outline RMS
  looked great while gables, towers and windows were wrong (the overlay can't see inside the silhouette); camera fit put
  the camera 25 m underground; one number per part → builder guessed pyramids/boxes/full-width pediment; a band misread
  as an eave; a test that passed with a deliberately wrong pediment.
- Fixes: **detail level at Gate A**; **50/50 blend** + `--zoom` + **`--sections`** sheets; `camera_z_range`;
  **profiles** (width at several heights) per part measured on 1:1 grids before building; **`builder_brief.md` with a
  shape vocabulary** (trapezoid stacks, lathes, flaring roofs, features with their own width); **prove every new test
  can fail**. Estimated effect: ~15 rounds → 2–3.

**Run 3: Kröpcke-Uhr** (in progress, `RunnerGame/Art/assets/kroepcke_uhr/`, replica level, prefix `PRP_KroepckeUhr`).
- Went wrong, in order: the builder's tests stayed green under spec mutations (a build-equals-spec test follows the
  spec) → **mutate the build code, not the spec**; a gap test looked only at vertices → **ray casts / plane slices /
  relative tests** (vertex tests were blind three times); looping on the front photo only hid the dome, the legs and
  the base (close photo from below) → **loop on both key photos**; a slope read once as a top surface, once as a slope →
  decide only when two views agree; the front photo is cut off at the bottom → **never extrapolate the ground**;
  "8 legs" and "tall dome" were coarse-grid misreadings → **zoom 1:1 before counting**; a mutation placed after the
  variable was read → check the mutation really changes geometry; glass sampled where exhibits showed through came
  out brown and flat → sample reflections in ≥ 2 photos, bake gradient + streaks + recessed pane; two crossed medallion
  rings where the photos show one sideways ring.
- Big structural fix (user's idea): **the parts workflow** — same-named sections (`top`, `head`, `glass`, `legs`) in
  every key photo, `crops` as the builder's reference images, `compare.py --part` as the per-part check, worst part first.
- Also added: lens shift + level camera fit for perspective-corrected photos; spec-driven tests.
- Not built (proposed twice, user preferred hand corrections): a **joint fit** solving key dimensions and both cameras
  together — it would remove the remaining two-photo contradictions.

## 5. Kröpcke-Uhr — current state

- Photos: `ref/04.jpg` (straight front, key, shift-corrected, cut at the bottom), `ref/01.jpg` (3/4, key), `ref/02.jpg`,
  `ref/05.jpg` (scale from a person). Parts defined in refs.json for 04 and 01.
- Model: stone slab, moulded iron plinth, 4 waisted ribbed corner legs, apron, table fascia + slope, body with pilaster
  figures/stars, glass with rounded valance head, bead frame and baked reflection, 4 dials with projecting arched hood,
  thick bezel and roman numerals, frieze, square ribbed cloister dome with hip ropes/volutes, banded ball, one sideways
  medallion ring with gold trefoil, beaded rod. ~24k tris (budget 25k), 2048², 26/26 tests (each verified RED/GREEN).
- RMS: ref/04 10.5 px (1.0 %), ref/01 23.8 px (2.0 %).
- Parts done: `glass` (user-approved after 2 rounds), `head` (r2), `top` (r2; dome slightly low/flat in ref/01 accepted).
  **`legs` part sheet r1 was just rendered (`previews/part_legs_r1.png`) and not yet evaluated.**

## 6. Next steps

1. Evaluate `part_legs_r1.png`, fix, re-check (`compare.py -- A --part legs`).
2. Independent sonnet review → Gate C with the user (engine view next to both photos).
3. Install to `RunnerGame/Assets/Models/Wahrzeichen/KroepckeUhr/`, row in `RunnerGame/Art/ASSETS.md`, `dotnet build CgiMin.sln`.
4. Add any new lessons to SKILL.md; commit; user pushes.
5. Optional: build the joint fit; pick the next Hannover model to test the skill on.
