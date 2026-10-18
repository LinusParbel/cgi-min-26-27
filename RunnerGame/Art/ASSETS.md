# Art asset register

Assets built with the photo-to-model workflow (`.claude/skills/photo-to-model/`). Runtime files live in
`RunnerGame/Assets/Models/<Category>/<Asset>/`; sources (photos, spec, build script) in `RunnerGame/Art/assets/<asset>/`.

| Asset | Runtime files | Triangles | Texture | Photo match | Approved |
|---|---|---|---|---|---|
| Voi e-scooter (2022 gen.) `scooter_voi` | `Models/Fahrzeug/ScooterVoi/VEH_ScooterVoi_{body,wheel_front,wheel_rear}.obj`, `VEH_ScooterVoi.png`, `VEH_ScooterVoi_parts.json` | body 2456, wheels 664 / 664 | 1024² shared | ref/17 side: landmark RMS 4.7 px (0.29 %), outline matched in 5 rounds; ref/15 rear 3/4: 26 px (2 %, scooter leans on kickstand) | 2026-10-18 |
| Neues Rathaus Hannover, Maschteich front `rathaus_hannover` | `Models/Wahrzeichen/NeuesRathaus/BLD_NeuesRathaus_body.obj`, `BLD_NeuesRathaus.png`, `BLD_NeuesRathaus_parts.json` | 24,540 | 2048² | ref/01 front: landmark RMS 3.2 px (0.20 %) over 28 points; 50/50 blend congruent at 1:1 for the central projection, dome group, pavilions, towers and window axes; north side simplified (out of scope) | 2026-10-18 (user: "make it perfect, don't ask again") |

## Notes per asset

**scooter_voi** — Wheels are separate OBJs with their origin on the axle; `parts.json` gives each part's pivot in
Blender coordinates (engine translation = (x, z, -y)). The scooter faces -Z in the engine (+Y in Blender).
Lessons: read grid labels, not display positions; side-photo readings of wide parts are near-face (perspective);
the landmark RMS is partly circular, the outline overlay is the real check; colour samples from sunlit highlights
come out too light (fenders); handlebar width could not be fixed from a leaning scooter (kept 0.60 m).

**rathaus_hannover** — Static backdrop landmark, the Maschteich front faces -Y in Blender (+Z towards the camera at yaw 0).
Measured with a 129 m facade ruler (hannover.de) and the 97.73 m dome tip; the south front came out 127.2 m. Lessons:
fit the camera with a plausible height range (it went 25 m underground without one); the outline check misses
everything inside the silhouette — the 50/50 photo/model blend at full resolution (`compare.py --zoom`) finds
windows, gables and pinnacles; build tapering gables from trapezoids, not stacked boxes; a 200 m viewer far plane hid
the dome; bands inside a gable can be misread as an eave — confirm on the 1:1 blend.
