# Independent rider review — 2026-10-22

**PASS for presentation as an Art candidate.** No must-fix geometry/contact issue found. This is not runtime installation or user approval.

Read Task 5/global constraints, rider scout, provenance, REPORT, measured contact/clearance files and final preview implementation. Viewed only `previews/final_export_board.png` (one final image); obsolete `fit_board.png` was not inspected. The board imports actual exported OBJ files with their shared atlas and unchanged scooter manifests, renders ride/duck exclusively in separate panels, and includes actual-export hand/sole closeups. These are Blender Cycles previews, not an engine-renderer test.

## Independent export/source checks

A separate lightweight Python parser read both final OBJ files: each has 14,727 positions and 26,706 triangular faces, below 35,000 per pose. Both resident endpoints cost 53,412 triangles; display contract explicitly says mutually exclusive. Every face references valid positive position/UV/normal indices, and all parsed values are finite. Normal lengths range approximately 0.99992–1.00008. Exact UV arrays and every face's position/UV index sequence match across endpoints; position arrays differ. Normal indices need not match when exported normals differ by pose.

Atlas is a single RGB 2048×2048 PNG, inherently opaque. Both pose manifests use zero pivots and common scooter axle/ground origin. Descriptor records Blender +Y / engine -Z facing; assembled final views confirm rider and scooter face together, with both soles at engine Y=.184. Export bounds are ride X[-.316098,.316098], Y[.184,1.674661], Z[-.297237,.289765]; duck X[-.335005,.335005], Y[.184,1.316786], Z[-.297237,.505894]. The rearward duck extent agrees with the visible crouch.

All 35 provenance source hashes independently match local files. Copied primary MPFB LICENSE sections C/D explicitly cover base, textures, clothes, rigs and output assets as CC0; skin and casualsuit02 headers explicitly record September 2020 CC0 release. Exact body, skin, wardrobe, shoes, eyes, eyebrows, hair and rig sources are enumerated. No officer equipment/uniform markings are visible.

## Contact and plausibility

Final export closeup shows both palms over the cylindrical grips and curled fingers wrapping below them, with sensible wrists rather than mere wrist-bone placement. Both side panels retain contact. Supplementary evaluated-skin surface tests report 65/72 actual grip-cylinder samples within 8 mm on each side/pose, about .035 mm closest gap.

Both actual-export shoes visibly rest on the narrow deck in tandem with separated soles and plausible ankle/trouser joins. Measured low-sole support is 100%, bottom z=.184, with 8.65 mm fore/aft whole-shoe separation. Duck visibly bends knees/hips while preserving feet and grips, and keeps chest/head behind the display. Recorded body-crown drop is .361041 m. Dashboard tests report zero skin/clothing triangle intersections for either pose; sampled nearest dashboard-vertex surface distances are 4.65 mm ride and 60.67 mm duck. These are sampled distances, not a claimed global minimum-clearance proof; final visual evidence supports the contact result.

## Must/could fix

- **Must fix:** none for this candidate.
- **Could fix:** no extra cosmetic refinement requested. Transition interpolation is outside this two-endpoint deliverable, as REPORT states.

## Engine appearance follow-up — 2026-10-23

**PASS retained.** Independently viewed `docs/art/previews/rider-ride-engine.png` and `docs/art/previews/rider-duck-engine.png`, supplied as actual course Engine renders using unchanged GammaLit and separate rider/scooter textures. Total review images inspected: three, including the final export board. Both engine views show one endpoint exclusively, coherent skin/clothes/hair textures, opaque surfaces, plausible grip contact and supported feet. Duck remains visibly distinct with bent knees and hips behind the display; no obvious dashboard/body penetration, missing faces, UV failure or shading blocker is visible. This resolves the earlier engine-appearance observation caveat for these rendered endpoints; no additional fix is requested.

No heavy Blender process, bake, installation or runtime edit was performed by this reviewer. Only this review artifact was written.
