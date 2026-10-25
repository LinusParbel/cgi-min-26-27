# Hannover pedestrian route blockout

User approved a geographically grounded Hauptbahnhof → Kröpcke → Steintor opening and explicitly requested sources/licensing documentation suitable for a professor. Three invisible steering positions are provisional, not a final design commitment.

## Deliverables and boundaries

- [x] Official city model acquired with primary publisher/licence evidence, selected tile CRC/SHA verification and preserved source IDs. No Google or OSM data incorporated.
- [x] Official aerial reference acquired with georeferencing and attribution; no aerial pixels in runtime textures.
- [x] Reproducible LoD2 conversion, raw source-coordinate derivative retained separately, actual GroundSurface footprints exported.
- [x] Route and ground authored from reference; rejected north-west path retained as negative evidence; south-east upper corridor chosen without shrinking footprints/openings.
- [x] Three positions at ±1.5/0 m, full player corridor 3.6 m. Smooth route sampling and turn tests; finite route ends at Steintor.
- [x] Candidate map renderer, overview toggle, road traffic replaced by pedestrian props; original straight-street mode retained.
- [x] Flat copy normalises building ground minima to H54, preserving footprints and relative heights. Explicit non-survey lower depth3m and guardrail assumptions. Original conversion untouched.
- [x] Professor-facing source/method note, printable self-contained HTML and attribution accompanying derivative map; central CREDITS copied to game output.
- [x] Independent review and bounded corrections: facade/terrain claims, licence wording, path clearance and tighter-turn smoothing.
- [x] Final current-output verification and actual GPU captures. Live window opened for user review; candidate remains under Art until promotion is requested.

Work stays in the established workspace because the required approved art is untracked. No engine/shared-art changes, no commits or runtime installation of the candidate map. New map is loaded explicitly from its Art output folder; first visual review precedes promotion.

Key files: `docs/art/HANNOVER_MAP_SOURCES_AND_METHOD.md`, `Art/assets/hannover_route/`, `Art/assets/hannover_route_reference/`, `Art/assets/hannover_pedestrian_blockout/`, `Gameplay/RoutePath.cs`, `Rendering/PedestrianMapRenderer.cs`, `RunnerGame.RouteTests/`.
