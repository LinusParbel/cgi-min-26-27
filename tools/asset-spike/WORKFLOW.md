# Asset workflow — cheap by design

Goal: one finished, reviewed model per asset with as few tokens, images and CPU-minutes as possible.
Everything is built by script (`baustelle/gen_*.py`, shared `asset_lib.py`), baked headless, checked in the
course engine, then **published** to `RunnerGame/Assets/Models/<Category>/<Asset>/`.

## 1. Who does what (model routing)

| Step | Who | Model | Notes |
|---|---|---|---|
| Find + download references | `fetch_refs.sh` (script) | – | ≤ 4 hits per query, polite to Wikimedia (no parallel calls) |
| Pick the best references | Agent reading **text only** (`index.tsv`) | haiku | no images; user picks from one contact sheet |
| Decide scope, specs, brief | main session | the user's model | short brief in `baustelle/BRIEF.md` style |
| Build + self-check one asset | builder agent | sonnet | headless Blender only, max 3 iterations |
| Independent review | reviewer agent | sonnet | checklist + max 6 images, **never edits files** |
| Fix review findings | the same builder (SendMessage) | sonnet | one batch of fixes, one re-export |
| Live tweaks in the user's Blender | MCP tools (`mcp__blender__*`) | main session | only for quick interactive work, not for bakes |
| Publish + commit | `publish_models.py`, git | main session | commit only when the user asks |

## 2. Image budget (images are the biggest token cost)

- References: ≤ 4 per object. Look at **one contact sheet** (≤ 12 thumbnails, 320 px), the user picks, only the
  chosen 1–3 are opened at full size.
- Builder per iteration: **one** engine sheet (`engine_sheet.sh`: 3 views in one image) + the reference crop.
  Never re-read images from earlier iterations; delete them. `render_previews(size=384)` is enough.
- Reviewer: reference + final engine sheet + at most 3 extra renders (≤ 6 images total).
- Screenshots are scratch (`out/`, git-ignored). Only OBJ + PNG (+ `mounts.json`) are published.
- Prefer numbers over pictures: bounds, tri counts, texel colours (`python -I`) beat another screenshot.

## 3. Parallelism and CPU

- ≤ 3 agents at once (5+ agents hit the API usage limit and share one CPU).
- Cycles bakes are the slow part (1–3 min alone, 6–12 min when three run together): bake once per iteration,
  `samples=32`, 1024² (512² for small props). Never bake just to look at geometry — use Workbench previews.

## 4. Steps for a new asset

1. `bash tools/asset-spike/fetch_refs.sh tools/asset-spike/ref/<name> 4 "query"` → pick 1–3 photos.
2. Write specs (real dimensions, variants, budget) into a brief; one builder agent per asset.
3. Builder: `blender --background --factory-startup --python baustelle/gen_<name>.py` (writes to `out/`),
   then `dotnet tools/asset-spike/SpikeViewer/bin/Debug/net10.0/SpikeViewer.dll <obj> <png> <prefix> 0,30,160`
   and `bash tools/asset-spike/engine_sheet.sh <prefix> <sheet.png>`.
4. Reviewer agent checks the sheet against the reference (checklist in `baustelle/BRIEF.md`).
5. `python tools/asset-spike/publish_models.py` → `RunnerGame/Assets/Models/...`.
6. Library bugs (found by agents) are fixed centrally in `asset_lib.py` — signatures stay stable.

## 5. Engine facts that avoid rework

One OBJ + one PNG per mesh, no `.mtl`, no transparency; the engine shows colours ~0.72× darker until
gamma-correct lighting exists (v0.2) — do not brighten textures to compensate.
