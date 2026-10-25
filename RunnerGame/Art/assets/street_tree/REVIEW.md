# Independent street tree review — 2026-10-23

PASS for candidate presentation. No runtime installation or gameplay approval implied.

Reviewed the corrected actual OBJ/PNG, final standalone engine image, source/spec, manifest, provenance, pre-bake checks and build report. The obsolete 7,516-triangle export is not the reviewed candidate. Final OBJ SHA256: `ad07bddedd7eff415b048c017d2b4a7572bf6487c63b3a200d52431291873bed`.

A fresh independent read-only parser passed all 11,516 triangles: finite coordinates, positive valid position/UV/normal indices, UVs within atlas bounds, unit normals and nonzero triangle areas. It found exactly 4,000 coincident opposite-winding triangle pairs, each with disjoint vertex IDs and opposed normals. This confirms both sides of all 2,000 diamond leaves survived actual export, fixing the initial UV-conversion loss. The remaining 3,516 triangles form the wood. Total is below the 12,000 budget. Texture is opaque 1024×1024.

Actual engine bounds are (-1.764350, 0, -1.759605) to (1.735650, 6.5, 1.740395): 3.5×6.5×3.5m. The manifest pivot is zero and the trunk ground ring is centred there; the crown's small asymmetric offset is intentional. Source leaf underside is 2.568m. Fixed seed 230326 and local RNG govern geometry; builder records matching geometry hashes from separate final no-bake and correction-bake runs (`bc1beba17f490089973bc5b3c2df870c203e398f8f6dd0761b094a4bc6d8f0ef`). This review did not rerun Blender or claim byte-identical baked images.

The final engine view shows a coherent porous green crown, many small opaque leaf polygons, visible connected branching and a grounded tapering trunk with clear space below the crown. Flat leaves and angular bark remain visible at close range and are consistent with this low-poly candidate. No silhouette, culling or support blocker found. Source is original scripted geometry and procedural colours; provenance lists no external assets, licensed model dependencies or species-replica claim.

Must fix: none for this candidate. No additional cosmetic correction or bake requested. Combined pavement placement is covered by the batch review.
