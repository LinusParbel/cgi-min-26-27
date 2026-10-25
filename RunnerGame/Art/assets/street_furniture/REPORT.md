Approved and installed2026-10-23; source/runtime SHA256 verified via docs/art/street-props-install-plan.json.

# Street furniture candidate — 2026-10-23

Three independently placeable original generic props, not replicas: timber/steel bench, thick concrete planter with opaque shrub, and 6 m streetlamp. Editable source `editable.blend`, authored dimensions `spec.json`, reproducible `build.py`, independent `verify.py`, `finish_export.py`, one opaque 1024 PNG and three triangulated OBJ files. No external models, photos, branding, alpha, installation or commits. Shared tools read-only.

## Actual output and verification

5728 exported triangles: bench 2128, planter 1836, lamp 1764. Evaluated source including bevel modifiers totals 5856; 128 collapsed serialized bench bevel triangles were filtered without removing nonzero-area surfaces. Actual independent OBJ parsing verifies finite positions/UVs, unit normals, valid indices, nondegenerate triangles, UV atlas range, bounds, zero manifest pivots and fully opaque 1024 texture. Reports: `out/geometry_checks.json`, `out/export_checks.json`.

Source bounds metres: bench X±.9, Y[-.28,.347994], Z[0,.861875], seat top .45; planter X/Y±.4625, Z[0,1.278642], concrete body .8; lamp X±.18, Y[-1.32,.18], Z[0,6.001]. Origins at ground: bench centred between feet, planter centred under base, lamp centred under mast foot. Source Z-up/front-Y exports engine Y-up/front+Z. Manifest pivots all zero. `bake_offsets.json` records original bake layout X0/12/24m; offsets subtracted from deliverable vertices, keeping 6m mast isolated during AO bake.

Prebake source checks evaluate actual modifiers and geometry budget. Structural checks inspect seat/rail contact, each prop ground-contact geometry, planter soil height, four walls/rim bars, lamp curved-arm and lens components, leaf reversed-winding faces, and no positive-area top rim intersection. Missing seat/rail/soil/rim/arm and raised-foot negative fixtures must fail. Shrub consists of 288 small double-sided opaque leaf polygons (576 triangles), not alpha cards.

## Exact commands / native results

From repository root, PowerShell. Blender 5.2.2 LTS, 8 threads, 32 samples.

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --threads 8 --python-exit-code 1 --python RunnerGame/Art/assets/street_furniture/build.py -- --export
python RunnerGame/Art/assets/street_furniture/finish_export.py
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --threads 8 --python-exit-code 1 --python RunnerGame/Art/assets/street_furniture/build.py
python RunnerGame/Art/assets/street_furniture/verify.py
& tools/asset-viewer/bin/Debug/net10.0/AssetViewer.exe RunnerGame/Art/assets/street_furniture/out/review_bench.json RunnerGame/Art/assets/street_furniture/previews/bench '35' --pitch 23
& tools/asset-viewer/bin/Debug/net10.0/AssetViewer.exe RunnerGame/Art/assets/street_furniture/out/review_planter.json RunnerGame/Art/assets/street_furniture/previews/planter '35' --pitch 28
& tools/essential-scene/bin/Debug/net10.0/EssentialScene.exe RunnerGame/Art/assets/street_furniture/previews/lamp_scene.json RunnerGame/Art/assets/street_furniture/previews/lamp_complete.png
```

Final commands exit0. First export verification failed on collapsed bevel triangles, corrected by deterministic serialized-OBJ filtering. One initial bake and one visible-blocker correction bake: initial wall tops coplanar with rim produced dark stripes; lowered wall tops .04m. Reviewer identified corner overlap; parent authorized UV-preserving endbar trim (.75→.725m), source parity update and re-render, without third bake. Saved editable source before each bake, and refreshed after final source parity/check changes. Two native helper bake passes per atlas are internal colour/AO stages of one shared-atlas invocation.

## Views and limits

Individual engine images: `previews/bench_35.png`, `previews/planter_35.png`, `previews/lamp_complete.png`. The earlier AssetViewer `lamp_35.png` is cropped by its automatic tall-asset framing; use complete EssentialScene image. Self-view shows grounded feet, distinct slats/arms, inset soil/rim and moderate open shrub. The lamp has geometric head/lens only; it emits no actual scene lighting. Tiny rim junction shading remains plausible baked AO after UV-preserving trim. Leaf cards are small opaque diamond polygons with both windings, deliberately stylized at close range; no species claim. Single atlas limits extremely close inspection of timber grain and mast hardware. Independent review is recorded separately in REVIEW.md.
