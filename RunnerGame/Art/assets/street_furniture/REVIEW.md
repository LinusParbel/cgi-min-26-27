# Independent furniture review — 2026-10-23

PASS for candidate presentation; no installation authorized by this review.

Reviewed final `bench_35.png`, `planter_35.png` and `lamp_complete.png`, source construction/cleanup, bake-offset and part manifests, geometry checks and actual OBJ/PNG bytes. A separate read-only parser confirmed triangulation, valid vertex/UV/normal indices, nonzero triangle area, UV range, unit normals, ground bounds and opaque 1024×1024 shared atlas.

| Prop | Final triangles | Width × depth × height (m) |
| --- | ---: | --- |
| Bench | 2128 | 1.800 × 0.628 × 0.862 |
| Planter including shrub | 1836 | 0.925 × 0.925 × 1.279 |
| Lamp | 1764 | 0.360 × 1.500 × 6.001 |

Total 5728 triangles is below 10000. Evaluated source geometry is 5856; the reproducible exporter removes 128 bench bevel triangles collapsed by six-decimal serialization. This cleanup is integrated into the build path. All actual exports have minimum engine Y=0 and support-centred local origins; published pivots are zero. The asymmetric lamp arm intentionally extends from its mast origin. Bake separation was 0/12/24 metres before normalization, preventing cross-prop occlusion from coincident local origins.

Bench: five distinct seat slats, four back slats, rail support beneath the 0.45m seat, grounded feet and connected arm/back supports read clearly. Endpoint/radius inspection corroborates the engine image; no floating seat or arm blocker.

Planter: cavity, inner wall, soil and opaque foliage are visible. Review found a 12.5mm coplanar overlap at four rim corners. Final end bars are trimmed to 0.725m in source and UV-preserving exports; the interval assertion rejects overlap. The final image has narrow plausible corner joint shading rather than the original broad top-face stripe. Existing atlas retained by explicit parent authorization: tiny residual corner AO is acceptable at candidate/game scale, and is the only noted could-fix if a future rebake is otherwise needed.

Lamp: full-height view shows a slender tapered mast, sturdy ground base, continuous curved arm and attached head/lens. Source endpoints overlap at base/collar/mast/arm connections; there is no disconnected segment or emitted-light claim.

Validation now measures seat/rail contact and ground contact for bench feet, planter bottom and lamp baseplate, checks soil height and rim overlap, and rejects five missing-component fixtures (seat, rail, soil, rim, curved arm) plus a raised-foot fixture. These are meaningful component-presence/contact checks, not a complete structural solver; independent source endpoint inspection and actual-export ground checks cover the remaining review questions. No further must-fix item found.
