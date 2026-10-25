# Independent street props final review — 2026-10-23

PASS for presentation of the completed candidate batch. No must-fix findings remain. This is a visual/export review, not runtime installation or gameplay approval.

Read the implementation plan, execution ledger, individual furniture/pothole reviews, tree source/spec/provenance and final scene configuration. Inspected exactly two final images: `RunnerGame/Art/assets/street_tree/previews/engine.png` and `docs/art/previews/street-props-engine.png`. Ran a separate read-only parser against all five actual OBJ files and all three PNG atlases; no production files, shared helpers or installed models were changed by this review.

| Candidate | Actual triangles | Opaque atlas | Budget |
| --- | ---: | --- | ---: |
| Bench | 2,128 | Shared 1024×1024 | Furniture total below 10,000 |
| Planter | 1,836 | Shared 1024×1024 | Furniture total below 10,000 |
| Lamp | 1,764 | Shared 1024×1024 | Furniture total below 10,000 |
| Pothole patch | 528 | 512×512 | 1,500 |
| Tree | 11,516 | 1024×1024 | 12,000 |

Furniture totals 5,728 triangles; the complete new batch totals 17,772. Actual exports pass triangulation, finite geometry, positive valid vertex/UV/normal indices, UV bounds, unit normals and nonzero triangle area. Furniture bases are at engine Y=0 with independent zero manifest pivots. Pothole geometry lies 2.502–14.320mm above its ground pivot. Tree measures 3.5×6.5×3.5m with a centred ground ring and zero pivot. All atlases are fully opaque. Earlier furniture review covers isolated atlas baking, structural contacts and the corrected planter rim; earlier pothole review covers its actual-road appearance and rejection fixtures.

The tree's final actual export contains 4,000 opposite-winding triangle pairs with distinct vertex IDs and opposed normals, confirming both sides of 2,000 leaves survived UV conversion. The initial 7,516-triangle export is superseded. Final OBJ SHA256 is `ad07bddedd7eff415b048c017d2b4a7572bf6487c63b3a200d52431291873bed`. Fixed local random seed and documented matching geometry hashes across two fresh final geometry builds support reproducibility; this review did not repeat a bake or verify byte-identical baked images. Original scripted geometry/procedural colours require no external model licence; no real species replica is claimed.

The combined actual-engine image shows a grounded bench with readable slats and supports, planter with rim/soil/foliage, slender complete lamp, visible dark road-damage patch and a recognisable porous tree crown at street distance. The tree standalone view confirms branching, lower trunk clearance and many small opaque leaves. The existing low-poly appearance is consistent across the batch.

Actual street exports put asphalt between X=-3.75 and +3.75, curb tops at ±3.75–3.93, and pavement out to ±5.75 at Y=.15. Bench at (-4.8,.15,-7), planter at (4.7,.15,-11) and lamp base at (-4.2,.15,-13) are on pavement. Tree placement was corrected from X=4 to X=4.2 so its ground ring clears the curb; final Z=-27 separates its canopy from the last building bay. Crown and lamp-arm overhang occur overhead; no new furniture/trunk obstructs the road at ground level. Pothole at (-2.5,0,-4) is on asphalt in front of the existing barrier and visibly clear in the final image. Prior car/barrier placements remain part of the existing scene.

Limits: pothole is an opaque surface damage patch, not excavated road or collision/gameplay logic. Lamp geometry/lens does not emit actual scene illumination. These candidates are still in authoring output folders. Parent reports final EssentialScene render exit 0 with 54 instances, 26 meshes and 12 textures; build verification and desktop presentation remain parent responsibilities.

Must fix: none. Could fix only if a future bake is otherwise needed: the already documented tiny residual planter corner AO. It is not a blocker and no additional cosmetic work or bake is requested.
