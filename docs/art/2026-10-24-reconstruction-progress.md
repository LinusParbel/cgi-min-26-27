# Public-realm reconstruction after user visual rejection

The user rejected the23October grey/narrow-strip interpretation and provided two annotated aerial screenshots. The red outlines specify the full Bahnhofstraße and Georgstraße/Steintor areas, not a single centreline. Screenshots are inspected for scope only and not redistributed or traced into shipped geometry. Official open aerial data supplies measurements; Commons photographs supply architectural references with per-photo licensing.

## Completed correction pass

- New isolated source/candidate folder `Art/assets/hannover_public_realm/`; v1 preserved.
- Full public surface and continuous supporting context; revised main opening from official reference, inward-facing retaining walls, upward lower floors and front-face ray regression checks.
- Route replanned rather than forcing it through the corrected opening. Approximately718.405m,8controls, three provisional1.5mpositions, swept route supported, broad turns.
- Two source-aligned Kröpcke facade interpretations in `Art/assets/kroepcke_facade_details/`: horizontal ribbons/rounded Magis corner and six-storey limestone-bay Center.10,616triangles, original opaque atlas; explicit historic/hidden-side/envelope limitations.
- Official CityGML source age conflicts with rebuilt Center documented; facade envelope is revised from photo and project-source evidence rather than deleting a visible window row to fit outdated walls.
- Optional static props and extra manifests, map-position inspection, right-drag orbit and wheel zoom.
- Map-only daylight depth shadows,2048PCF. Actual same-camera A/B identified ground bands as shadow acne; receiver-plane correction removed them without blurring paving or inflating contact bias. Actual shader/FBO rendering verified.
- Independent actual facade/whole-canopy projection checks and regression evidence. Source and reference credits merged; professor note updated for v2 and unfinished status.

## Visual checkpoint and remaining work

The ground width, promenade and first Kröpcke architecture can now be inspected together. The rest of the city's grey massing is still not a realistic reconstruction. Priority next work is station frontage and forecourt, street-by-street frontages/shop glazing along Bahnhofstraße, complete Georgstraße frontage, lower-level stairs/shopfronts, landmark positions and finer materials. Exact current signage, hidden facade returns and a stone-by-stone paving survey are not claimed.

The initial sparse tree placement did not show the paired Georgstraße avenue clearly. A bounded placement revision is being checked using official aerial references plus the licensed street-level photograph; inferred row spacing is labelled rather than presented as a current tree inventory. Overhead canopy can overhang the path when its underside clears the rider; trunk/structure and facade clearance remain physical checks.

Final placement pass:32 avenue trees form16 paired stations at9.75m authored height, plus9 plaza trees. Source placement uncertainty±3m is retained. Minimum scaled lower-geometry route margin.233m; whole canopy/source-and-hero margin.266m. Source photo01 also guided gray central pavers and two2m red/terracotta brick strips. Geometry is disjoint, route and hero meshes unchanged. Actual GPU avenue capture inspected: both rows visible, no shadow banding, patterned foliage shadows and material strips visible. Remaining walls are explicitly unfinished gray massing.

Do not equate geometry PASS with aesthetic approval. Human visual review of the corrected extent and first detailed slice is the next gate before repeating facade treatment along the remaining street.

Final handoff evidence: complete production rebuild0warnings/0errors; gameplay/input/manifest/route/scene-metadata/light-matrix checks pass. Actual route C# length718.40491m, minimum sampled radius11.3205m. Actual facade geometry, front-face floor/wall rays and independent scaled canopy/hero integration checker pass. Final runtime captures cover overview, Kröpcke and Georgstraße; current workload19meshes/13textures with77draws in overview and49draws in inspection. These counts are not a sustained performance benchmark. A development launch during output copying failed; after waiting and a clean rebuild, all captures succeeded. No unresolved build/runtime error remains.

Map-side source and reference attribution accompany the candidate. Central credits and the printable professor note are updated. V1 remains intact; v2 is not installed/promoted before the human visual checkpoint. Open the live candidate near Kröpcke with `RunnerGame.exe --map RunnerGame/Art/assets/hannover_public_realm/out --inspect 245`.
