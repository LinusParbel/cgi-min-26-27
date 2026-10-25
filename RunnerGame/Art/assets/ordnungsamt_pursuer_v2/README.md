# Ordnungsamt officer v2 — dark uniform and protective vest preview

Separate development asset for Hannover Rush Hour. This is a clothed neutral A-pose review, not a finished game export. The approved v1 and its runtime files remain unchanged.

## Construction

- Official MakeHuman MPFB 2.0.18 human mesh, game-engine armature, anatomical hands and face.
- Official system assets: `male_casualsuit01` adapted into a closed navy jacket and duty trousers, `shoes03` duty boots, `short01`, `eyebrow001`, low-poly eyes, base teeth and middle-aged Caucasian male skin.
- Navy jacket, pale blue inner neckline, fitted duty belt with closed pouches, shoulder microphone and coiled lead, conforming pockets/shoulder tabs, Hannover sleeve shields, two-line city identification patches.
- Current revision adds a **separate external protective vest** over that uniform: smooth padded front/rear shells, bound edges, shoulder bridges and hook-and-loop overlaps, two side fastening bands per side, front zip, authority patch, upper zip pockets, front pocket flaps, radio mounting/coiled lead and lower rear reinforcement. Vest labels read `ORDNUNGSAMT`, following the user's supplied photo. Covered jacket labels/pockets are retained but hidden. Flat cargo pockets were added to the trouser thighs.
- Black leather boots with rubber soles, crossed laces and eyelets; boot uppers narrowed beneath trouser cuffs.
- Short textured hair, wider jaw/chin, age targets and subtle facial creases, individual tapered moustache hairs.
- Body macros: male 1.0, age .63, muscle .50, weight .62, height .57. These are generator parameters, not physical measurements.

`build.py` runs `build_refined.py`, generating `officer_v2.blend` and eight renders in `previews/`. `-- --draft` reduces resolution and samples. `generate_textures.py` reproduces the identification label and vector-derived sleeve artwork. The workspace-local MPFB bootstrap and extracted assets under `.model-research/` are required to rebuild. The Blender scene packs image textures for portability. The earlier anatomy build is retained as `build_anatomy.py` and its Blender checkpoint is in `checkpoints/anatomy_preview.blend`.

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --python-exit-code 1 --python RunnerGame/Art/assets/ordnungsamt_pursuer_v2/build.py
```

## Licensing / provenance

The MakeHuman base/targets and official system assets used here are CC0. The downloaded system asset OBJ/MHCLO headers explicitly record the September 2020 CC0 release and identify Data Collection AB, Joel Palmius and Jonas Hauquier. MPFB software licensing is separate from generated asset licensing. No community wardrobe assets were added. The incorporated Hannover coat of arms is a public-domain vector from Wikimedia Commons; see `source/provenance.json` for author, source, copyright status and reference-photo usage. No reference-photo pixels are incorporated in textures.

Sources already selected in the October 18 handoff:

- https://github.com/makehumancommunity/mpfb2/releases/tag/v2.0.18
- https://static.makehumancommunity.org/mpfb/faq/use_in_closed_source.html
- https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html

## Review limits

`verify.py` reopens the saved scene, checks the 53-bone rig, packed textures, six rendered views, front zipper placement and clearance of the back identification panel. `previews/validation.json` records evaluated geometry counts (including curves/facial hairs) and bounds. This is a source preview budget, not an agreed runtime budget.

For the vest revision it also checks both carrier labels against their own shell surfaces, garment clearance across shell vertices, padded torso clearance, separate shoulder bridges/side bands and front zip placement. `vest.py` can rebuild the vest from `checkpoints/pre_vest.blend` for faster iteration; the normal `build.py` includes it automatically. Detailed front/side outputs are `previews/vest_front.png` and `previews/vest_side.png`. The source-only vest has no functional protective properties; it is a game model.

The visible navy uniform, sleeve insignia, two-line labels, shoulder fittings and dark footwear follow Hannover photo references. This is a modeled interpretation, not a measured garment replica: source photographs show several different seasonal outfits and do not resolve exact footwear model, tread, stitching or pouch layout. The face is fictional and not a likeness of a photographed officer. The approved run attaches rigid equipment to corresponding moving bones. Source hair uses alpha cards; the export candidate trims transparent regions into opaque hair/brow geometry for the engine. See the final export section for current delivery status and limits.

The latest user correction establishes the Dortmund-style dark outer carrier as the intended silhouette. Its rear follows the supplied photo; the front is informed by comparable real municipal carriers (center zipper, identification patch, flapped pockets and radio mount), not claimed as a verified exact Dortmund issue model. The result is a fictional composite over the retained navy uniform/Hannover sleeve shields. No cap was added to the existing cap-free character. See the vest section of `source/provenance.json`.

## Running animation preview

`previews/officer_v2_run_natural_hands.gif` (also copied to `officer_v2_run.gif` and `officer_v2_run_smooth.gif`) is a 40-frame, 0.8-second in-place run shown from synchronized three-quarter and side cameras. GIF timing is uniformly 20 ms per frame (50 fps). Editable animation: `officer_v2_run_preview.blend`. The neutral `officer_v2.blend` is unchanged (SHA-256 checked).

The hand orientation uses an anatomical frame from wrist-to-middle-knuckle and pinky-to-index landmarks. This explicitly keeps the thumb side uppermost and the hand aligned with the forearm, correcting the previous unconstrained palm-down roll. Wrist secondary motion is limited to 2 degrees. `verify_hands.py` checks all 41 keyed poses: maximum wrist angle 1.993 degrees and minimum thumb-up alignment 0.9799 (1 is exact alignment).

`animate_run.py` builds an IK-solved leg cycle, opposite arm swing, relaxed fingers, torso lean/counterrotation and foot lift. The pelvis follows a smooth analytic path; each ankle handles its own evaluated skinned-sole correction. The planted ankle travels backward at constant speed, with continuous swing transitions. Elbow flex changes through the stride and the wrist has a small secondary lag. Rigid equipment follows its appropriate chest/pelvis/head/arm/foot/thigh bone; existing MPFB weights drive body and clothes. `verify_run.py` checks all 41 keyed poses including the duplicate endpoint: sole contact within 1 mm, knee bend above 12 degrees, unchanged bone lengths, correct equipment transforms and zero loop seam error. `make_run_gif.py` uses a shared palette and verifies 40 frames, uniform timing and 800 ms duration. Reports live under `previews/run/`.

Frame analysis identified the old end-of-step body jolt: pelvis peak acceleration about 47.9 m/s² and wrist peak about 53.9 m/s², plus alternating 30/40 ms GIF timing. The revised cycle measures about 5.88 m/s² pelvis and 20.08 m/s² wrists, with a steady 2.125 m/s planted-ankle speed and uniform 20 ms GIF frames. `analyze_run.py` measures saved-rig trajectories; `check_motion_smoothness.py` guards against those jolts and timing regressions. The old GIF remains at `previews/run/run_before_smoothing.gif`.

The appearance and corrected-hand run were approved on 2026-10-20. The carrier remains rigid; there is no cloth simulation.

## Final approved export

`out/` contains 40 matching-topology OBJ poses, one opaque 2048-square atlas and a 20 ms/frame animation manifest (800 ms loop). Prefix: `CHR_OrdnungsamtV2`. Each pose has 73,710 triangles, substantially heavier than v1. `export.py` reduces small fittings, hair and hidden mouth detail in memory, preserves face/hand topology, converts alpha hair/brows to opaque geometry and shifts the studio floor to game ground zero. Neutral and approved animated source hashes are checked unchanged. `check_export.py` validates the actual OBJ data and PNG. `package_export.py` creates the game and editable-source ZIPs.

`previews/export_01_*.png` show the baked candidate in the existing engine viewer. Its shared material is glossier than the approved Blender render; facial hair is more stippled after opaque conversion/reduction. Independent read-only review found no blocking issues: all 40 exports have valid normals, UV bounds and nondegenerate triangles. The baked engine view was approved on 2026-10-20 and v2 is installed in RunnerGame/Assets/Models/Charakter/Ordnungsamt/, retaining the runtime CHR_Ordnungsamt prefix with 40 poses. The previous runtime is backed up in checkpoints/runtime_v1_before_v2_install/. The manifest alone does not implement gameplay animation. install.py verifies installed hashes and records previews/runtime_installation.json.

The first fitted jacket candidate was rejected because its lapels and long hem read as a blazer. The replacement retained human topology while adding a closed service front. Iterative renders caught an undershirt floating on the neck, zipper rays hitting the rear through the open collar, floating belt sections, boot uppers penetrating cuffs and separate text sinking into cloth folds. The final build closes the front before fitting accessories, uses woven label textures on dense fitted patches, smooths the belt contour and narrows hidden boot uppers. `previews/iteration_01/` preserves the rejected blazer render for comparison.
