# Essential models ready for review

The clock and all five essential asset groups are approved and installed. All28new runtime files match the approved source SHA256 delivery list. Gameplay integration is pending; the combined scene is an art-review tool. No commits made.

![Essential batch in the course-engine art scene](previews/essential-batch-engine.png)

| Group | Triangles | Texture | Source and outputs |
|---|---:|---|---|
| 20m street, pavements, curbs |68 across5parts|2048|RunnerGame/Art/assets/street_kit|
| Shop floor + sandstone/brick upper floors |1764 across3modules|2048|RunnerGame/Art/assets/shopfront_kit|
| Civilian rider, ride + duck |26706 perpose;53412 both resident|2048 shared|RunnerGame/Art/assets/scooter_rider|
| Generic compact car |17686 acrossbody+4wheels|2048|RunnerGame/Art/assets/city_car|
| Original double-sided H token |868|512|RunnerGame/Art/assets/city_token|

Each folder contains reproducible build inputs, editable Blender source, actual OBJ/PNG/manifest exports, verification and review notes. Do not load both rider poses simultaneously; use its mutually-exclusive pose descriptor. Street parts share a common module origin; facade modules each start at ground and must be stacked externally. Car wheels use axle pivots. Token origin is at its centre and its spin axis is engineY.

The `out/` folders contain verification/presentation scratch files as well as delivery files. `essential-install-plan.json` enumerates only the proposed runtime files with SHA256 and target directories. Its status now records completed approved installation; all listed files are present in runtime.

Reproduce the full engine image:

```powershell
dotnet run --project tools/essential-scene -- docs/art/essential-scene.json docs/art/previews/essential-batch-engine.png
```

This is a static model review, not a playable runner. Code in RunnerGame/Program.cs still needs model placement, pose switching, movement, collision and pickups.

Verification: all five actual-export verifiers passed;14photo-tool unit tests passed; solution rebuild succeeded with one pre-existing CS0649 warning; review-scene tool built without warnings. Final independent review:2026-10-23-essential-final-review.md. Known limits: straight street only, opaque windows, shallow facades, two fixed rider poses, modest car faceting/fine seam aliasing and unspecified car native bake-process exit (PowerShell warning/error handling ambiguity; outputs independently validated).

Next content after this batch: pothole, bench, planter, street lamp, tree and delivery van. Extra zones, tram and goose remain later work.


Approved and installed2026-10-23: user said "it looks good for now lets move on" after seeing the desktop preview. All28runtimefiles match the approved SHA256 delivery list. Gameplay integration remains pending.
