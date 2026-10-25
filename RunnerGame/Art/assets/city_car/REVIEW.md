# Independent city car review

Verdict: **PASS as an exported review candidate**, not runtime installation or user approval. Reviewed Task 4 and global constraints in `docs/superpowers/plans/2026-10-22-essential-assets.md`, candidates, spec, provenance, build/normalization code and REPORT. No production files changed.

## Evidence

- Independently parsed all five actual OBJ files, without invoking Blender or trusting pre-bake counts: **17,686 triangles** (body 14,344; wheels 836/835/836/835). Valid indexed triangles, nonzero areas, finite coordinates/UVs/normals, unit normals and UVs within [0,1]. The approved hard 18,000 limit passes; 12,000 remains a missed target, reasonably disclosed rather than a blocker.
- Independently assembled manifest pivots using OBJ axis conversion. Actual bounds: X [-1.058365, 1.058365], Y [0, 1.485697], Z [-2.118680, 2.140343] metres. Mirror-inclusive width 2.116730 m leaves 0.191635 m on each side of a centred 2.5 m lane. Length is 4.259023 m. Actual dimensions are distinguished from source authored dimensions in REPORT.
- Four separate wheels have meaningful local axle centres: Blender X +/-0.775, front Y 1.2321, rear Y -1.3505, height 0.31205 m. All four actual assembled tyre minima are exactly ground Y=0 in OBJ/engine coordinates. Wheel local fore/aft bounds centre on their axle. Rotation axis is X. Deterministic export normalization fixes the inherited wheel node offset without changing UVs.
- Source negative-X hood/headlamps mapped to Blender +Y; OBJ front is -Z. Body has ground-centred common origin. Front/rear images agree with the documented orientation.
- Atlas independently opened as **2048 x 2048 RGB**, necessarily opaque. Opaque glazing hides the removed interior; no visible cabin detail is claimed.
- Independently recomputed SHA256 of the source GLB, stored publisher page and publisher preview; all match provenance.json. Stored primary publisher page identifies an original Innerscene unbranded model released CC0 and links CC0 1.0. GLB hash: `107410e01453abbce452fabbe6d51436fb98a0920672643a893263a8861873d7`. Publisher attribution/source URLs and changes are recorded. This does not independently establish the publisher authoring process.

## Visual review

Inspected three engine views: `previews/engine_0.png`, `engine_180.png`, and `engine_90.png`. These show the actual exported exterior; the subsequent wheel-only 2.858 mm grounding correction does not alter body geometry/materials. Compact five-door hatchback silhouette, mirrors, door handles/seams, bumpers, front/rear lamps, wipers and wheel wells read clearly. Side view shows both axles at appropriate arches and tyre contact at a common ground line. No broad missing body faces, reversed exterior panels, obvious culling holes, logo or identifying plate text is visible. Blank plate panels are acceptable.

Must fix: **none found** within this candidate review.

Could improve: glazing and some body transitions visibly facet; thin hood/roof/door outlines break into small dashed pixels at this preview scale. Their narrow, feature-following pattern is consistent with reduced thin geometry and raster aliasing, rather than demonstrated broad coplanar face overlap. Static screenshots cannot prove absence of local intersection or temporal z-fighting; no flicker claim is made. This is a minor finish limitation, not a justified request for another bake or silhouette-damaging reduction. Preserve the current rounded exterior rather than force 12k solely for the target.

Limit: no animated steering/wheel-spin or live camera sweep was reviewed. The default close game-camera crop is documented in REPORT; this verdict concerns the export and three exterior views, not gameplay integration.
