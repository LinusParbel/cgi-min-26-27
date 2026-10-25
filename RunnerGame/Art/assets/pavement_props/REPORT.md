# Pavement props candidate

Completed original generic rack/table/chair, pending independent parent review. No installation or commits. All changes confined to RunnerGame/Art/assets/pavement_props.

Outputs: out/PROP_Pavement_rack.obj (612 triangles), out/PROP_Pavement_table.obj (596), out/PROP_Pavement_chair.obj (924). One shared opaque out/PROP_Pavement.png, 1024x1024. Combined unique triangles2132; table plus two chair instances2444, well under6000. Manifest out/PROP_Pavement_parts.json; per-prop review_rack.json/review_table.json/review_chair.json alongside it. Editable source editable.blend; reproducible builder build.py; deterministic serialized face cleanup finish_export.py (zero faces removed).

Actual OBJ verifier verify.py validates finite positions, all triangle indices, nonzero triangle area, UVs in0..1, unit normals, independent dimensions, grounding, centred pivots, triangle budgets and opaque atlas. out/export_checks.json records results plus rejected raised-ground, UV-range, zero-normal, invalid-index and collapsed-triangle fixtures. verify_source.py evaluates component bounds, tests rack/plates, chair legs/bearers/slats/posts/boards and table top/support/pedestal/base contacts, grounded pads, .45seat top. out/structural_checks.json records rejected missing rack tube, chair bearer/post, table pedestal and raised chair foot fixtures. These are bounding-box contact checks, not stress/physics analysis.

Dimensions source XYZ: rack .15 x .88 x .8, table .7 x .7 x .74, chair .45 x .465782 x .821017. Rack long axis sourceY/engineZ. Chair faces source-Y/engine+Z. All pivots zero at pavement level; chair back projects .035782m farther than front. Source Z-up exported engineY-up using photo_lib conventions. Source rack mesh has smooth quarter-bend progression, continuous hollow-profile sweep closed at ends; two surface anchor plates. Table has four radial splayed feet. Chair has four legs, bearer rails, five seat boards, three back boards and a front stretcher.

One 32sample bake invocation at1024 with8threads; components separated at X0/4/8m for bake, offsets removed for export. After bake, rack rotated90degrees into requested sourceY alignment and its terminal rings lowered .01m into the plates to eliminate a .005m source gap. UVs unchanged; source build and editable.blend updated to match geometry. No rebake needed for these small rigid/terminal changes; this limits exact AO accuracy at the concealed tube ends. Future full build generates final geometry directly. Atlas did not require another bake. Source-only refresh option avoids rebaking.

Commands (root PowerShell):
- Blender5.2 blender.exe --background --factory-startup --threads8 --python-exit-code1 --python RunnerGame/Art/assets/pavement_props/build.py (actual flags have spaces: --threads 8, --python-exit-code 1)
- same Blender command --python .../build.py -- --source-only refreshes editable source without bake
- same Blender command --python .../verify_source.py
- python RunnerGame/Art/assets/pavement_props/verify.py
- tools/asset-viewer/bin/Debug/net10.0/AssetViewer.exe <review_manifest> <preview_prefix> 35 --pitch 23
- tools/essential-scene/bin/Debug/net10.0/EssentialScene.exe RunnerGame/Art/assets/pavement_props/previews/scene.json RunnerGame/Art/assets/pavement_props/previews/engine_complete.png

All final checks exit0. Native viewer sheet previews/engine_sheet.png inspected: rounded rack silhouette, supported round table and coherent slatted chair. Automatic AssetViewer framing crops the nearest chair foot slightly; use complete scene previews/engine_complete.png for full foot visibility. Complete engine scene inspected too; muted colours, clear geometry and full bounds visible. Parent should show its GUI scene to user; inline images are not the user's viewing surface. A first scene JSON failed parsing due to .4 literal; corrected to0.4, final native render exit0.


Installation closeout 2026-10-23: user approved the live batch (good). All eight runtime files installed and SHA256 verified. Full runtime scene: docs/art/installed-street-scene.json. Gameplay integration remains pending.
