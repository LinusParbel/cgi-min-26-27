# Next street props ready for visual review

The previous essential batch is installed and hash-verified. This new batch adds five original generic props, exported and independently reviewed but awaiting user visual approval before installation.

| Prop | Triangles | Atlas | Source/export folder |
|---|---:|---|---|
| Timber/steel bench |2128|1024shared|RunnerGame/Art/assets/street_furniture|
| Concrete planter + shrub |1836|1024shared|RunnerGame/Art/assets/street_furniture|
| Curved-arm street lamp |1764|1024shared|RunnerGame/Art/assets/street_furniture|
| Visual pothole patch |528|512|RunnerGame/Art/assets/pothole|
| Opaque-leaf street tree |11516|1024|RunnerGame/Art/assets/street_tree|

Total17772triangles for one of each prop. Each folder has reproducible sources, editable Blender files, actual-export checks and review evidence. The furniture kit has three independent ground origins; place selected parts separately. Tree branches/leaves use actual opaque geometry with4000opposed triangle pairs verified after export. Pothole is a visible overlay above the opaque road, not excavated terrain. The lamp has a lens mesh and no active illumination.

Full course-engine scene: `previews/street-props-engine.png`, built using `street-props-scene.json` and unchanged renderer/materials. Tree is on the pavement beyond the final building bay, avoiding crown/building intersections. Pothole is in front of the barrier so it remains visible. The scene is static art review; gameplay logic is not implemented here.

Closeups are under each asset's previews folder: bench_35.png, planter_35.png, lamp_complete.png; pothole/road.png; street_tree/engine.png. Inline tool images are not visible to this user, so open the combined scene in the desktop image viewer.

Verification on2026-10-23: all3actual-export verifiers exit0,14photo-tool tests pass, solution and review-tool incremental builds pass0warnings/errors (existingCS0649 known from clean solution rebuild). Final independent review:2026-10-23-street-props-final-review.md. No commits. Runtime delivery list/hashes prepared in street-props-install-plan.json; not installed yet.


Approved and installed2026-10-23 after user replied "okay" to reopened visual review. All14runtimefiles match the source SHA256 delivery list. Gameplay integration is separate. No commits.
