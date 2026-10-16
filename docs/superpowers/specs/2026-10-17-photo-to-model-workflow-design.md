# Photo-to-Model Workflow — Design

**Date:** 2026-10-17 · **Status:** draft, agreed in brainstorming · **First asset:** Voi e-scooter (2022 generation)
**Related:** game design `docs/superpowers/specs/2026-10-16-hannover-rush-hour-design.md`,
spike notes `tools/asset-spike/README.md`

## 1. Why

The asset spike showed that Claude can build props in Blender through Python (the 120 L wheelie bins),
but every model started from zero and its quality depended on how well that one chat went. The results
look like clean generic CG rather than the real object. The user wants a way to turn **photos of a real
object into a believable model** that is our own work: no external 3D generators (Rodin, Tripo, Meshy,
TRELLIS), no paid services. The workflow must be repeatable, so that the user, Linus or a later Claude
session produce the same quality every time, and reusable for the next Hannover assets (bin, tram,
Kröpcke clock, building fronts).

The key idea is to replace "Claude guesses from a description" with **measured data plus a visual
comparison loop**: a model is rebuilt from a measured spec sheet and compared against the reference
photos from the same camera angle until the outlines match.

## 2. Goals, non-goals, anti-goals

**Goals**
- A repeatable 7-step workflow (section 4) from reference photos to OBJ + PNG in `RunnerGame/Assets/`.
- A project skill that walks Claude through the steps, and a small Python helper library that does the
  mechanical parts.
- First result: a Voi-style e-scooter (2022 generation) that is recognisably that scooter from the game
  camera, ready for the v0.2b asset milestone (until 8 Nov 2026).

**Non-goals**
- External 3D generation services or paid APIs. (ChatGPT was only mentioned as an example of a helper
  we *could* use; it is not part of this workflow.)
- Using photo pixels as textures (keeps licensing simple; see section 6).
- The rider, the officer or any character; animation other than spinning wheels.
- Parked scooters as street props or obstacles, scooter clusters, and how the rider sits on the
  scooter (user, 2026-10-17: player scooter only for now; decide those later).
- Colour variants ("skins"): one Voi-coloured scooter only (user, 2026-10-17).
- Engine changes. A normal-map material is a separate, later topic.
- Map / OSM / 3D-city-model data for buildings. That is a likely second input type for this workflow
  and gets its own design when we get to building fronts.

**Anti-goals (failure even if everything technically works)**
- A scooter that could be any brand: generic proportions, wrong colours.
- A process that only works inside one particular chat and cannot be re-run from the repo.
- A model so heavy it hurts the frame rate (the engine has no batching or instancing).

## 3. Constraints

- Engine: OBJ only (positions, normals, UVs), `.mtl` ignored, one material = one PNG per draw,
  no sRGB conversion, no normal maps yet. Export settings verified in the spike:
  `forward_axis='NEGATIVE_Z', up_axis='Y'`, 1 unit = 1 m, triangulated.
- Facing: the player scooter drives towards −Z in the engine, so the model faces **+Y in Blender**
  (spike result).
- Blender 5.2 LTS with the `mcp-for-blender` add-on (port 9876). Blender scripts must look shader nodes
  up by type, never by name.
- Team: two Blender beginners, so the user's job is judging and approving, not modelling.
- The system Python (3.10) has an outdated certificate store: downloads must go through `curl`, not
  `urllib`.
- Public repo: everything committed must be redistributable. No Voi logo or wordmark on the model.
- Time: no fixed time box yet. The user decides on a limit and a fallback after seeing the first
  results (Gate B). Until then, build the thinnest working path first.

## 4. The workflow

Each step produces a file in the asset's folder, so the work survives across chats and can be re-run.

### Step 1 — Reference pack
Collect free-licensed photos (Wikimedia Commons first), pick the useful ones and tag each with its
view: `side_left`, `side_right`, `rear`, `rear_34`, `front_34`, `top`, `detail_<part>`. Store downscaled
copies (long side ≈1600 px) plus `refs.json` with title, author, licence, source URL and view tag per
photo. Credits go into `RunnerGame/CREDITS.md`.
**Gate A:** the user approves the photo pack (right model generation, enough angles).

Known data for the scooter: about 25 usable photos of the 2022 generation exist on Commons
(Hannover 2022, Liverpool 2022 series, Frankfurt 2024 close-ups of handlebar and rear). No straight
top or front view exists; the 3/4 views cover those. Voi publishes no dimensions; 10-inch wheels
(Voiager 5 listing) serve as the scale reference.

### Step 2 — Measurements → spec sheet
Use a known size (here: wheel diameter) as the ruler and measure the rest from the clearest side photo:
wheelbase, deck height, length and width, stem angle and height, handlebar height and width, the size
and position of the stem box, the fenders and the lights. Colours are sampled from the photos
(averaged over a clean patch, converted to linear RGB, avoiding highlights and shadows). The result is
`spec.json`: named dimensions in metres, angles in degrees, colours, plus each value's source
(photo + note) so later corrections are traceable.

To read pixel positions accurately, a helper renders a photo with a labelled pixel grid and can zoom
into regions; Claude marks points on these images instead of guessing from a full photo.

### Step 3 — Rough model from the spec sheet
`build.py` reads `spec.json` and builds the model from simple parts. A correction means changing a
number and rebuilding, never hand-editing geometry. Named landmark points (axle centres, handlebar ends,
stem top, deck corners, rear light) are created as empties; step 4 uses them.

### Step 4 — Comparison loop (the core)
For each tagged reference photo:
1. **Camera fit:** mark the same landmarks in the photo (with the grid helper), then solve for the
   Blender camera (position, rotation, focal length) that projects the model's landmarks onto them,
   e.g. a least-squares fit in numpy. If the fit is poor, fall back to adjusting the camera by hand
   with `look` until wheels and deck line up.
2. **Overlay:** render the model from that camera and produce a comparison image: photo | render, and
   the render's outline laid half-transparent over the photo.
3. **Diff:** Claude lists concrete differences ("stem 5° too steep", "stem box 4 cm too short",
   "rear fender ends too early") and corrects `spec.json`, then rebuilds.

The loop runs only on a few key photos (my call): one clean side view and one rear 3/4 view for the
outline, then one or two close-ups per detail area in step 5. It does not run on all ~25 photos.
**Build order (my call):** the thinnest path comes first, with the camera adjusted by hand via `look`
plus the overlay images. The landmark camera solver is built only if the manual fitting turns out
too slow or imprecise.
Repeat until no difference is visible at game-camera distance, at most about 5 rounds per photo. The
comparison images are kept in `previews/` as a record.
**Gate B:** the user approves the rough outline (side + rear 3/4 overlay).

### Step 5 — Details by camera priority
The game camera sits behind and above the rider, so detail goes in this order: rear (light, reflector,
German insurance plate, fender), deck (grip surface, rails), handlebar (grips, brake levers, display
block, bell), stem box and kickstand. Front and underside stay simple. The comparison loop from step 4
is reused for close-up photos.

### Step 6 — Materials, bake, export
Procedural Blender materials in the sampled colours (paint, rubber, plastic, metal), with optional
Poly Haven CC0 textures for grip tape or rubber. Bake colour × AO into **one shared 1024² PNG** used by
all parts. Export three OBJs: body, front wheel, rear wheel (wheel origins on the axle so the game can
spin them). Budget: body ≤ 8,000 triangles, each wheel ≤ 1,000. The body's origin sits on the ground
between the two wheel contact points.

### Step 7 — Engine check
Render the OBJs with the course engine (extend `tools/asset-spike/SpikeViewer` or a successor) from a
"game camera" preset (behind and above, at play distance) and from the reference photo angles, and
place the screenshots next to the photos.
**Colour handling (my call):** the PNG is stored sRGB-encoded (normal PNG), matching the game spec's
RunnerLit material (texture → linear → lighting → gamma). Until RunnerLit exists, the viewer copies
that gamma-correct handling so the approved look matches the game. The final check repeats in the game
once RunnerLit is in.
**Gate C:** the user approves the in-engine look; files go to `RunnerGame/Assets/`.

## 5. Packaging

- **Project skill** `.claude/skills/photo-to-model/SKILL.md`: the seven steps, the three gates,
  stop rules, file layout, commands and known pitfalls (axes, scale, node lookup by type, licences,
  no logos, curl for downloads). Anyone running Claude Code in this repo gets the same process.
- **Helper library** (Python, plain `bpy` + numpy + Pillow) covering the mechanical parts:
  reference download and downscaling, grid/zoom images, landmark empties, camera fit, overlay
  comparison images, finishing (join, smooth, UV), bake, OBJ export with the verified settings,
  triangle and size report. It builds on the shared `tools/asset-spike/asset_lib.py` (materials,
  primitives, bake + export, previews), which another session's construction-site props use. That
  file and `SpikeViewer` are therefore **imported or used, never edited**. New helpers live in
  `RunnerGame/Art/lib/`, and the multi-part viewer is a new project. Merging both libraries is a
  later cleanup.
- **Execution:** each build must run **headless** (`blender --background --python ...`) so anyone can
  rebuild an asset without the MCP. The MCP is used interactively for `look` and quick checks.
- **Per-asset folder** (one folder per asset, my call instead of the scattered `Art/scripts`,
  `Art/previews` layout in the game spec):

  ```
  RunnerGame/Art/
    lib/                      helper library
    assets/scooter_voi/
      ref/                    downscaled reference photos
      refs.json               licence + view tag per photo
      spec.json               measured dimensions, colours, sources
      build.py                builds the model from spec.json
      previews/               comparison and engine images
    ASSETS.md                 register of assets and their status
  RunnerGame/Assets/          runtime OBJ + PNG only
  ```

## 6. Licensing

Commons photos are CC BY / CC BY-SA. We use them as references and for colour sampling only; no photo
pixels go into textures, so the model and its PNG are our own work. The downscaled reference copies in
the repo stay under their original licences and are credited in `RunnerGame/CREDITS.md` and
`refs.json`. Poly Haven textures are CC0. No Voi logo, wordmark or QR code is modelled.

## 7. Left to the builder

- Exact helper-library API and module split.
- Camera-fit maths (DLT, PnP or iterative optimisation) and its "poor fit" threshold.
- How comparison images are composed (Pillow or the Blender compositor).
- The game-camera preset values until the real gameplay camera exists.
- Exact skill wording, as long as it covers section 4's steps, gates and stop rules.

## 8. After the scooter

Run the same workflow on the wheelie bin (to compare against v3) and then on the next Hannover assets.
Building fronts will need a second input type (map data: OSM outlines and heights, Lower Saxony's
open 3D building models) — separate design.
