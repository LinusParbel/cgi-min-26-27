# Independent Hannover map review — 23 October 2026

Scope: candidate `hannover_pedestrian_blockout`, runtime map renderer, route helper, pedestrian simulation profile, and professor-facing source explanation. Read-only review except this report; no source modifications or commits. Unrelated asset changes were excluded.

## Verdict

The geographically grounded grey blockout is suitable as a reviewable candidate. It must be presented as imported official building massing with authored flat pedestrian surfaces and provisional gameplay, rather than a finished street reconstruction. No runtime correctness blocker was identified by this review. The two documentary must-fixes below were resolved and checked during bounded closeout; no outstanding must-fix remains within this review scope.

## Documentary findings — resolved

1. Initial method omitted the candidate's per-building normalization. Resolved: the method now distinguishes raw conversion from `Y_game = source height − building_ground_min − 1`, describes the separate playable copy, and records normalization in attribution. Horizontal coordinates and relative building heights remain source-derived; absolute vertical placement is deliberately changed.
2. Initial central credits lacked city/aerial entries. Resolved: `RunnerGame/CREDITS.md` now includes material names, provider, source and licence links, and modifications including normalization, with candidate/reference-only status. Candidate `out/SOURCE_CREDITS.md` carries the same attribution section. The source 20 cm GSD versus derived 50 cm pixel resolution is explicitly distinguished.

Correction to the initial review message: the proposal reference `../hannover_route_reference/waypoint-proposal.json` does resolve from the candidate directory to the archived asset-side reference. The builder reads that same copy. The earlier claim of a broken path was an unchecked reviewer inference and is withdrawn; no path fix is required.

## Verified findings

- Re-ran `dotnet run --project RunnerGame.RouteTests --no-restore -- RunnerGame/Art/assets/hannover_pedestrian_blockout/out/route.json 714.2760882703527`: PASS. Actual C# route: 52 nodes, 714.27637 m, minimum sampled radius 4.57566 m at 243.125 m, zero reverse steps at either ±1.5 m lane offset. This supersedes the retained tight-bend checkpoint. The radius is a sampled result, not a mathematical global bound.
- Runtime forward/right basis is internally consistent: initial negative-Z direction has positive-X right; model yaw maps negative-Z authoring forward onto the route tangent. Rider, scooter, objects, pursuer and chase camera all sample travelled route distance. The camera samples 6 m behind and 12 m ahead. Endpoint tangent extrapolation supports that framing.
- `Program` selects the geographic candidate only through `--map`; default street scene remains separately selectable. Ordinary play pauses two metres before route end with a Steintor completion message, and restart resets completion. Candidate status is visible in the map title.
- Pedestrian profile uses 1.5 m steering spacing and replaces spawned cars/vans with planters. Renderer does not load those vehicles. Collision remains the runner's distance/lane abstraction, appropriate to document as provisional gameplay.
- Meshes/textures are cached per resolved file and disposed once; scene disposal runs during shutdown and constructor failures dispose resources already registered. No new resource-lifecycle blocker was found.
- Current generated report records player tube halfwidth 1.8 m, building clearance 1.038 m, opening clearance 1.074 m and clock clearance 5.598 m. Independent geometry verifier output records complete tube support and no upper-floor overlap with openings. I inspected these outputs and verifier code; I did not rerun `verify.py`, because it rebuilds and rewrites candidate assets.
- The original NW route failure remains archived. Current SE corridor changes route placement rather than source footprints/opening polygons; measured Hausdorff deviation from proposal is 22.867 m within the declared 40 m allowance. Lower level depth and flat H54 floor are explicit assumptions.

## Source and licence evidence

Archived city publisher and licence pages, extracted-tile CRCs/hashes and retrieval records support the claimed official LoD2 source. The archived page identifies the 2010 base survey, 2024-12-05 metadata modification and 2026-01-20 publication; these dates must not be collapsed into a 2026 survey claim. Source city geometry has 504 selected building objects and 54,274 triangles.

The archived DOP page and extraction metadata support flight date 2025-03-06, publication 2026-01-20, EPSG:25832 and original 20 cm GSD. The assembled reference crop is resampled to 0.5 m pixels; distinguish this from original source resolution. World files and the crop pixel transform are retained. Orthophoto pixels are reference-only, absent from runtime texture generation.

Publisher links point to the German-language deed of CC BY 4.0 International. The proposed attribution appropriately identifies provider, materials, licence/source URLs and modifications, retains source evidence and avoids implying endorsement. This is an evidence/implementation review, not a claim of legal clearance. No Google or OSM geometry is incorporated in the reviewed pipeline.

## Could fix / limitations

- Resolved during closeout: `PedestrianMapRenderer` now describes the authored flat blockout datum rather than “surveyed height”.
- The route helper tests prevent offset folds but do not enforce the chosen usability goal of radius ≥4 m. A future route could regress below 4 m while still passing. Consider a configurable minimum-radius acceptance check when route geometry changes.
- Source triangulation includes extremely thin valid triangles. Reported minimum area/angle is not evidence of a rendering failure; keep an eye on these during later facade work.
- No additional GPU run was needed for this scope. Parent-provided actual-engine captures are useful presentation evidence, but this review does not claim a full interactive traversal, camera occlusion audit or final visual acceptance.

Bounded final closeout re-read the corrected method, central/candidate credits and renderer ground comment. All documentary must-fixes in this report are resolved. This closeout did not expand the scope into a full interactive traversal or new broad runtime testing.
