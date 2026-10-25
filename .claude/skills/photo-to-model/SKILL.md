---
name: photo-to-model
description: Build a recognisable 3D model of ONE specific real object (Hannover landmark, building, tram, bin, scooter, clock, vehicle, monument) from free-licensed reference photos - measure the photos by script, build in headless Blender, compare with the photos until it matches, export OBJ + PNG for the runner game. Also covers adapting a clearly licensed existing model (CC0/CC-BY) instead of building from scratch. Use whenever the user wants a real-world thing modelled or replicated from photos or references, wants an asset that must look like the real one, or says photo-to-model / "model X from photos" - even if they do not name the skill. Do NOT use for generic props where recognisability does not matter (cone, barrier, crate - use tools/asset-spike/WORKFLOW.md). Characters (people, animals) go through route B, adopting a licensed base.
---

# photo-to-model

Reference photos -> measured `spec.json` -> headless Blender build -> photo comparison -> shared-texture OBJ export -> engine check.
Worked examples (see `references/history.md`): `scooter_voi` (vehicle), `rathaus_hannover` (facade), `kroepcke_uhr` (ornate, parts workflow).
No AI 3D generators, no paid services, no photo pixels in textures, no logos; existing models only with a verified CC0/CC-BY licence. Register: `RunnerGame/Art/ASSETS.md`.

Notation: `BL` = `"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup --python-exit-code 1`;
`A` = `RunnerGame/Art/assets/<asset>`; commands run from the repo root in Git Bash; pass **absolute** output paths to Blender.

## 0. Photos always first, then the route

Every object starts with the reference photos: they tell us exactly what the real thing is (model, generation, proportions, colours), and
that makes any search for a base model far better aimed. The route is chosen at Gate A, when photos AND candidate bases are on the table.
- **Route A, photos:** measure and build from the photos. Required when the object must be recognisably THAT real thing and no candidate fits.
- **Route B, adopt a base:** start from a free-licensed model (CC0 / CC BY) that matches the photos, normalise, reduce, adjust to the photos.
  Best for organic shapes (people, animals, trees) and detailed generic categories; skips the expensive scripted shape work.
- **Hybrid:** adopt the base, then run the measure/compare loop on the parts that must match the real object.
Licence is a hard stop. Process, licence table and the officer and bike results: `references/adopt_base_model.md`.
Route B replaces steps 2-3 below; photos, classes, gates, review and export stay the same.

## 1. Choose the class and the loop (Gate A decides)

The class is the budget: every extra triangle and texel is paid in every frame and in every instance on the track, and
every extra detail is paid in rounds. Pick the cheapest class that still reads as the real object from the game camera.

| Class | For | Triangles | Texture | Loop |
|---|---|---|---|---|
| `backdrop` | far away, outline only | <= 5k | 1024² | sections |
| `medium` | main features visible | <= 12k | 1024² | sections |
| `replica` | every visible feature of the key side | <= 25k | 2048² | parts |
| `custom` | hero object; the user names the numbers | e.g. 40k | up to 4096² | parts |

The classes are defaults, not walls. The user may name any class or number at Gate A and may **raise it at any later gate**;
raising it only adds work to the parts that benefit. Animated characters ship as baked poses, so the budget is triangles per pose x poses.
Record `route`, `detail_level`, `tri_budget`, `tex_res`, `workflow`
(`"sections"` or `"parts"`) in spec.json; tests and the builder read the budget from there.

**Loop = how the work is checked, not a different method.** Both loops use the same `"sections"` boxes in refs.json.
- **sections loop** (simple or medium objects, about <= 5 distinct parts): one sheet shows all sections of the key photo at once
  (`compare.py ... --sections`). One image per round for the whole object, so it is the cheap default.
- **parts loop** (complex objects, `replica`/`custom`, or parts that differ in every photo): the same box names exist in EVERY key
  photo, parts are built and checked one at a time, worst first (`compare.py ... --part <name>`), and the builder gets only that
  part's crops. One image per part per round: it costs more images and finds what the all-in-one sheet hides.
Start with the sections loop; switch an object to the parts loop when a sections round shows the same section still wrong twice,
or when two key photos disagree about it. Details of both: `references/measure_and_compare.md`.

## 2. Flow

**1 Reference pack.** `A/titles.txt` (one Commons title per line, `File:Name.jpg`; find candidates with curl, low volume).
```
python RunnerGame/Art/lib/photo_tools.py fetch A A/titles.txt   # -> A/ref/NN.jpg (long side 1600, EXIF applied) + A/refs.json
python RunnerGame/Art/lib/photo_tools.py sheet A                # -> A/previews/ref_sheet.jpg (view only this)
```
Tag `view` (`side_left|side_right|rear|rear_34|front_34|top|detail_<part>`) and `"key": true` on 2 key photos in refs.json
(a haiku-class agent can do tags + CREDITS lines). Prune by deleting from refs.json and titles.txt.
**1b Scout bases** (cheap, text and thumbnails only): with what the photos show, search CC0/CC-BY libraries for up to 3 candidates; for each record
link, licence, triangles, and how far it is from the photos (right model? right proportions? what would change). Skip when the object is a
unique landmark. Detail: `references/adopt_base_model.md`.
**GATE A (user, ONE AskUserQuestion):** route (A photos / B adopt candidate X / hybrid, with your recommendation and the candidate's licence) - photo pack ok (right model, a true side/front view, a second angle?) - class/budget and
loop (section 1, with your recommendation) - facing side - supervision (only at the gates / also after each part) - and per key
photo `camera_z_range` from where it was taken (street ~[1,2]; across water ~[-4,6]). Stop and wait.

**2 Measure -> spec.json.** Pick a ruler, split into sections, measure each on its own 1:1 grid as a *profile* (width at 4-6
heights) plus features, read landmarks and colours, write spec.json with a `source` for every value.
Commands and formats: `references/measure_and_compare.md`.

**3 First build.** Sonnet-class builder agent with `builder_brief.md` filled in. Props face -Y, vehicles +Y. Corrections = change a
number in spec.json and rebuild, never hand-edit geometry. The main session proves each new test can fail:
`python RunnerGame/Art/lib/mutation_check.py A/build.py <test.py> <test_name> --old "<code>" --new "<code>"` (mutate BUILD code, not spec).

**4 Compare loop.** `BL --python RunnerGame/Art/lib/compare.py -- A ref/NN.jpg --fit` once per key photo (numbers first:
`--errors` prints signed landmark errors, `--errors --starts` tries many start cameras when a fit lands on a far telephoto).
Then loop with `--sections` or `--part` until no row shows a double image. **Loop on both key photos** - one view hides parts.

**5 GATE B (user): shape.** Outline/blend approved. Skipped for `backdrop`/`medium`: those get one combined B+C gate.

**6 Details + export** (sonnet builder; <= 2 rounds per detail photo). Materials from spec colours. The only bake:
```
BL --python A/build.py -- --export     # -> A/out/<PREFIX>_<part>.obj, <PREFIX>.png, <PREFIX>_parts.json
```
`bake_shared_and_export(parts, pivots, out, "<PREFIX>", res=tex_res, samples=32)`; body origin on the ground at its centre, moving
parts on their axis. Check triangle counts against `tri_budget`.

**7 Review.** One read-only sonnet reviewer against the photos (never edits): outline vs key photos; dimensions within +-10 % of
spec; facing and pivots in the engine sheet; no missing, floating or intersecting faces; colours not sunlit-bright; budgets; no
logos or photo pixels. Output: numbered list, each **must fix** or **could fix** with evidence. Must-fix -> one fix batch by the same
builder + one re-export; could-fix -> Gate C.

**8 Engine check, GATE C (user), install.**
```
dotnet run --project tools/asset-viewer -- A/out/<PREFIX>_parts.json A/previews/engine game,0,90,180   # or --show
```
Then `mkdir -p RunnerGame/Assets/Models/<Category>/<Asset>` (`Fahrzeug`, `Baustelle`, `Mull`, `Wahrzeichen`), copy `A/out/<PREFIX>*`,
`dotnet build CgiMin.sln` (no new warnings), add a row to `RunnerGame/Art/ASSETS.md`, finish `RunnerGame/CREDITS.md`.
Commit only when the user asks.

## 3. The human in the loop

The machine loops on everything measurable; the human decides what cannot be measured: what to build (A), whether the shape
is right (B), whether it looks right in the game (C). Reasons: a wrong class or photo costs the most if found late; a wrong shape
is cheap until details sit on it; "looks right" is the user's call, never the model's.
- **Gates scale with the class.** `backdrop`/`medium`: A, then one combined gate (overlay + engine sheet). `replica`/`custom`: A, B, C.
- **Part check-ins (parts loop) only on request or on escalation:** a part that hits its round limit, or that dominates the game view,
  goes to the user with "keep as is / one more round". Otherwise parts run without asking. Gate A records which supervision level the user wants.
- **Every gate is one message:** (1) what matches, one line each with the number that shows it; (2) what still differs, each as
  **keep as is / fix** with the cost in rounds, images and re-bakes; (3) your recommendation. At most one image, at most 4 decisions,
  recommendations first, so "ok" is a valid answer. Then stop. Never self-approve. Feedback = one fix batch + one re-export.
- **"Loop until perfect, don't ask":** run to the limits below without asking, but still show the result before installing.
- Agents never commit and never approve.

## 4. Roles, limits, budgets

| Step | Who | Tier | Limit |
|---|---|---|---|
| search, fetch, sheet, grids, crops | scripts | - | - |
| tags, credits (text only) | helper agent | cheapest (haiku) | once |
| sections, profiles, spec, fit, judging | main session | user's model | before any build |
| build, details, export, fixes | builder agent | mid tier (sonnet) | until its tests pass; <= 2 rounds per detail photo |
| review | reviewer agent | mid tier, read-only | one review + one fix batch |

(Model names change; the rule is: cheapest tier for text sorting, mid tier for building and reviewing, the best model only for judging
images and deciding.) At most 3 agents at once, one asset at a time.

**Loop rules (never ask mid-loop):** key photo <= 3 rounds, detail photo <= 2, part <= 3. Continue while a round cuts the error by
> ~20 % or fixes something visible; stop early when a round brings no improvement and say why. At the limit put every remaining
difference into the next gate as "keep / one more round (~1 image)". Hard ceiling 5 rounds per photo including extras - beyond that the
photo is the problem. Target: no double image in the blend and landmark RMS < ~1.5 % of photo width (leaning objects may stay higher).
One review + one fix batch; a second review only on the changed must-fix items.

**Token rules (each image is the expensive part of a round):** numbers before pictures (`--errors`, `measure`, triangle counts);
view ONE image per round and never re-read old ones; <= 4 reference photos in the loop (2 key + <= 2 details); previews in Workbench,
bake only for `--export`; briefs name exact files, the image budget and "do not commit".

## 5. Files and conventions

```
RunnerGame/Art/lib/    photo_tools.py (no bpy)  photo_lib.py (Blender)  compare.py  geom_probe.py  mutation_check.py
RunnerGame/Art/assets/<asset>/   ref/ refs.json spec.json titles.txt build.py previews/ out/
RunnerGame/Assets/Models/<Category>/<Asset>/   runtime OBJ + PNG + parts.json only
```
`<PREFIX>_parts.json` = `{"texture","parts":[{"name","obj","pivot":[x,y,z]}]}`, pivots in Blender coordinates (engine = (x, z, -y)).
Blender Z-up, 1 unit = 1 m; OBJ export forward -Z / up Y, triangulated (done by `bake_shared_and_export`); PNG sRGB, spec colours
linear; look shader nodes up by type, never by name; the engine has no normal maps, so do not brighten textures to compensate.
Tests: `python -m unittest discover -s RunnerGame/Art/tests -p "test_*.py"`; Blender `blender_test_*.py` via `BL`.
Never edit `tools/asset-spike/asset_lib.py` or `SpikeViewer` (another session uses them; reach `asset_lib` only via `photo_lib`);
leave `tools/asset-viewer/` alone unless the task is the viewer. Reference photos are CC BY / CC BY-SA: credit each in `RunnerGame/CREDITS.md`.

## 6. Read next

- `references/measure_and_compare.md` - sections, grids, profiles, spec/refs formats, compare flags (read at step 2 and 4).
- `references/lessons.md` - mistakes that cost extra rounds, as general rules (read before step 2 and when a loop stalls).
- `references/adopt_base_model.md` - route B: adopting a licensed base model.
- `references/pitfalls.md` - download, EXIF, Blender, shape pitfalls.
- `references/history.md` - what each finished model taught and what no model has tested yet.
- `builder_brief.md` - the filled-in brief for the builder agent.
- `evals/evals.json` - test prompts and the metrics to log per run.
