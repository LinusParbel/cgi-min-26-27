# Art asset register

Assets built with the photo-to-model workflow (`.claude/skills/photo-to-model/`). Runtime files live in
`RunnerGame/Assets/Models/<Category>/<Asset>/`; sources (photos, spec, build script) in `RunnerGame/Art/assets/<asset>/`.

| Asset | Runtime files | Triangles | Texture | Photo match | Approved |
|---|---|---|---|---|---|
| Voi e-scooter (2022 gen.) `scooter_voi` | `Models/Fahrzeug/ScooterVoi/VEH_ScooterVoi_{body,wheel_front,wheel_rear}.obj`, `VEH_ScooterVoi.png`, `VEH_ScooterVoi_parts.json` | body 2456, wheels 664 / 664 | 1024² shared | ref/17 side: landmark RMS 4.7 px (0.29 %), outline matched in 5 rounds; ref/15 rear 3/4: 26 px (2 %, scooter leans on kickstand) | 2026-10-18 |

## Notes per asset

**scooter_voi** — Wheels are separate OBJs with their origin on the axle; `parts.json` gives each part's pivot in
Blender coordinates (engine translation = (x, z, -y)). The scooter faces -Z in the engine (+Y in Blender).
Lessons: read grid labels, not display positions; side-photo readings of wide parts are near-face (perspective);
the landmark RMS is partly circular, the outline overlay is the real check; colour samples from sunlit highlights
come out too light (fenders); handlebar width could not be fixed from a leaning scooter (kept 0.60 m).
