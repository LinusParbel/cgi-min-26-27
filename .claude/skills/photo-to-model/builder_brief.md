# Builder brief (fill in, send to the sonnet builder)

Repo root: <path>. Do not commit. Never edit tools/*, RunnerGame/Art/lib/*. Never use mcp__blender__* tools.
Asset: `RunnerGame/Art/assets/<asset>/` — <what it is>; <facing: vehicles +Y, props −Y>; class <backdrop|medium|replica|custom>,
≤ <tri_budget> triangles, <tex_res>² texture (both are in spec.json; read them from there, do not hard-code). Read `spec.json` fully (every dim has a source) and `scooter_voi/build.py` as pattern.

## Parts to build (one line per section, all numbers via spec.d())
- <section>: <spec key of its profile/feature list> → <shape from the vocabulary below>

## Shape vocabulary — use these, never a single box/pyramid for a profiled part
| Spec gives | Build |
|---|---|
| profile `[[z, width], ...]` of a flat part (gable, pediment, stepped wall) | one trapezoid prism per segment on the face plane (width a at z0 → width b at z1) |
| profile of a round part (dome, cap, spire, bulb, wheel hub) | lathe through the profile points, 8–24 sides |
| profile of a square roof (flaring, bell, pyramid) | stacked square frustums per segment; concave if the widths shrink fastest at the top |
| feature with its own width on a face (frontispiece, pediment over it, clock, plate) | its own prism with THAT width — never stretched to the face width |
| windows / arches / gallery / dials | recessed: dark inset ≈ 10 % of the opening width + frame ≈ 5 % of it (a 3 m building window → 0.3 m / 0.15 m; a 0.6 m clock dial → 6 cm / 3 cm); arch head ≥ 8 segments |
| pinnacles, finials, obelisks | slim frustum + small cap, width from spec, inset from spec |
| repeated features (window axes, dormers) | positions from the spec list (left half), mirrored; never re-spaced evenly |
| curved or organic body (bin, tram, mudguard, handlebar) | lathe or loft through the measured profile rings; tubes along a path (`pl.tube`, `pl.arc_shell`); rounded corners with a bevel, not a box |
| moving parts (wheels, lids, doors) | own object per part, origin on its axis/hinge; pivot goes to `<PREFIX>_parts.json` |
Reliefs on side faces stay ≤ ~3 % of that face's width proud (deeper ones show beside the outline in the front view).

## Landmarks
Create `pl.landmark(name, loc)` for EVERY name in refs.json → photos[<key photo>].landmarks, at the matching 3D point.

## Tests (blender_test_<asset>.py), written first, run with the BL command
- budget (tris ≤ spec tri_budget), ground at z 0, facing, every refs landmark exists
- one test per profiled part that measures the BUILT surface (e.g. width at two heights), not the spec value; use
  `RunnerGame/Art/lib/geom_probe.py` (`width_at`, `slice_points`, `ray_hit`, `tri_count`) instead of looking at vertices
- counts and positions come from the spec (e.g. `spec.d("pedestal")["legs"]`), never hard-coded
Report: test result line, triangle count, which spec entries you could not build. The main session proves each new
test can fail with `python RunnerGame/Art/lib/mutation_check.py A/build.py <test.py> <test_name> --old ... --new ...`
(mutates BUILD code, checks the geometry changed, expects RED, restores) before trusting it. Test openings with
`geom_probe.ray_hit`, never by looking for vertices in the gap.

## Image budget
The part's reference crops `A/previews/crops/crop_<part>_<NN>.png` (≤ 2) + at most 1 own preview
(Workbench, size 512). Do not open comparison images.
