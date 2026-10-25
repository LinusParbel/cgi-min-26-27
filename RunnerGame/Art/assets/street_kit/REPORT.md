Approved and installed2026-10-23 after user desktop-preview approval; runtime files verified against docs/art/essential-install-plan.json.

# Street kit candidate - 2026-10-22

Completed original generic modular street, five OBJ parts, one opaque 2048 x 2048 PNG. Source is editable `street_kit.blend` (saved before destructive atlas bake), `build.py`, and `spec.json`. No photo pixels or external assets. Not installed into runtime and not committed.

## Contract and measured output

68 triangles total: road 12, pavements 12 each, curbs 16 each. Overall source bounds X [-5.75,5.75], Y [-10,10], Z [-.12,.15] m. Road X [-3.75,3.75] and top Z0. Each pavement totals 2 m including its .18 m curb. Pavement main slabs cover X [-5.75,-3.93] and [3.93,5.75]. Curb top has a 3 cm chamfer toward road. The five pivots are [0,0,0]. Blender Z-up/Y longitudinal exports to engine Y-up/-Z longitudinal. Translate next module 20 m source +Y / engine -Z.

Checks authored before builder, then run before export: five names, actual transformed mesh bounds, 7.5 m drivable width, .15 m sidewalk height, exact snap planes and <=3000 triangle budget. Export checks independently parse OBJ: all triangles nondegenerate; finite positions, UVs and unit normals; valid indices; UVs within atlas; five resolvable files and zero pivots; 2048 PNG header. Both reports in `out/*checks.json` PASS.

## Exact commands and results

From repository root, PowerShell:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --python-exit-code 1 --python RunnerGame/Art/assets/street_kit/build.py -- --export
python RunnerGame/Art/assets/street_kit/verify.py
& tools/asset-viewer/bin/Debug/net10.0/AssetViewer.exe RunnerGame/Art/assets/street_kit/out/ST_Street_parts.json RunnerGame/Art/assets/street_kit/previews/engine '0,45,90' --pitch 55
python RunnerGame/Art/assets/street_kit/preview_repeat.py
& tools/asset-viewer/bin/Debug/net10.0/AssetViewer.exe RunnerGame/Art/assets/street_kit/out/ST_Street_repeat_parts.json RunnerGame/Art/assets/street_kit/previews/repeat '45' --pitch 70
```

All exit 0. Blender 5.2.2 LTS; one initial and one correction `photo_lib.bake_shared_and_export` call, 2048 atlas / 32 samples. Only warning: Blender `Material.use_nodes` deprecation for Blender 6.0. No shared tools altered.

## Preview and self-review

Engine views `previews/engine_0.png`, `engine_45.png`, `engine_90.png`. Two consecutive modules `previews/repeat_45.png`, produced by review-only `out/ST_Street_repeat_parts.json`. Self-inspected oblique single and repeated view: continuous road and curb, consistent lane divider dashes and paving phase; no gap, overlap width or lane obstacle at join. Pattern periods divide 20 m: dash 5 m, curb joints 1 m, paving .4 m; asphalt noise maps Y to sine/cosine period 20 m. The joint at module boundary can remain faintly perceptible in pavement due to unique-atlas filtering and AO at closed module caps. No visible road crack in engine repeat view.

## Review correction batch

Independent review identified the single centre stripe as a blocker for the approved three lanes. Corrected to two 0.12 m dashed divider stripes at X -1.25 and +1.25 m, defining three 2.5 m lanes within 7.5 m road. Added an independent numerical evaluator of the actual production shader math graph: samples both stripe interiors/edges, rejects centre and lane-centre paint, verifies dash gaps and matching longitudinal end phases. The shader assertion runs before geometry/bake. Geometry dimensions now come exclusively from spec.json; verifier constants remain independent contract expectations and no longer supply production geometry. One correction export uses the same exact build command above. No geometry budget/bounds change.

Limitations: no junction, drain or crossing variants; paving joints, grain and painted markings are atlas detail rather than geometry. Straight rigid modules only. Source colours were not boosted to compensate for older renderer lighting.
