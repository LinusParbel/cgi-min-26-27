# Officer v2 final export candidate

## Installed after approval

User inspected the interactive engine viewer and said "okay llooks good". Gate C is satisfied. `install.py` installed all 40 poses, atlas and manifest (42 files) into the existing `RunnerGame/Assets/Models/Charakter/Ordnungsamt/` directory with the established `CHR_Ordnungsamt` prefix. The old 10-file runtime is backed up and hash-verified under `checkpoints/runtime_v1_before_v2_install/`. Runtime hashes and all 42 build-output copies were verified. `dotnet build CgiMin.sln --no-restore` succeeded: 0 errors and the pre-existing Program.cs CS0649 unused `_texture` warning. `previews/runtime_installation.json` records evidence. ZIPs and asset register/credits updated. Gameplay pose switching is still not implemented; no engine code, commits or pushes changed. The following preparation notes describe the earlier pre-approval boundary.

User approved the corrected-hand GIF and said "this looks good lets finish things off". Prepared a game export and portable editable sources. Source appearance/motion are approved; baked engine-view approval before runtime installation is the remaining photo-to-model Gate C. Existing v1 runtime remains unchanged. No engine/shared-tool edits, commit or push.

## Deliverables

Folder: `RunnerGame/Art/assets/ordnungsamt_pursuer_v2/`.

- `ordnungsamt_v2_game_pack.zip`: 40 OBJ poses, shared opaque 2048-square texture, animation manifest, per-pose viewer manifests, validations/hashes, provenance, README, actual engine GIF and review image.
- `ordnungsamt_v2_editable_source.zip`: packed neutral and approved animated Blender files, source artwork/provenance, asset-local scripts/README, approved source GIF.
- `previews/engine_run.gif`: actual OBJ+PNG rendered by existing engine viewer, fixed game-camera crop, 40 uniformly timed 20 ms frames, 800 ms.
- `previews/engine_review.png`: baked three-quarter, side and back.
- `out/CHR_OrdnungsamtV2_run_01.obj` through `_40.obj`, 73,710 triangles each. Source about 160,092 triangles. This is substantially heavier than v1's 11,542 triangles/pose and needs a budget decision before runtime replacement.
- Shared `CHR_OrdnungsamtV2.png`, `CHR_OrdnungsamtV2_animation.json`; Y-up, engine +Z facing, metres, common origin with source studio floor shifted to ground zero.

## Reproduction

1. `export.py` (headless Blender) loads approved animation without modifying either source. Reduces small rigid fittings, hair/mouth/clothing in memory; face and hand topology retained. Samples moustache curves, makes opaque cutout geometry for hair/brows. Captures deterministic evaluated geometry and fixed triangulation, bakes one 2048 atlas with shared asset_lib, exports all 40 frames with identical UVs/topology. Saves separate `officer_v2_export_preview.blend`.
2. `check_export.py` validates actual exported data, timing, atlas opacity and source hashes.
3. Existing `tools/asset-viewer/bin/Debug/net10.0/AssetViewer.exe` renders per-pose manifests. Five angles for pose01, fixed game view for all40. `assemble_export_review.py` builds review artifacts.
4. `package_export.py` packages and performs ZIP CRC tests.

## Verification and review

- Export/check scripts exited 0: all40 poses match topology/UV layout, valid finite indices/normals, no floor penetration beyond 1 mm tolerance, opaque2048 atlas, 800 ms cycle, unchanged source SHA256.
- Existing viewer loaded all40 poses successfully; multi-phase game-camera contact sheet inspected.
- Independent read-only reviewer (photo-to-model skill) passed candidate with no must-fix issues. All40 OBJs: zero degenerate triangles; unit normal error at most 0.000084; UV range [0.004018,0.995982]. Five pose01 angles preserve face silhouette, hands, carrier/equipment/cargo/boots.
- Presentation differences: engine's uniform material looks glossier than Blender; opaque/reduced facial hair appears more stippled. No claim of pixel-identical appearance.

## Remaining boundary

Show the actual baked engine view to the user for Gate C approval before installing over v1. Game pose-switching remains unimplemented; animation JSON describes timing but does not implement gameplay playback. This task does not authorize committing/pushing or modifying the engine.
