# Civilian scooter rider source scout — 2026-10-22

Read-only inspection of local scripts, asset headers and existing validation. No Blender process, modelling, bake, export or runtime change was performed. Triangle figures below count OBJ face fans (`vertices_in_face - 2`) and are source estimates, not evaluated fitted exports.

## Minimum robust approach

Generate a fresh MPFB body using the bootstrap in `.model-research/inspect_human.py`, rather than stripping `officer_v2.blend`. Actual local MPFB directory is `.model-research/mpfb2-2.0.18`, not `.model-research/MPFB`. Reuse `HumanService.create_human`, `set_character_skin(..., skin_type='GAMEENGINE')`, `add_builtin_rig(body, 'game_engine')` and the small `fit()` wrapper from `RunnerGame/Art/assets/ordnungsamt_pursuer_v2/build_refined.py`. Start with a civilian macro shape and no officer-specific head targets. Fit `clothes/male_casualsuit04/male_casualsuit04.mhclo` (3,240 source triangles), or `male_casualsuit02` (4,120), plus `clothes/shoes01/shoes01.mhclo` (3,320), low-poly eyes (172), eyebrow001 (192), short01 hair (3,678 before alpha cutting). These complete outfits are tagged Casual/Male; inspect their first preview before committing to one silhouette. Retain standard civilian material textures or recolor plainly. Do not call the later officer procedural detail code, `fit_labels.refit_labels()` or `vest.add_vest()`.

The officer's casualsuit01 alone costs 16,672 source triangles; its existing final export is 73,710 triangles per pose (`out/validation.json`). It is unsuitable as the direct <=35,000 triangle starting point. Fresh low-density clothes avoid the jacket closure, patches, arms, radio, coiled lead, belt pouches, boot eyelets/laces, cargo modifications and 1,450 moustache curves entirely. A short hair mesh and painted facial detail suffice.

Keep all SUBSURF modifiers at zero in export. Keep MPFB body/helper masks and clothing delete masks active. First inspect the evaluated visible-mesh triangle total; enforce <=35,000 **after** final triangulation. Prefer preserving the original face and individually rigged fingers over global body decimation. Only reduce hidden teeth/hair/clothes as needed. Omit teeth for a closed mouth or reduce teeth_base to .15 as the proven officer exporter does: its unmodified 7,120 triangles are disproportionately expensive. Hair alpha-cut tessellation can multiply 3,678 source triangles; do not assume its input count survives. Use `export.py:opaque_cutout` carefully, or build a simple opaque scalp haircut. Eyebrow tessellation also increases its 192 input triangles. Face and fingers are part of the body, not cheap independent components; preserve their rigging and test both hand grips visibly.

## Rig and matching two-pose export

Use game_engine rig data at `.model-research/mpfb2-2.0.18/src/mpfb/data/rigs/standard/rig.game_engine.json` and `weights.game_engine.json`. `animate_run.py` demonstrates quaternion reset (`matrix_basis = Identity`), `orient()` with rest-bone roll, analytic `two_bone()` solve and an anatomical hand frame based on hand-to-middle-knuckle plus pinky-to-index axes. These are useful helper patterns; its running trajectories, -Y-facing assumptions and finger curl values are not scooter poses. Parameterize the elbow/knee pole for scooter stance and solve wrists to actual grips; rotate whole rider geometry/rig 180 degrees about Z for scooter +Y front, or consistently transform all target coordinates into the MPFB -Y local frame. MPFB anatomical `l` is +X before that rotation, whereas scooter rider-left is -X.

Build two named poses on the same rig/wardrobe with one modest stance or lean variation, maintaining grip contact in both. The officer exporter is the proven topology pattern: apply deterministic reductions/cutouts once **before** posing; sort the source objects once; capture frame A; join and triangulate once; bake one 2048 atlas with `tools/asset-spike/asset_lib.py:bake_and_export`; capture frame B using the identical object and face order and update vertex coordinates only. Assert identical vertices, faces and atlas UVs. Preserve explicit `source` UV nodes before adding atlas UVs. Its existing 2048 bake uses samples=16, ao_strength=.18, margin=8, uv_margin=.003, keep_origin=True. Replace its 80,000 assertion with <=35,000 and its 40-frame loop with two named poses. Do not copy its officer-specific +.0265 ground correction blindly: rider soles belong at deck z=.184. The exporter uses OBJ forward NEGATIVE_Z/up Y; its animation descriptor says Blender -Y / engine +Z, which needs adjustment for scooter +Y orientation.

## Scooter contact coordinates (metres, Blender Z-up)

Derived exactly from `RunnerGame/Art/assets/scooter_voi/build.py` and `spec.json`, with ground origin midway between wheel axles and front +Y:

| Contact | Coordinates / extent |
|---|---|
| Front/rear axles | (0, +.424, .127), (0, -.424, .127) |
| Grip axes | y=.2681990457, z=.982; left x=-.300 to -.170, right x=.170 to .300 |
| Grip midpoint targets | left (-.235, .2681990457, .982), right (.235, .2681990457, .982) |
| Grip radius | .018; palm/finger surfaces wrap this axis, wrist is offset by hand anatomy |
| Deck top | z=.184; y=-.291 to +.214; x=-.090 to +.090 |
| Black deck grip | x=-.080 to +.080, y=-.281 to +.204, upper surface z=.184 |

`bar_y = .424 - .117 - (.982-.534)*tan(10.1 degrees) + .041`. Suggested starting sole centers are one fore/aft tandem pair around y=.07 and y=-.14, with x near +/- .025; actual shoe length/width must determine fit. These are proposed pose targets, not existing measured landmarks. The deck is only .18 m wide; two parallel side-by-side adult shoes will overhang. Keep hands at both grip midpoints and solve shoulders/lean accordingly; do not scale scooter dimensions to fit the character. Head block reaches z=1.157 and projects rearward, so test forearm/chest clearance against it.

## Licensing evidence and source paths

`.model-research/mpfb2-2.0.18/LICENSE.md` sections C/D explicitly classify base mesh, targets, textures, MHCLO clothes, rigs, poses, expressions and mesh JSON as CC0, and explain output is the combination of these assets and creator input. `LICENSE.ASSETS.md` contains CC0 1.0 Universal; `LICENSE.CODE.md` is the separate GPL software license. Base source is `src/mpfb/data/3dobjs/base.obj`; its header explicitly records September 2020 CC0 release. Both recommended clothing `.mhclo` and `.mhmat` headers do likewise (Data Collection AB / Joel Palmius / Jonas Hauquier). The short01 MHCLO header has the same release statement. Skin source used by tested builder is `.model-research/system-assets/skins/middleage_caucasian_male/middleage_caucasian_male.mhmat`; remaining assets live under the corresponding `eyes/low-poly`, `eyebrows/eyebrow001`, `hair/short01`, `teeth/teeth_base` folders. Copy applicable license evidence and list exact adopted files in new rider provenance.

Officer `source/provenance.json` already records the official MPFB 2.0.18 system assets as CC0. It separately identifies Hannover arms artwork and photo reference material: no reason to carry any of this officer reference/artwork into a fresh civilian build. This scout relies on the locally preserved primary license documents, without a new web licensing audit.
