# Asset backlog — audited 22 October 2026

This is a finite production backlog for the first Hannover Rush Hour street slice. Sizes and triangle budgets below are proposals for review in the course engine, not approved specifications. More objects alone will not establish a finished game: the current executable still draws a rotating cube.

## Evidence and technical contract

- `RunnerGame/Program.cs` creates `Primitives.CreateCube()` with `NormalColorMaterial`. No game models are loaded, and no runner gameplay systems are implemented here.
- `RunnerGame/RunnerGame.csproj` copies `Assets/**` into the build. This makes assets available; it does not place or animate them.
- The agreed design is `docs/superpowers/specs/2026-10-16-hannover-rush-hour-design.md`. The longer `RunnerGame/Hannover_Rush_Hour_Game_Design_and_3D_Asset_Plan.md` is an earlier planning draft.
- Production assets use triangulated **OBJ + opaque PNG**, with UVs and normals. The engine ignores MTL. One shared baked colour atlas per asset is the established route; separate parts can share that atlas. GLB, skeletal animation, transparency, and PBR material slots are not the runtime acceptance contract.
- Use metres, intentional pivots, consistent orientation and explicit coordinate conversion. Existing asset directions differ; record each asset's direction rather than assuming one convention.
- Test in the course-engine viewer. Blender appearance alone is insufficient. For animated characters, the current production approach exports pose OBJs plus an animation manifest; gameplay playback still needs implementation.

## Existing work: preserve and reuse

| Family | Audited state | Remaining work |
|---|---|---|
| Voi scooter | Installed: `Assets/Models/Fahrzeug/ScooterVoi/`; body, two wheels, PNG and parts manifest | Fit rider; implement placement/wheel motion |
| Commuter bicycle | Installed: `Assets/Models/Fahrzeug/BikeCommuter/`; three meshes, PNG and manifest | Optional second vehicle; placement/wheel motion |
| Officer v2 | Installed: `Assets/Models/Charakter/Ordnungsamt/`; 40 run poses, PNG and animation manifest | Implement pursuit and pose switching; avoid drawing all poses together |
| Neues Rathaus | Installed: `Assets/Models/Wahrzeichen/NeuesRathaus/` | Place as backdrop; check scale, orientation and visibility |
| Wheelie bins | Installed: four skins under `Assets/Models/Mull/Tonne/` | Choose gameplay collider independently of render mesh |
| Construction kit | Installed: barriers, guide bollards, cones, sign 123 and warning lamps under `Assets/Models/Baustelle/` | Assemble readable patterns; use mounts manifests for lamps |
| Kröpcke clock | Approved and installed in `Assets/Models/Wahrzeichen/KroepckeUhr/`: 23,410 triangles, 2048 atlas, 26/26 tests; source/runtime hashes match | Export refreshed and independently reviewed; user approved 2026-10-22; placement in gameplay remains |

The authoritative existing asset notes are `RunnerGame/Art/ASSETS.md` and `tools/asset-spike/README.md`. No installed family above is currently wired into runner gameplay.

## First batch: complete one street slice

The user approved this essential batch on 2026-10-22. Execution plan: docs/superpowers/plans/2026-10-22-essential-assets.md. Clock is approved and installed; the street kit is exported and independently reviewed, awaiting batch visual review. Other candidates are in production.

| Order | Deliverable | Proposed scope and budget | Acceptance focus |
|---|---|---|---|
| 1 | Finish Kröpcke clock | Reuse existing candidate; retain its approximately 25k-triangle / 2048-square target unless review finds a reason to change | Compare both key references and actual engine view; preserve recognisable silhouette; install only verified output |
| 2 | Scooter rider | One clearly licensed human base, riding and ducking poses; approximately 1.7–1.8 m standing scale, 15–35k triangles per pose, 2048-square shared atlas | Hands on grips, feet on deck, plausible elbows/knees; no clipping in neutral/duck; engine-readable silhouette |
| 3 | Road, curb and pavement kit | One snapping 20 m module; three 2.5 m lanes, proposed 2 m pavements, approximately 0.12–0.15 m curb; below 3k triangles per assembled module, 1024–2048-square atlas | No endpoint gaps or unintended steps; clean repeating UVs; gameplay clearance |
| 4 | Shop/facade kit | One shop ground floor and two upper-floor variants, approximately 5–8 m bays and 3–3.5 m storeys; 2–6k triangles per module, shared 2048-square atlas | Coherent proportions at game distance, finished visible sides, no transparent-glass dependency |
| 5 | Blocking vehicle | First one city car, then one delivery van if street slice performance allows; approximately 4.2 × 1.8 × 1.5 m car / 5.4 × 2.0 × 2.6 m van, 8–18k triangles each, 1024–2048-square atlas | Recognisable proportions from rear and oblique views; footprint fits chosen lane pattern; separate simple collision bounds |
| 6 | City token | One original readable token; proposed 0.25–0.35 m diameter, below 1k triangles, 512-square atlas | Visible at game camera distance; sensible centre pivot for spinning; silhouette and baked face remain legible |

Finish the first batch with a review scene containing one road module, facade kit, rider/scooter, existing bin and barrier, car, tokens and Kröpcke backdrop. Review scale, camera distance, material consistency and measured performance together. Record each asset as source-ready, exported, engine-verified, installed and gameplay-integrated separately.

### Proposed initial 20 m street-kit brief

Produce independent road, left/right pavement and left/right curb meshes so the game can place or replace each part separately. The road spans x = −3.75 m to +3.75 m for three 2.5 m lanes; each pavement extends 2 m outward from its road edge. Proposed curb rise is 0.15 m. Keep the longitudinal endpoints flat and aligned on the same 20 m snapping grid, with no seams or elevation changes between repeated modules. Include no obstacles or decorative objects in these meshes. Use metres and record each part's origin, forward direction and shared atlas contract. The approved candidate is built under Art/assets/street_kit: 68 triangles, 2048 atlas, two lane dividers at x +/-1.25 m, geometry/export checks and independent review passed. It remains uninstalled pending the batch visual review.

## Next batch: fill the street without expanding zones

| Priority | Missing asset | Proposed scope |
|---|---|---|
| P1 | Pothole / damaged surface | One opaque road patch or shallow mesh, with independent hazard trigger; avoid assuming decal support |
| P1 | Bench | One reusable approximately 1.8 m street bench; below 4k triangles, 1024-square atlas |
| P1 | Planter | One large street planter with optional vegetation insert; below 4k triangles, 1024-square atlas |
| P1 | Street lamp / sign pole | One reusable lamp and compatible sign mounting; below 4k triangles, 1024-square atlas |
| P1 | Tree | One full-geometry opaque foliage solution compatible with current renderer; establish performance before variants |
| P2 | Bicycle rack | One rack sized around existing bicycle; below 3k triangles, shared street-prop atlas if practical |
| P2 | Café set | One table and chair set for pavement/background; below 6k triangles per set |
| P2 | Additional facade/road variants | Add only where the first slice visibly repeats; reuse atlas and snapping contract |

## Stretch: defer until first slice is playable

- Hannover Stadtbahn with advance warning and fair obstacle patterns.
- Marktkirche / Altstadt zone, then Maschsee or Herrenhausen scenes.
- Background pedestrians and goose animations, using licensed bases and the established character route.
- Shopping cart, car-door animation, cargo bike and additional vehicle skins.
- Helmet shield, battery, magnet, pretzel bonus and landmark collectibles.
- More distant landmark detail, LODs and decorative variants, justified by actual camera views and profiling.

## Completion evidence for every asset

Save reproducible source/build inputs and provenance; verify exported files, bounds, orientation, pivots, triangles, UVs and texture references. Inspect multiple engine angles and its intended game distance. Correct meaningful reference mismatches before adding unseen microdetail. Keep factual limitations in the asset notes. Installation and gameplay integration are separate milestones; neither is implied by an export or a viewer screenshot.


## First batch closeout (2026-10-23)

All five new essential groups are exported and independently reviewed: street68tri,facades1764tri,rider26706tri perpose,car17686tri,token868tri. The combined engine scene is docs/art/previews/essential-batch-engine.png. The clock is installed; new candidates await explicit visual approval before runtime copy. See2026-10-23-essential-handoff.md and essential-install-plan.json for the exact28deliveryfiles and remaining integration limits. Next batch remains pothole,bench,planter,lamp,tree and deliveryvan; no extra-zone work was started.


Installation closeout2026-10-23: user approved desktoppreview and nextwork; all28files of the five essential groups installed/hashed. Next streetprop batch underway per2026-10-23-street-props plan.


Nextpropsbatchcomplete2026-10-23: bench,planter,lamp,pothole,tree exported/reviewPASS;17772totaltri. Awaiting desktop visual approval before runtimeinstall. See2026-10-23-street-props-handoff.md. Deliveryvan remains the next missing vehicle; no extra zones started.


Deliveryvan candidate ready2026-10-23:15532triangles,2048opaqueatlas, fivegrounded axle-pivoted parts. IndependentreviewPASS; sourceactualmirrors narrowedto2.437moverall, bodyunscaled. Pendinglivevisualapproval, not runtimeinstalled. See2026-10-23-delivery-van-handoff.md.


Approved and installed 2026-10-23: user approved the live delivery van. All seven runtime files copied and SHA256 verified; gameplay integration remains pending.


Pavement finishing candidates 2026-10-23: bicycle stand, cafe table/chair and missing head-height duck barrier built, actual-export checked and independently reviewed. New unique geometry 2956 triangles. Pending live visual approval, not installed. These cover the current first-slice modelling gaps; additional variants require visible need. Gameplay integration remains separate.


Installation closeout 2026-10-23: user approved the live batch (good). All eight runtime files installed and SHA256 verified. Full runtime scene: docs/art/installed-street-scene.json. Gameplay integration remains pending.
