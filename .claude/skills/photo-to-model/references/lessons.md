# Lessons: mistakes that cost extra rounds

Each row is a general rule; "Seen in" names the model where it happened (details in `history.md`). Read before step 2, and again when a
loop stalls.

Contents: planning · measuring · building and tests · comparing · colour and material

## Planning
| Rule | Why | Seen in |
|---|---|---|
| Check the licence of a downloaded model on its source page before working on it; no verifiable CC0/CC-BY = do not use | Downloaded bike files were rough and had no redistribution licence, so the work was redone from photos | Bike |
| Budget animated characters as triangles per pose x poses | 73.7k x 40 poses is ~2.9M resident triangles | Officer v2 |
| Agree the detail class and budget at Gate A | The first model was rejected as "not detailed enough" after a full build | Rathaus |
| Choose `camera_z_range` from the shooting position at Gate A | A camera fit placed the camera 25 m underground | Rathaus |
| A true side/front view is a Gate A criterion | Without one, depth and proportions are guesses | Scooter |
| Photos from close and below hide set-back upper parts and cut off the ground; heights of such parts come from a more distant photo, ground heights from a photo that shows the ground, scaled by a part both photos see | The ball/finial came out too low, the base far too short | Kröpcke |

## Measuring
| Rule | Why | Seen in |
|---|---|---|
| Record profiles (width at 4-6 heights) and give features their own widths | One number per part makes builders guess pyramids, box steps, a full-width pediment | Rathaus |
| Measure each section on its own 1:1 grid and read the labels | A band was misread as an eave on a medium-zoom grid | Rathaus |
| Zoom 1:1 (crop x2) before counting repeated parts or judging height | Coarse grids gave 8 legs instead of 4 and a tall dome instead of a low one | Kröpcke |
| Decide slope vs. top surface only when two views agree (same height in both = real slope) | A sloped band was read once as a flat top, once as a slope | Kröpcke |
| Perspective inflates near-face widths read from a side photo; correct after the first compare | Near faces looked wider than they are | Scooter |

## Building and tests
| Rule | Why | Seen in |
|---|---|---|
| Prove each new test can fail with `mutation_check.py`: mutate the BUILD code, never spec.json | A build-equals-spec test follows the spec and stays green when the spec is wrong | Rathaus, Kröpcke |
| After a mutation, check the geometry fingerprint changed (the script does) | A mutation placed after the value was read changed nothing, so GREEN meant nothing | Kröpcke |
| Test surfaces, not vertices: `geom_probe.slice_points / width_at / ray_hit` or a relative test (build twice with a changed value) | Vertex tests were blind three times: a closed gap between feet, frame steps, long rails (vertices only at their ends) | Kröpcke |
| Test openings and gaps with a ray cast | A gap has no vertices inside it | Kröpcke |
| Tests read counts, positions and budgets from the spec (`inset`, `legs`, `tri_budget`), never hard-coded numbers | A changed leg inset made a hard-coded test fail | Kröpcke |
| Give the builder the shape vocabulary and the part crops, not the whole photo set | Builders turn profiled parts into boxes and pyramids when given only numbers | Rathaus |

## Comparing
| Rule | Why | Seen in |
|---|---|---|
| Done = no double image in the blend, not a good RMS | The outline looked perfect while gables, towers, windows were wrong | Rathaus |
| Loop on BOTH key photos | Looping on the front photo hid a dome, the legs and the base | Kröpcke |
| A fit that always goes far telephoto = inconsistent landmarks; re-read them on a zoom, then try `lens_shift` + level | A 30 px misread corner cost 15 px RMS | Kröpcke |
| When the engine view contradicts the blend, suspect the tool first | A viewer far plane hid the dome | Scooter |
| Never extrapolate a cut-off ground | The extrapolated ground made the base far too short | Kröpcke |

## Colour and material
| Rule | Why | Seen in |
|---|---|---|
| Sample colours on flat shaded areas, then check in the engine sheet | Sunlit samples came out too light | Scooter |
| Glass: sample plain reflection areas in >= 2 photos; fake the reflection in the bake (vertical gradient + diagonal streaks + recessed pane), never photo pixels | Sampling where exhibits showed through gave brown; a flat pane looked dead | Kröpcke |
| Count symmetric features on the photo, then build what the photo shows (one sideways ring, not two crossed) | The builder assumed the symmetric default | Kröpcke |
