Hannover public realm v2

Build: python RunnerGame/Art/assets/hannover_public_realm/build.py
Verify: python RunnerGame/Art/assets/hannover_public_realm/verify.py
Entry point: out/map.json (same cityManifest/groundManifest/route/groundY/clock contract; optional sceneProps).

Scope: wide station forecourt, both upper sides of Bahnhofstrasse, Kroepcke, full Georgstrasse and Steintor plaza, not a lane buffer. Manual facade-edge interpretation from licensed official aerial. Separate continuous gray context covers city extent under buildings and prevents floating buildings. Six original texture zones share an atlas, tiled with UV-safe per-cell triangulation; zone polygons are disjoint at Y=-1. Openings cut through ALL upper ground, with lower floors at Y=-4 and supported rails. These depths are assumptions.

Route: recomputed against full public polygon, source building footprints and revised opening. Full 1.5m lane spacing retained (1.8m swept half-width). 0.5m grid A* explores both available upper corridors; southeast corridor fits. Buffered-obstacle visibility is simplified, and a Kr?pcke control is moved 4m farther into the plaza for broad corners. Complete runtime 20% quadratic curves are checked for supported ground, >=0.3m building margin, >=0.5m opening margin and >=4m corner radius. The old 714.276m curve correctly fails the revised-opening fixture. Independent verify.py reconstructs exported controls with denser samples and analytic quadratic curvature. Trees are re-filtered against the final tube. Some paired avenue placements remain rejected where historic footprints and clearance prevent placement.

Known realism limits: city objects remain grey generalized LoD2; no new facade realism claimed. Aerial 2025 vs footprint base 2010 has conflicts. Procedural patterns represent material zones rather than exact stone catalogues. Flat ground datum is not surveyed terrain. No Google geometry or pixels used; user marked images determined scope only. Official reference crops are review-only and never referenced by runtime manifests. Source city raw is ../hannover_route/out/HannoverRoute.obj; normalized copied derivative is out/HannoverRoute.obj, with source and normalization provenance JSON copied here.

License: see SOURCE_CREDITS.txt and aerial-reference-provenance.json.


Paired avenue update: run python RunnerGame/Art/assets/hannover_public_realm/pair_avenue.py after a full ground rebuild to apply the inferred representative paired rows. 16 paired stations (32 avenue trees) use 10m row spacing and authored9.75m mature height. These are aerial-fit positions with +/-3m uncertainty, not an exact tree inventory. Full scaled crown projections clear source and hero facades; height-clipped actual lower mesh projections clear the player tube. See paired-avenue-placements.json and paired-avenue-report.json.

Georg material update: original gray rectangular pavers and2m terracotta running-bond strips under each inferred tree row, informed by licensed historical photo01 (2019). Source/photo pixels are never used. Run rebuild_ground_only.py to regenerate ground while preserving ALL map/route/city metadata and props. See paving-material-report.json for attribution, zone checks and protected file hashes.
