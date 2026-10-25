Read docs/handoff/session-context.md first, then continue.# Session context (compaction summary for Claude)

## User and goal

- Student (Windows, repo `C:\Users\Saturn\Desktop\Studium\Master\ws_26_27\CGI\cgi-min-26-27`), uni CGI course, C#/OpenTK engine,
  runner game "Hannover Rush Hour". Team of 2 Blender beginners, deadline ~late Nov 2026, AI use fully allowed.
- Core goal of this session: build and continuously improve the project skill **`/photo-to-model`**
  (`.claude/skills/photo-to-model/SKILL.md` + `builder_brief.md`) by modelling real Hannover objects with it. Every model is a
  test run; every mistake that costs rounds becomes a rule/tool/test in the skill; then commit.
- User preferences: no external 3D generators or paid services; realistic, recognisable replicas; token-cheap work
  (scripts → haiku for text sorting → sonnet builder/reviewer agents → main session measures/judges; one image per round;
  ≤ 3 agents); often says "loop until perfect, don't ask" — then loop, but always SHOW results (open images with
  `cmd //c start "" "<path>"`, or the viewer) before installing. Replies short, plain language.

## Ground rules

- Branch `feature/photo-to-model` (user: keep it, don't merge). Commit messages end with
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Push is impossible from here: GitHub 403 (account `Ar000sh`
  lacks write access to `LinusParbel/cgi-min-26-27`) and Claude Code's classifier blocks pushes — user must push himself.
- Another session owns `tools/asset-spike/` (asset_lib.py, SpikeViewer, baustelle) and is working on
  `RunnerGame/Art/assets/ordnungsamt_pursuer/`, `.model-research/`, and has uncommitted edits in `RunnerGame/Art/ASSETS.md`
  and `RunnerGame/CREDITS.md`: never edit or commit those; stage only our own paths.
- Blender: `"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup --python-exit-code 1 --python <file>`.
  Headless only, absolute output paths, never `mcp__blender__*` for builds. Downloads via curl (old Python cert store).
- Scratch helpers in `C:/Users/Saturn/AppData/Local/Temp/claude/.../c710d44d-.../scratchpad/` (`signed_k.py` = signed
  landmark errors ref/04 with level+shift fit, `signed_k01.py` = ref/01, `starts.py` = multi-start camera fit).

## Tools (ours, all tested)

- `RunnerGame/Art/lib/photo_tools.py`: fetch / sheet / grid / color / measure / **crops** (2× crop per part per key photo
  → `A/previews/crops/crop_<part>_<NN>.png`). Unit tests 14/14.
- `RunnerGame/Art/lib/photo_lib.py`: Spec, landmark, tube, arc_shell, match_camera, project_landmarks,
  fit_camera(z_range, shift, level), compare_image(zoom, sections), part_sheet, bake_shared_and_export. Blender tests 12/12.
- `RunnerGame/Art/lib/compare.py -- A ref/NN.jpg [--fit] [--zoom] [--sections]` and `-- A --part <name>`
  (one part, all key photos with camera, one image: photo | model colour | 50/50 blend).
- `tools/asset-viewer`: `dotnet run --project tools/asset-viewer -- <parts.json> <prefix> 0,35 --pitch 5` or `--show`.

## Skill workflow (current)

Gate A (photos + detail level backdrop/medium/replica + facing + camera_z_range) → parts with the same names in every
key photo, measured as profiles on 1:1 grids → sonnet builder from filled `builder_brief.md` with the part crops → main
session proves each new test can fail by mutating BUILD code (`# MUTATION`, check it reaches geometry, restore) →
`--fit` per key photo → `--part` loop worst part first until no double image → Gate B → details/export → read-only sonnet
review + one fix batch → Gate C → install to `RunnerGame/Assets/Models/<Category>/<Asset>/`.

## History of lessons (already in SKILL.md "Mistakes that cost extra rounds")

- Scooter (installed): need a true side view; perspective bias; sunlit colours too light; viewer far plane; token routing;
  builder/reviewer loop; stop format; adaptive loop limits.
- Rathaus (installed, Maschteich front, ~24.5k tris): agree detail level first; outline RMS is blind inside the silhouette
  → blend/zoom/sections; camera height range; profiles + shape vocabulary instead of one number per part; tests can be blind.
- Kröpcke (in progress): mutate build not spec; test surfaces (ray cast, plane slice, relative builds), not vertices; loop
  on BOTH key photos; close-from-below photos hide set-back parts; slope vs top only when two views agree; never
  extrapolate a cut-off ground; zoom 1:1 before counting (8 legs → 4, tall dome → low); glass: sample reflections in
  ≥ 2 photos, bake gradient + streaks + recessed pane; parts workflow (user's idea).
- Proposed but not built (user chose hand corrections): a joint fit of key dims + both cameras.

## Current task: Kröpcke-Uhr (`RunnerGame/Art/assets/kroepcke_uhr/`, prefix `PRP_KroepckeUhr`, replica, ≤ 25k tris, 2048²)

- Photos: ref/04 (straight front, key, lens_shift, cut at bottom), ref/01 (3/4, key), ref/02, ref/05 (scale).
  Parts in refs.json: top, head, glass, legs. Cameras: ref/04 close level shift camera (~8.8 m, 42 mm), ref/01 far.
- Model ~24k tris, 26/26 tests (each verified RED/GREEN). RMS ref/04 10.5 px (1.0 %), ref/01 23.8 px (2.0 %).
- Done parts: glass (user approved), head (arched hood, bezel, roman numerals), top (one sideways medallion ring; dome a bit
  low/flat in ref/01 accepted). Legs/base accepted by user earlier; **`previews/part_legs_r1.png` rendered, not yet evaluated.**
- The builder subagent (sonnet, id a2fe7a6ab62f60864) is resumed via SendMessage with exact spec changes, 1–2 crop images,
  "do not commit", tests measuring built geometry.
- Last commit: `9bbfdc5` (handoff doc). Long handoff: `docs/handoff/2026-10-18-photo-to-model-handoff.md`.

## Next

1. Evaluate part_legs_r1, fix, re-check. 2. Read-only review → Gate C (engine view vs both photos).
2. Install to `Models/Wahrzeichen/KroepckeUhr/` (ASSETS.md row only after the other session's edits are resolved — ask).
3. Add new lessons to SKILL.md, commit; remind user to push. 5. Next model to test the skill (user picks).
