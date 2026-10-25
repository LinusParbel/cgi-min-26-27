# Art asset register

Assets built with the photo-to-model workflow (`.claude/skills/photo-to-model/`). Runtime files live in
`RunnerGame/Assets/Models/<Category>/<Asset>/`; sources (photos, spec, build script) in `RunnerGame/Art/assets/<asset>/`.

| Asset | Runtime files | Triangles | Texture | Photo match | Approved |
|---|---|---|---|---|---|
| Kroepcke clock `kroepcke_uhr` | `Models/Wahrzeichen/KroepckeUhr/PRP_KroepckeUhr_body.obj`, `PRP_KroepckeUhr.png`, `PRP_KroepckeUhr_parts.json` | 23,410 | 2048 x 2048 shared | Reviewed game interpretation; key-photo RMS 0.97% / 2.14%; simplified ornaments; 26 geometry tests passed | 2026-10-22 (user: "clock is find") |
| Navy commuter bicycle `bike_commuter` | `Models/Fahrzeug/BikeCommuter/VEH_BikeCommuter_{body,wheel_front,wheel_rear}.obj`, `VEH_BikeCommuter.png`, `VEH_BikeCommuter_parts.json` | body 7,680, wheels 4,020 each; total 15,720 | 2048 x 2048 shared | Batavus-inspired photo interpretation; source shape and baked engine view approved; independent export review passed | 2026-10-20 |
| Voi e-scooter (2022 gen.) `scooter_voi` | `Models/Fahrzeug/ScooterVoi/VEH_ScooterVoi_{body,wheel_front,wheel_rear}.obj`, `VEH_ScooterVoi.png`, `VEH_ScooterVoi_parts.json` | body 2456, wheels 664 / 664 | 1024² shared | ref/17 side: landmark RMS 4.7 px (0.29 %), outline matched in 5 rounds; ref/15 rear 3/4: 26 px (2 %, scooter leans on kickstand) | 2026-10-18 |
| Neues Rathaus Hannover, Maschteich front `rathaus_hannover` | `Models/Wahrzeichen/NeuesRathaus/BLD_NeuesRathaus_body.obj`, `BLD_NeuesRathaus.png`, `BLD_NeuesRathaus_parts.json` | 24,540 | 2048² | ref/01 front: landmark RMS 3.2 px (0.20 %) over 28 points; 50/50 blend congruent at 1:1 for the central projection, dome group, pavilions, towers and window axes; north side simplified (out of scope) | 2026-10-18 (user: "make it perfect, don't ask again") |

| Fictional Ordnungsamt pursuer v2 `ordnungsamt_pursuer_v2` | `Models/Charakter/Ordnungsamt/CHR_Ordnungsamt_run_01.obj` through `_40.obj`, `CHR_Ordnungsamt.png`, `CHR_Ordnungsamt_animation.json` | 73,710 per pose | 2048 x 2048 shared | MakeHuman-based officer with dark external vest; corrected-hand run and baked engine view approved; v1 backed up | 2026-10-20 |

## Notes per asset

### Approved essential batch (2026-10-23)

These are exported, independently reviewed, approved by the user and installed on2026-10-23. Gameplay integration remains pending. Full engine composition and handoff: `docs/art/2026-10-23-essential-handoff.md`. Exact runtime delivery filenames/targets/hashes are prepared in `docs/art/essential-install-plan.json`; all28runtimefiles are installed and SHA256-verified.

| Asset | Source/export folder | Triangles | Atlas | Review |
|---|---|---|---|---|
| Street, pavements and curbs | `Art/assets/street_kit/` |68 across5parts|2048|PASS;20m snap ends, three lanes|
| Shop + sandstone/brick upper modules | `Art/assets/shopfront_kit/` |1764 across3modules|2048|PASS; side-face/AO correction completed|
| Civilian scooter rider | `Art/assets/scooter_rider/` |26706 perpose;53412 both resident|2048 shared|PASS; ride/duck exclusive, actual engine check|
| Generic compact hatchback | `Art/assets/city_car/` |17686 acrossbody+4wheels|2048|PASS; CC0 adopted base, axle pivots, minor faceting/seam aliasing|
| Original city H token | `Art/assets/city_token/` |868|512|PASS; double-sided, centre pivot|

### Approved street props (2026-10-23)

Approved and installed2026-10-23; all14runtimefiles hash-verified. Reproducible sources, full engine scene and reviews: `docs/art/2026-10-23-street-props-handoff.md`.

| Asset | Source | Triangles | Atlas | Review |
|---|---|---|---|---|
| Bench, planter and lamp | `Art/assets/street_furniture/` |5728 total|1024shared|PASS; independent ground origins|
| Visual pothole overlay | `Art/assets/pothole/` |528|512|PASS; visible above opaque road|
| Generic street tree | `Art/assets/street_tree/` |11516|1024|PASS; opaque two-sided leaves verified after export|


### Approved delivery van (2026-10-23)

`Art/assets/delivery_van/out/VEH_DeliveryVan_parts.json`:15532triangles acrossbody/four axle wheels,2048opaqueatlas,5.704837x2.437192x2.505583m. Independent reviewPASS; User approved live viewer; all seven runtime files installed and SHA256 verified in Assets/Models/Fahrzeug/DeliveryVan/. Generic CC0 adopted base; mirror projection adjusted, bodyunscaled. Details/primarylicence/exportchecks/liveviewercommand: `docs/art/2026-10-23-delivery-van-handoff.md`.

### Installed models

**bike_commuter** - Installed after source and engine-view approval. Three meshes share one opaque atlas. Wheels have axle-centered local origins; manifest pivots are Blender coordinates, converted to engine (x,z,-y). Front is Blender -Y / engine +Z. Centre stand is deployed. Wheelbase 1.08 m is an assumed reference ruler; this is a recognisable photo-based interpretation, not a measured factory replica. Source, packed Blender preview, validations and game/source ZIPs are in `RunnerGame/Art/assets/bike_commuter/`. No imported Bushido/PyBullet geometry is used. Fine wire spokes alias at small screen sizes. Wheel motion/gameplay placement is not implemented by the asset files.

**ordnungsamt_pursuer_v2** - Approved MakeHuman-based officer appearance and corrected-hand run, in `RunnerGame/Art/assets/ordnungsamt_pursuer_v2/`. Navy uniform with separate Dortmund-inspired protective carrier, Hannover sleeve shields, belt/radio, cargo pockets and duty boots. Export candidate: 40 matching OBJ poses, 20 ms each (800 ms loop), 73,710 triangles per pose, shared opaque 2048-square atlas, prefix `CHR_OrdnungsamtV2`. Packed neutral/animated Blender sources and game/source ZIPs are available. Actual OBJ data and engine viewer images checked; independent review found no blocking issues. Baked engine view approved and runtime installed on 2026-10-20, retaining the CHR_Ordnungsamt filename prefix. Previous v1 runtime backed up under checkpoints/runtime_v1_before_v2_install. See source README/provenance for licensing, presentation differences and playback limits.

**ordnungsamt_pursuer** - Historical v1, replaced in runtime by approved v2 on 2026-10-20; its source and verified runtime backup remain available. Eight static OBJ poses, 100 ms each (0.8 second loop), one shared texture. Character faces +Z in the engine (Blender -Y), metres, common world origin. Runtime files installed after engine-preview approval. The animation manifest describes the sequence; gameplay pose switching is not implemented. Do not draw all poses together. Source, editable Blender previews and export scripts: `RunnerGame/Art/assets/ordnungsamt_pursuer/`. Independent review verified matching topology/UVs, readable back lettering and smooth shading. Six poses touch the ground; poses 3 and 7 have 3.5 cm flight clearance.

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


### Approved pavement finishing props (2026-10-23)

Original generic bicycle stand (612 triangles), cafe table (596), chair (924), and high duck barrier (824). Shared 1024 pavement atlas and separate opaque 512 barrier atlas. Actual export checks and independent reviews PASS; candidate scene docs/art/pavement-props-scene.json loads 73 instances / 38 meshes / 16 textures. Sources Art/assets/pavement_props and Art/assets/duck_barrier. User approved the live view; all eight runtime files installed and SHA256 verified. Gameplay integration remains pending.


### Geographic pedestrian route candidate (2026-10-23)

Hauptbahnhof via Bahnhofstrasse/Kroepcke/Georgstrasse toward Steintor: approximately714.28m. Official CC BY4.0 LoD2 building geometry:504objects/54274triangles. Separate flat playable derivative normalises per-building ground elevations; original source conversion preserved. Authored ground/openings/rails5052triangles, procedural paving texture; aerial reference pixels are not shipped as textures. Three invisible provisional positions at1.5mspacing; pedestrian profile excludes cars/vans/asphalt damage. Grey blockout only, candidate Art output loaded with --map, not installed under Assets/Models. Source/licence/method note: docs/art/HANNOVER_MAP_SOURCES_AND_METHOD.md. Full source and transformations: Art/assets/hannover_route, hannover_route_reference and hannover_pedestrian_blockout.
