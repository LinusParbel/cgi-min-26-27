# Essential batch final independent review — 2026-10-23

**PASS for presenting the exported art candidates; documentation corrections remain before claiming the batch fully closed.** No blocking cross-asset geometry, placement, material or preview integration defect found. This is not runtime gameplay verification or approval to install the five new candidates.

## Evidence and integration

Read the implementation plan, execution ledger, four completed per-asset reviews, car report/verifier/manifest/bake log, rider pose descriptor, scene configuration, new EssentialScene implementation and the existing viewer pivot/material conventions. Independently inspected `previews/essential-batch-engine.png` (one image). It shows a coherent three-lane street, repeated storefronts, rider/scooter, lane-compatible car, three visible gold pickups and existing props. The pickup silhouettes read at this camera distance; the H is a close-range detail. The empty distance is a preview boundary, not a completed game environment.

Fresh lightweight read-only Python parsing independently confirmed every referenced scene OBJ/texture exists and all selected part names resolve: **49 instances / 21 unique meshes / 9 unique textures**. All five new exports contain finite coordinates/UVs/normals and valid triangulated face indices. Counts and opaque RGB atlas sizes are:

| Candidate | Actual triangles | Atlas |
|---|---:|---:|
| Street, five parts | 68 | 2048² |
| Facade, three independent modules | 1,764 | 2048² |
| Rider | 26,706 per pose; 53,412 for both resident | 2048² shared |
| Car, body plus four wheels | 17,686 | 2048² |
| Token | 868 | 512² |

The parent separately reports all five actual-export verifiers and 14 unit tests passing; those executions were not rerun here. Prior independent reviews cover detailed street joins, facade side overlap, rider contacts and token winding/UVs. Car-specific visual/seam review is being finalized separately; this review does not replace its findings.

EssentialScene resolves manifest assets relative to their manifests, direct assets relative to the scene, and caches meshes and texture/material pairs by normalized absolute path. Different rider/scooter textures cannot overwrite each other. Blender pivots map `(x,y,z)` to engine `(x,z,-y)`, matching the existing viewer. Local pivot translation precedes whole-instance scale/yaw/translation, retaining correct axle placement and reuse. Resource disposal is appropriate for this short-lived review tool. No issue requires changing the shared engine/viewer.

Street instances meet at engine Z=-10 with 20 m spacing. Facade storeys use independent zero origins and 3.2 m offsets above pavement Y=.15, with opposing ±90° orientations facing the street. Rider and car use engine -Z forward. Car wheel pivots are axle-centered and its 2.11673 m mirror envelope fits the 2.5 m lane. The scene uses only the ride manifest; the rider descriptor explicitly marks ride/duck mutually exclusive and records resident cost. Token center pivots are placed at Y=.9; vertical spin is engine Y. All five candidate scene paths point to Art outputs, not an implied runtime installation.

The approved clock's OBJ, PNG and manifest each independently match the installed `Assets/Models/Wahrzeichen/KroepckeUhr` file by SHA256.

## Required documentation closeout

1. `city_car/REPORT.md` currently says Blender exits with code 1 after clean quit. The saved `bake.log` records a `Material.use_nodes` deprecation warning wrapped as PowerShell `NativeCommandError`, then successful bake/export messages and `Blender quit`; it does **not** record the native process exit code. Correct the assertion to distinguish verified artifacts from an unrecorded native exit status, unless actual process-result evidence is available. No additional bake is justified by this ambiguity alone.
2. Append current car/token/full-scene and final validation status to the execution ledger: its final entries still describe the car bake running and omit token completion. Include the final independent car verdict when available. Keep new runtime installation pending explicit preview approval.

## Nonblocking limitations

- Car exceeds its 12k target but remains under the approved 18k hard limit; this is disclosed.
- Rider provides two tested endpoints, not verified transition animation. Shared ride-baked AO is intentional.
- EssentialScene silently ignores an unknown selected part name. Current configurations all validate; fail-fast selection checking could help future editing but is unnecessary for this batch.
- This scene is a static art preview: no collision, endless spawning, pickup logic, animation or functional game acceptance is implied.

Only this report was written. No production edits, Blender/bakes, runtime installation or commits were performed.
