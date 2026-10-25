# Commuter bicycle continuation

## Installed after final approval

User approved the baked engine viewer with "looks good". Five runtime files
installed into `RunnerGame/Assets/Models/Fahrzeug/BikeCommuter/` and hash-checked
against export. All five build-output copies hash-verified. Solution build
`dotnet build CgiMin.sln --no-restore` passed with 0 warnings/0 errors. Asset
register, credits, source/package README and ZIPs updated. Evidence:
`previews/runtime_installation.json`. No engine changes, commits or pushes.
Gameplay placement and wheel animation remain unimplemented. Historical
pre-approval notes below are superseded by this installation status.

## Latest: baked export ready for engine-view approval

User inspected source preview and said "looks good move on". GateB satisfied.
Exported body/frontwheel/rearwheel with shared opaque2048 atlas using existing
photo_lib. Actual15,720tri (7,680body+4,020eachwheel), within25k. Export includes
applied bevels vs15,240 source geometry count. `check_export.py` passed actual
OBJ indices/normals/UV bounds/nondegeneracy, axle pivots/radius/wheelbase/floor,
texture opacity and records hashes in `out/validation.json`. Existing engine
viewer rendered six angles into previews/engine_*.png. Independent review
passed all files/images with no mustfix; normal error<.000079, UVrange
[.005345,.994655], no degenerate triangles. Fine spokes/cables alias in small
engine screenshots. No runtime installation yet; GateC engine view pending.

Game/source ZIPs packaged and CRC-checked by `package_export.py`:
`bike_commuter_game_pack.zip` (~2.6MB), `bike_commuter_editable_source.zip` (~2.4MB).
Review sheet `previews/engine_review.jpg`. Interactiveviewer opening for user
review with `out/VEH_BikeCommuter_parts.json --show`. Next: user approves baked
view, then install5 runtimefiles (3OBJ+PNG+partsmanifest) into
`RunnerGame/Assets/Models/Fahrzeug/BikeCommuter/`, update ASSETS/CREDITS status,
build and verify output hashes. No commits/enginechanges. Historical notes below.

User switched from approved/installed officer v2 to "continue the new model for bike". They want active progress and became frustrated with perceived waiting. The existing `bike_commuter` spec identifies navy Batavus Blockbuster Plus, replica level, 25k triangles/2048 texture/front -Y. Optional direction clarification offered navy photo build vs old imports; no different direction received, so continued the existing photo design. Do not redo that question.

## Existing and new work

- Folder: `RunnerGame/Art/assets/bike_commuter/`.
- Prior rough `bike_bushido.glb`, `pybullet/`, `assemble_pybullet.py` and previews preserved; none of their geometry incorporated. Their redistribution licences are not established here.
- Main wrote `measure_reference.py` and expanded existing `spec.json` from local public-domain refs03/04. Original JSONs backed up in `checkpoints/before_photo_build_*.json`.
- Assumed 1.08m axle ruler, wheel diameter0.68m. Pixel conversion at axle plane1.08/782, roll correction using axle line. Widths/hidden detail inferred; not a measured factory replica. Corrected placeholder brown saddle to black, bright navy paint to near-black navy.
- Photo-to-model skill explicitly requested builder delegation; builder implemented local scripted geometry in `build.py`, no imported geometry. Editable `bike_commuter.blend`; preview `previews/build_contact_sheet.jpg` (right side + front34).
- Parts body/frontwheel/rearwheel, wheel pivots on axles. 36 thin crossed wire spokes per wheel, rims/hubs, diamond frame/curved fork, full mudguards/struts, enclosed chaincase, sculpted black saddle, swept chrome handlebar/grips/levers/bell/cables, tall-backed front cargo rack/rear rack/supports, cranks/pedals, lights, twin centre stand.
- Refinement batch rounds chaincase/rack corners, adds silver crank cover and inset strip, improves saddle contour, extends rear mudguard tail below axle. A subsequent final check found saddle/rail/post gaps; builder fixing physical supports before final preview.

## Camera and tests

Correct reference viewing side is -X, not +X. Front=-Y means rider right=-X, so `chaincase_x=-.073`. Main fixed build pedal offset to use abs(chaincase_x), changed preview cameras to-X, and corrected measurement script cameras/spec for reproducibility. Original wrong-side fit04 r1 is invalid and retained only as history.

- Correct fit04 r2: RMS10.6px/1600 (0.66%), frame joints mostly1.7-10px; max26px at approximate wheel-bottom landmark. Camera saved in refs.
- Fit03 r1: RMS9.2px/1600 (0.57%), max14.2px at approximate saddle landmark. These are sparse landmark fits, not proof all outlines match.
- Both comparison sections images generated and side04 inspected. Frame/wheels broadly aligned; details refined afterwards without changing axle/frame layout.
- `blender_test_bike.py`: actual built geometry budget/floor/wheelbase, spokes slenderness/count, tyre/rim dimensions, landmark coverage, rack supports, stand feet, real ray-cast frame/wheel openings.
- Main added `--mutate-spokes`: modifies build source in memory to generate one fewer spoke. Observed FAIL at spoke-count assertion. Fresh normal test after first refinements PASS14,832 tris (body6,792,wheels4,020each), floor0, wheelbase1.08000003,36spokes. Final saddle support fix requires fresh normal test/updated count.

## Next boundary

Final saddle support correction is complete and saved. Post/riser/clamp/shaped rails now connect into saddle underside; actual BVH surface interval tests passed after catching and correcting a front rail outside the narrow saddle nose. Latest count15,240 triangles (body7,200, wheels4,020 each). Refreshed source and preview saved. Main independently reruns the full geometry test before delivery. No remaining builder processes.

Inspect final saddle support fix and preview. Record latest triangle count. Present concrete side/34 silhouette for photo-to-model GateB before atlas bake/export. No bake, runtime install, engine/shared-tool edits, commit or push performed for bike. Continue details/export/engine review after shape approval; intended exports one shared2048 atlas with body/front/rearwheel OBJs. No external downloading is needed to resume.
