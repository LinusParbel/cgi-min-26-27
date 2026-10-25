# Essential asset execution ledger

Plan: docs/superpowers/plans/2026-10-22-essential-assets.md

User approved clock and next essential batch on 2026-10-22. Existing feature branch and uncommitted source assets retained. No commits authorized.

Ruling: execute approved batch without a second plan-permission round; user explicitly asked to proceed. New art candidates will be shown before installation.
Ruling: generic modular street, facade, token and unbranded compact car use original scripted construction. They are not advertised as replicas of particular real objects. Rider adopts verified local CC0 human assets.

Preflight: tasks1-6 own distinct asset folders. Task2 module dimensions feed task6 scene placement. Task3 independent floor origins feed scene stacking. Task4 vehicle orientation and task5 rider orientation are explicitly +Y; existing scooter source is consulted for fitting. Task5 consumes existing scooter read-only. Shared register changes remain with parent only. No conflicting file ownership found.

Task 1: complete. Approved clock installed; all three SHA256 hashes match Art/out. Register and approval record updated. Existing credits retained.
Task 2: complete candidate. Five parts,68tri,2048atlas. Reviewer caught two-lane markings; one correction produced dividers at x+/-1.25 for three2.5m lanes. Spec now drives geometry. Independent review PASS (street_kit/REVIEW.md). Not installed.
Task 3: facade_builder implementing three independent modules and an assembled-stack preview.
Tasks 4-6: pending. Rider scout complete: docs/art/2026-10-22-rider-scout.md; local CC0 base/clothes and exact scooter contact targets. Car/rider reference packs fetched; second rider photograph is context-only, not anatomy evidence.

Review tooling: new tools/essential-scene reuses existing engine and gamma-lit material without editing shared viewer/Engine. It will render multiple candidate textures in one street slice. Restore needed escalation after sandbox NuGet failure; approved restore succeeded. Build pending.

Review tooling built with zero warnings/errors and smoke-rendered 16 instances /11 meshes /5 textures in the course engine. An overlapping initial sandbox restore later failed; approved restore was repeated successfully to restore clean generated assets. Solution build succeeded, zero warnings in this incremental run (earlier clean baseline had existing CS0649).

Task3 pre-export correction: separated facade variants in bake layout to prevent cross-variant AO. Each exported module retains independent zero pivot. Geometry checks pass at1764tri; corrected bake running.

Ruling: execute rider (Task5) before car (Task4) once facade finishes, because its two-pose contact fitting has the greatest remaining uncertainty and source scouting is complete. Both tasks are independent; no interface changes.

Task3 reviewer found visible side-face zfighting. Builder corrected quoin depth and trim extents in both source and actual exports while preserving UVs, and added side-triangle positive-area overlap verification. Geometry passes but old atlas retains AO from removed deep trim. Corrected-source facade rebake queued after rider releases CPU. Candidate not accepted yet.

Task4 scout: Innerscene original unbranded hatchback source page explicitlyCC0; downloaded candidate SHA256/provenance and alternatives in city_car/candidates.json.130902tri raw;8,670tri body shell, wheels/hidden internals expensive. Visual inspection/reduction decision pending after current model. Original scripted fallback retained.

Ruling: publisher car preview inspected; CC0 base has suitable unbranded compact proportions and modelled features. Adopt/normalize/reduce it rather than spend modelling rounds recreating its shape. Target12k, hard18k (within approved8-18k backlog range); mirror width up to2.16m is permissible within2.5m lane. No assertion of exact Golf replication. Preserve downloaded source and licence-page evidence.

Task5 fitting: 26922tris/pose pre-bake; both poses' soles supported on deck within reported tolerance, shoe separation8.65mm, head height1.65619m ride /1.29515m duck (36.1cm drop). Parent inspected combined ride side view and found silhouette credible. Final export/bake pending.

Task5 export complete:26706tris/pose after shoe-collar trim; both poses share one2048 atlas baked from ride only. Endpoint dashboard triangle intersections zero; duck hips sourceY-.40 clears dashboard by~60.7mm nearest sampled vertex, ride~4.65mm. Handgrip surface check65/72 samples within8mm. Rider_builder running final actual-export checks/board; rider_review independently reviewing. Candidate uninstalled.
Task3 final corrected-source rebake running at8threads after rider released bake slot. No additional geometry/cosmetics queued.

Current task status:1 installed/complete;2 candidate complete/reviewPASS;3 rebake then scopedreview;5 exported/finalreview;4 car adaptation next;6 token and fullscene pending. New candidates await batch visual approval before installation.

Task5: candidate complete, independent structural/visual reviewPASS,35source hashes verified. Parent rendered ride and duck separately with actual courseEngine/GammaLit via essential-scene and inspected both; no blocking appearance issue. Scoped reviewer engine addendum pending. CREDITS updated. Only one pose in each scene; two resident meshes cost53412tri, one atlas.
Task3 corrected-source rebake complete, source/export1764tri; canonical stack/side previews refreshed; scopedindependentre-reviewpending.
Task4 car_builder adapting licensed base now; CPU bake slot available to that builder only.

Task3: candidate complete, independent scoped final reviewPASS after corrected-source bake. Side AO/zfight resolved; three588tri modules /1764total,2048atlas, normalizedzero pivots. Final review dated2026-10-23.
Task5: reviewer inspected both actualEngine screenshots as addendum; PASS retained, no blockers. Engine paths docs/art/previews/rider-{ride,duck}-engine.png.
Task4: reduced source inspected in Workbench by builder:17686tri within18khard cap (12ktarget missed), original visiblebody/lamps/seams/mirrors retained, four tyre profiles rebuilt around original axles. Single2048/32sample bake running8threads. No installation.

## Final state (2026-10-23)

- Task1 clock: approved and installed,3runtime hashes verified.
- Task2 street: candidate complete/reviewPASS,5parts68tri,2048atlas.
- Task3 facade: candidate complete/reviewPASS after source+rebake side correction,3parts1764tri,2048atlas.
- Task4 car: candidate complete/independentreviewPASS,5parts17686tri,2048atlas; actualbounds4.259023x2.116730x1.485697m. Minor faceting/fine seam aliasing recorded. Three static images cannot establish temporal zfight absence; no blocking surface/culling defect observed.
- Task5 rider: candidate complete/reviewPASS including actualEngine images,2exclusive26706tri poses,2048atlas,361mm crown drop, verified contacts/clearance.Total resident triangles for both poses is53412.
- Task6 token: candidate complete/reviewPASS,868tri,512atlas,centerpivot. Parent wrote missing BRIEF/REPORT from retained source and fresh artifact evidence after builder thread ended. Fullscene rendered49instances/21meshes/9textures; parent inspected pickup-distance silhouette and complete assembly.

Fresh root verification: all5actual-export verifiers exit0; photo-tool unit suite14/14; solution clean rebuild succeeds with exactly the known CS0649 unused _texture warning; art-scene tool build succeeds0warnings0errors. No new course-engine/gameplay changes.

Car bake-status wording corrected: PowerShell log wraps Material.use_nodes deprecation warning as NativeCommandError, later prints successful exports and Blender quit. Native exit code was not captured, so do not claim native Blender exit1 or that such exits are normal. Delivered artifacts independently validate and render successfully. No redundant bake performed just to recapture a return code.

Final independent whole-batch review: docs/art/2026-10-23-essential-final-review.md, PASS for candidate presentation with documentation closeout (addressed here and car REPORT). User's latest "okay" acknowledged status; no explicit new-batch installation approval inferred. New candidates remain in Art/out; proposed runtime file list/hashes in essential-install-plan.json. No commits.


Approved and installed2026-10-23: user said "it looks good for now lets move on" after seeing the desktop preview. All28runtimefiles match the approved SHA256 delivery list. Gameplay integration remains pending.
