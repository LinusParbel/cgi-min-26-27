# Hannover route blockout handoff

User approved a real-location pedestrian opening and requested professor-facing source/licence/method documentation. The candidate is built and independently reviewed; it remains an Art-side preview, not an installed replacement of the original street mode.

## Show the work

- Self-contained printable source note: `docs/art/HANNOVER_MAP_SOURCES_AND_METHOD.html`.
- Editable source note: same name with `.md`.
- Actual engine captures: `docs/art/previews/hannover-route-overview.bmp` and `hannover-route-start.bmp`.
- Candidate launch from repository root: `RunnerGame/bin/Debug/net10.0/RunnerGame.exe --map RunnerGame/Art/assets/hannover_pedestrian_blockout/out --overview`.

Enter starts riding in chase view. Tab switches overview/chase and pauses an active run. Enter resumes. A/D change provisional steering position, Space jumps, S ducks, Esc pauses, R restarts. Preview ends at Steintor. Three positions at1.5mspacing are temporary; no road lane markings are present. The proposed offence/introduction sequence is still future story work; current first-hit/second-hit pursuit mechanics remain.

## Sources and changes

Official Hannover LoD2 city geometry and official2025 aerial reference, both CC BY4.0 with archived primary-source evidence. No Google or OSM geometry/image pixels incorporated. Aerial pixels are reference-only, not runtime textures. Imported buildings are explicitly credited as third-party geometry. Original procedural ground and game integration are AI-assisted project work.

Raw conversion:504buildings,54274triangles. Candidate flat copy uses per-building GroundSurface normalization; footprint and relative height retained, absolute elevation not preserved. Original conversion untouched; shifts and source/derivative hashes recorded. Upper floor H54 and lower depth3m are blockout assumptions. Authoritative survey dates are distinguished from publication dates in the source note. Model detail remains grey massing; station/frontage detailing needs a separate reference pass.

Final route714.27637m,52points. Minimum sampled radius4.57566m, zero outer-lane reversals. Entire3.6m player corridor clears buildings by1.038m and interpreted openings by1.074m; ground supports it completely. Authored ground/detail5052triangles. Original NW proposal failed; SE upper corridor selected without shrinking footprints/openings. Old audit remains as historical negative evidence; `REPORT.json` and `verification.json` describe current output.

## Verification

- Production solution build:0warnings/0errors.
- Gameplay24checks; input8; manifest7; route geometry/JSON/actual-map tests pass.
- Raw city actual-export validation passes; final blockout rebuild and actual OBJ/support/negative-fixture checks pass.
- Nine candidate delivery file hashes match; source credit accompanies map and central credits copy to game output.
- Actual GPU loads17meshes/11textures, representative35draws; overview and starting chase view captured successfully. Counts are workload evidence, not a sustained FPS benchmark.
- Independent review has no outstanding must-fix: `docs/art/2026-10-23-hannover-map-review.md`.

No engine/shared-art edits or commits. The existing plain street remains available by launching without `--map`. Live human playtesting and the user's control preference are still to be evaluated.
