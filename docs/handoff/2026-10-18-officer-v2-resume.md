# Resume: realistic Ordnungsamt officer v2

Saved at user request on 2026-10-18, about 23:51 Europe/Berlin. **User explicitly asked to stop for now. Do not resume modeling until they ask.** No background Blender or curl processes were present at the pause check. No commit or push was requested or performed.

## User intent and accepted direction

The project is Hannover Rush Hour in `cgi-min-26-27`. We built, iterated and installed a stylised fictional Ordnungsamt pursuer (v1). The user now wants a **separate, substantially more realistic v2**, with actual human anatomy, correct hands/fingers, realistic shoes and good proportions, suitable for reuse elsewhere. Merely shrinking eyes or adjusting the existing primitive-based figure is insufficient.

Latest clarification, verbatim:

> i want an actaull persentaion of human correct shoes and hands propations to be actaully good and can be used otherwise if you think its better we can get an exsiting model of human and modify it

We recommended using an existing human base mesh and modifying it. The user has authorised choosing an existing base if that is better. No need to ask that choice again. Existing character intent: stocky adult man, no cap, navy service clothing with pale blue shirt, moustache/short hair, shoulder radio and clear ORDNUNGSAMT lettering. Uniform is Hannover-inspired artistic approximation; Hannover's actual service uses "Stadt Hannover Ordnungsdienst". Keep recognisability, but humour should come from attitude and movement, not distorted anatomy.

Do not overwrite v1 while developing v2. Start with a dressed neutral-pose v2 preview to evaluate anatomy, hands and footwear before a new run cycle. Clothing/skin, rigging, exports and new v2 preview have **not** been built yet.

## Existing v1, complete and approved

- Source: `RunnerGame/Art/assets/ordnungsamt_pursuer/`.
- Runtime installed: `RunnerGame/Assets/Models/Charakter/Ordnungsamt/`.
- Runtime has eight `CHR_Ordnungsamt_run_01.obj` through `_08.obj`, shared `CHR_Ordnungsamt.png`, and `CHR_Ordnungsamt_animation.json` (10 files total).
- 11,542 triangles per pose, shared 1024-square atlas, eight 100 ms frames (0.8-second loop), Blender -Y / engine +Z facing, same origin for every pose. Frames 3 and 7 have 0.035 m flight clearance.
- User approved revised run poses and baked engine result, then approved runtime installation.
- Game pose-switching logic **is not implemented**. Manifest describes frames; it does not animate the game by itself.
- `build.py`: primitive-based neutral character. `running_preview.py`: revised joint-chain geometry and eight art-directed running phases. `export.py`: reduce base once, clone it for poses, use fixed topology/UVs and preserve smooth flags, bake one atlas, export all OBJ poses. `check_export.py`: verify actual exported data, create review sheet/GIF/ZIP.
- Important outputs: `previews/engine_review.png`, `previews/engine_run.gif`, `ordnungsamt_model_pack.zip`.
- `RunnerGame/Art/ASSETS.md` and `RunnerGame/CREDITS.md` updated. Runtime copies matched source hashes; all 10 were verified in game build output.
- Most recent `dotnet build CgiMin.sln --no-restore`: success, 0 warnings/errors (an earlier nonincremental build reported the known pre-existing unused `_texture` warning in RunnerGame/Program.cs). Asset-viewer build: 0 warnings/errors. Python photo tools: 14 tests passed.
- Independent reviewer checked actual exported topology/UV equality and engine images, caught smoothing loss on later poses; fixed and independently rechecked. Remaining v1 visual limitations include segmented shoulders and stylised anatomy; v2 is intended to address the latter properly.

## Chosen v2 foundation: official MakeHuman / MPFB

Research selected **MPFB 2.0.18**, the official MakeHuman Blender human generator. Core base mesh/targets/skins and official system asset pack are CC0; addon source code has its own software licence. Verify any additional community assets individually. Do not equate software and asset licences.

Authoritative sources:

- https://github.com/makehumancommunity/mpfb2/releases/tag/v2.0.18
- https://static.makehumancommunity.org/mpfb/faq/use_in_closed_source.html
- https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html
- https://github.com/makehumancommunity/mpfb2/blob/master/script_samples/index.md

### Downloads already completed; do not re-download

Stored in repository-local `.model-research/`:

- `mpfb2-v2.0.18.zip`: **45,601,989 bytes**, readable ZIP, 3,114 entries. Source extracted to `.model-research/mpfb2-2.0.18/`.
- `makehuman_system_assets_cc0.zip`: **280,737,770 bytes**, readable ZIP, 517 entries. Asset pack **not extracted yet**. ZIP entries start directly with `skins/`, `clothes/`, etc.; no wrapper directory.
- Source download URL: https://codeload.github.com/makehumancommunity/mpfb2/zip/refs/tags/v2.0.18
- Asset download URL: https://files.makehumancommunity.org/asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip

ZIP central directories were read successfully at pause; full CRC scan was not run. Source ZIP extraction verified paths remain inside `.model-research/` before extraction. Apply the same traversal check before extracting asset pack into a dedicated subdirectory.

Useful verified paths inside asset ZIP:

```text
clothes/male_worksuit01/male_worksuit01.mhclo
clothes/shoes01/shoes01.mhclo
clothes/shoes02/shoes02.mhclo
hair/short04/short04.mhclo
eyebrows/eyebrow001/eyebrow001.mhclo
eyes/low-poly/low-poly.mhclo
```

These are candidates, **not visually approved selections**. Inspect clothing/shoe thumbnails before choosing. The official pack also has multiple male casual suits, several shoe styles, male skins, eyes, hair and teeth. Choose actual footwear geometry that fits an officer; do not repeat v1's inflated primitive boots.

## Successful Blender 5.2 compatibility check

Blender executable:

```text
C:\Program Files\Blender Foundation\Blender 5.2\blender.exe
```

Research script: `.model-research/inspect_human.py`. It **successfully ran with exit code 0** before pausing. Captured output:

```text
HUMAN_READY 19158 18486 (1.1211267709732056, 0.47323888540267944, 1.7260947227478027)
RIG_READY [('Human.rig', 53)]
Blender 5.2.2 LTS
```

Those counts are the generated base including helper data, not final visible game-mesh counts. Default generated height was ~1.726 m; choose/normalise v2 scale deliberately. This inspection generated a body and a 53-bone game-engine rig in memory and then exited; **no human scene was saved and no v2 model exists yet**.

Command (from repo root):

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --python-exit-code 1 --python .model-research/inspect_human.py
```

### Bootstrap lessons: use successful script, not failed earlier attempts

- MPFB not installed globally as an enabled addon. We import its downloaded source through `sys.path` in a headless Blender process.
- Bare `import mpfb; mpfb.register()` failed because its preferences entry did not exist. Successful bootstrap registers `MpfbPreferences`, creates a temporary `bpy.context.preferences.addons.new()` entry with module `mpfb`, assigns `entry.preferences.mpfb_user_data` to `.model-research/mpfb-user`, then calls `mpfb.register()`.
- It prints a duplicate preference-class registration warning (expected from this source-only bootstrap) but completes.
- `bpy.utils.extension_path_user` is wrapped **inside the research process only** to route package `mpfb` to workspace-local `.model-research/mpfb-user`. No downloaded addon source files were edited.
- First failed attempt's logger tried to create `%APPDATA%/Blender Foundation/Blender/5.2/mpfb/` and hit sandbox permissions. Retried with explicit approval as required; it created initial log/config files there, then failed due missing preferences entry. Successful bootstrap subsequently keeps config/log/cache in workspace. No global Blender preferences were saved.
- Don't use a live shared Blender MCP scene for these builds. Live MCP had been disconnected earlier; headless executable works.

### Relevant source APIs already read

`src/mpfb/services/humanservice.py`:

- `HumanService.create_human(mask_helpers=True, detailed_helpers=True, extra_vertex_groups=True, feet_on_ground=True, scale=0.1, macro_detail_dict=None)`.
- `HumanService.add_builtin_rig(basemesh, 'game_engine')` (successful).
- `HumanService.add_mhclo_asset(path, basemesh, asset_type='Clothes', subdiv_levels=1, material_type='GAMEENGINE', ...)` supports fitting clothes/eyes/hair to base and rig.
- `HumanService.set_character_skin(path, basemesh, skin_type='GAMEENGINE')`.
- `TargetService.get_default_macro_info_dict()` supplies complete macro dictionary.

Inspection selected `gender=1.0, age=.55, muscle=.48, weight=.57, height=.5` as **initial test parameters**, not final approved proportions. Preserve hand and facial topology; avoid aggressive decimation before visual checks.

Official examples are in `.model-research/mpfb2-2.0.18/script_samples/`. In particular `10_complete_character_export_fbx.py` shows base, skin, rig, eyes, brows, lashes, teeth, hair, clothing and export preparation. Our engine needs OBJ+PNG, so adapt its construction process, not its FBX runtime format.

## Next steps after user resumes

1. Read this handoff and the successful inspection script; do not redo licence/download research.
2. Create separate `RunnerGame/Art/assets/ordnungsamt_pursuer_v2/` for v2 work. Document chosen base/source licences and current intent. Keep v1 runtime assets intact.
3. Safely extract official system asset pack to `.model-research/system-assets/`. Inspect relevant thumbnails/contact sheet for realistic shirt/jacket/trousers, black duty shoes, short hair and skin.
4. Use successful MPFB bootstrap and actual human base, fit clothing/shoes/body parts via MPFB. Use a proper armature for later posing rather than v1's ad hoc limb reconstruction.
5. Render a **fully clothed neutral-pose character**, plus closeups of hands, face and shoes, to verify actual anatomical improvement. Do not claim photorealism just because the base is from MakeHuman. Check scale, fingers, limb lengths, clothing intersections and footwear silhouette.
6. Let user review v2 appearance before producing its animation/export set. Retain the cap-free navy Ordnungsamt direction unless they steer otherwise. A slightly larger triangle/texture budget may be justified for anatomy, but agree before replacing runtime assets.
7. Later bake/export OBJ static poses compatible with engine, independently review, show baked engine result before installation (photo-to-model Gate C). No runtime skeletal animation exists.

## Constraints and workspace hygiene

- C#/OpenTK engine: OBJ + PNG, ignores MTL, no skeletal animation. Export normals/UVs, triangles, Y-up/-Z forward. Character desired Blender -Y / engine +Z.
- `.claude/skills/photo-to-model/SKILL.md` and its builder brief are available; adapt honestly for an existing human base rather than pretend this is measured replication of a specific person.
- Shared `tools/asset-spike/asset_lib.py` and `tools/asset-viewer/` should not be edited for character work. Existing helpers can be read/imported.
- `Example/` is lecturer reference; leave unchanged. Avoid engine changes for this asset task.
- Work is uncommitted. Last pause check showed tracked modifications to `RunnerGame/Art/ASSETS.md` and `RunnerGame/CREDITS.md`; many officer/research files may be untracked/ignored. Do not clean, reset, delete or blindly stage the repository. `.claude/settings.local.json` existed as unrelated user configuration earlier.
- No need to keep any process running. The source archives, successful script and this handoff are enough to resume offline character construction.

Suggested resume message: **"Read docs/handoff/2026-10-18-officer-v2-resume.md and continue the realistic officer v2 from the MakeHuman base."**
