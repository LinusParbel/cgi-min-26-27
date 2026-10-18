# HANNOVER RUSH HOUR
## Game Design Document + Blender Asset Production Plan

**Version:** 0.1 — planning draft  
**Date:** 16 October 2026  
**Project type:** University 3D game / semi-realistic city runner  
**Status:** Concept approved in principle; engine, team size, schedule, and grading rubric TBD  
**Working language:** English (use German signage in-game)

> **One-line pitch:** Race through a semi-realistic, game-friendly version of Hannover on a customizable e-scooter or bike, dodge everyday urban chaos, collect rewards, and stay ahead of an increasingly ridiculous pursuit.

---

## 1. Vision and design pillars

**Working title:** *Hannover Rush Hour* (HRH).  
**Genre:** Third-person 3D arcade runner; initial implementation is a 3-lane endless runner, with optional authored levels or branching zones later.  
**Target:** Desktop first (keyboard/gamepad); mobile is out of initial scope.  
**Camera:** Third-person follow camera, behind and slightly above rider.  
**Tone:** Energetic, humorous, recognizable Hannover; no realistic injury or gore.  
**Visual direction:** **Semi-realistic stylization**: believable proportions, architecture, asphalt, vehicles and lighting, with simplified details, readable color accents, and slightly exaggerated gameplay silhouettes. Avoid toy-like low-poly city packs as the final look unless upgraded/reworked.

### Design pillars
1. **Recognizable Hannover:** Landmark silhouettes, street details, green Stadtbahn, signage and local humor.
2. **Immediate readability:** The player must identify whether to switch lanes, jump, or duck at speed.
3. **Accessible production:** Small, reusable modular scenes rather than a street-by-street digital twin.
4. **Replayable chaos:** Curated safe obstacle patterns, procedural sequence variation, score and pickups.
5. **Asset quality with provenance:** Custom hero assets plus selected external assets; licenses documented.

### Non-goals for the first version
- No full open-world Hannover or centimeter-accurate real-world city map.
- No realistic vehicle physics simulation, networking, NPC traffic AI, or photogrammetry of whole districts.
- No requirement to build 5 complete zones before gameplay is fun.
- No dependence on paid AI 3D generation to complete the MVP.

---

## 2. Core player fantasy and story

**Main concept — the city escape:** Player rides an e-scooter and accidentally enters an inconveniently restricted area during rush hour. A comically persistent **Ordnungsamt-inspired fictional officer** pursues them. We treat this as playful fiction: the streets can be rearranged, and the game does not encourage unsafe real-world riding.

**Alternative pursuers / events:**
- An oversized orange street-cleaning vehicle with spinning brushes.
- A territorial goose near Maschsee (special chase event).
- A funny “late for the delivery” timer (mission variant).

**Recommendation:** Make the pursuing figure a *visual pressure mechanic* rather than implementing full pathfinding. On one hit, the pursuer gets closer; on a second or third mistake, the run ends. A pursuing-character animation can follow later.

### Minute-to-minute loop
1. Start run on selected rider + scooter.
2. Move forward automatically; steer between three lanes.
3. Jump low obstacles and duck under high hazards (if appropriate for vehicle/animation).
4. Collect tokens and temporary power-ups.
5. Survive progressively faster street segments with rising density and variety.
6. Reach a landmark transition / personal-best milestone.
7. Crash or get caught → results → replay or unlock cosmetic variation.

### Controls (proposal)
| Action | Keyboard | MVP? |
|---|---|---|
| Move lane left / right | A/D or Left/Right | Yes |
| Jump | Space / Up | Yes |
| Slide/duck | S / Down | Optional |
| Pause | Esc | Yes |
| Use special ability | E | Later |

**Design safeguard:** Every generated obstacle pattern must leave at least one achievable escape route. Avoid unpredictable moving hazards without clear early visual/audio warnings.

---

## 3. World and landmark strategy

**Important:** Make a *fictionalized* sequence of recognizable Hannover scenes, not a geographic reconstruction. The game can transition between landmarks using curves, tunnels, fades, bridges or loading segments.

| Zone | Signature identity | Landmark(s) | Gameplay hazards | Delivery priority |
|---|---|---|---|---|
| 1. Kröpcke Chaos | Pedestrian retail center | Kröpcke clock, central shops | bins, benches, barriers, pedestrians in background | **MVP** |
| 2. Altstadt Dash | Historic, narrow streets | Marktkirche silhouette, timber-framed frontage | café furniture, cobblestones, turns | Next |
| 3. Rathaus Run | Broad formal civic space | Neues Rathaus dome and side towers | planters, temporary works, fountain edges | Next |
| 4. Maschsee Madness | Lakefront promenade | lake, paths, tree lines | puddles, food stalls, geese, picnic props | Stretch |
| 5. Herrenhausen Finale | Formal landscaped garden | hedges, alleys, fountains | hedge turns, garden obstacles | Stretch |

### Landmark modeling priorities
**Kröpcke clock — first hero asset**
- Build the distinctive vertical silhouette: base, metal body, clock housing, glass/ornament details.
- Model from multiple photographic references; prioritize recognizable proportions over microgeometry.
- Add PBR metal, glass and clock-face materials; bake small surface details if needed.
- Deliver an LOD0, simplified LOD1, collision proxy, and clean GLB.

**Marktkirche — second hero asset**
- Focus on brick façade, iconic tower, roofline and large architectural masses.
- Use modular brick materials and repeated windows; not individually modeled bricks.

**Neues Rathaus — third hero asset**
- Focus on central dome, towers and front silhouette.
- Repeat modular windows and ornament trim; reserve detailed sculpting for camera-visible elements.

**References (not a license grant to reuse photos):**
- Kröpcke clock: https://www.visit-hannover.com/Kultur-Sehensw%C3%BCrdigkeiten/Sehensw%C3%BCrdigkeiten/Auf-den-Spuren/Auf-vielf%C3%A4ltigen-Spuren/Kr%C3%B6pcke-Uhr
- Neues Rathaus: https://www.visit-hannover.com/Kultur-Sehensw%C3%BCrdigkeiten/Sehensw%C3%BCrdigkeiten/Neues-Rathaus/Neues-Rathaus
- Old town/Marktkirche: https://www.visit-hannover.com/Media/01-DATA-Neu/Galerie/Altstadt-Historische-Bauten
- More city images: https://www.visit-hannover.com/Media/01-DATA-Neu/Galerie/Hannovers-sch%C3%B6nste-Seiten

For each landmark collect **front, left/right, rear (where useful), three-quarter, and detail references**. Record photographer/URL and permission before including image files in a distributed repository.

---

## 4. Art direction — semi-realistic, not photorealistic

### Appearance
- **Geometry:** Realistic proportions, simplified roof details and street geometry, subtle bevels.
- **Materials:** PBR with restrained texture detail; asphalt, brick, painted steel, glass, concrete, plastic.
- **Lighting:** Daytime late-afternoon sun with moderate shadows, soft ambient sky and reflective highlights.
- **Palette:** Neutral city grays / sandstone / brick with selective green trams, orange construction, blue/yellow pickups.
- **Visual hierarchy:** Neutral world → bright and readable hazards → even clearer player and collectibles.
- **Atmosphere:** Light haze, occasional flags, trees, subtle decals, readable shadows; no constant heavy rain/fog in MVP.
- **Optimization:** Hero landmarks look good at a distance; incidental shops share modular assets and tileable materials.

### Style test before mass production
Create a **single 50–80 m street slice** containing:
- one block of buildings; roadway and pavement;
- one player scooter and rider proxy;
- one trash bin, one barrier and one car;
- one background landmark silhouette (Kröpcke clock);
- fixed camera and target game lighting.

Review in the **actual game engine**, not only Blender's render view. If external props look too cartoony, rework materials and proportions or replace them before producing 100 assets.

### Initial technical targets (starting assumptions, not hard requirements)
- Blender units: metric, 1 Blender unit = 1 meter.
- Straight track module: example **20 m length**, lanes ~**2.5 m** wide each (tune to camera and obstacles).
- Reusable generic street prop: usually aim for low thousands of triangles or less; hero landmark triangle count may be higher and should be tested in engine.
- Default texture sizes: 1K for small props, 2K for hero assets where justified; shared trim sheets/atlases strongly preferred.
- Export: `.glb` or `.gltf` depending on engine import pipeline; `.blend` is the editable source.
- Origins/pivots: bottom-center for props; consistent origin and forward direction for vehicles; apply transforms carefully.
- Collision: separate simplified collision objects or game-engine colliders rather than render mesh collision.
- Naming: `ENV_`, `PROP_`, `VEH_`, `LMK_`, `CHR_`, `FX_`, `COL_` prefixes.
- Define axis orientation and color space with the engine integrator once the engine is selected.

---

## 5. Gameplay building blocks

### Obstacles — implement in layers

| Asset / pattern | Behavior | Player response | First-pass method | Tier |
|---|---|---|---|---|
| Mülltonne (small wheelie bin) | stationary, low-medium | switch/jump | custom procedural Blender | MVP |
| Road barrier (Baustelle) | blocks lane | switch/jump depending height | procedural / existing | MVP |
| Traffic cones | lane cluster | weave | existing / procedural | MVP |
| Car / delivery van | blocks lane; later moves | switch | downloaded + material editing | MVP |
| Pothole | road hazard | jump | decal + collision trigger | MVP |
| Bench / planter | stationary | switch/jump | existing or simple custom | Phase 2 |
| Café table/chairs | clustered | weave | existing | Phase 2 |
| Parked bicycle | long low obstacle | switch | existing | Phase 2 |
| Tram | large moving threat; warning bell | change path | custom/available tram | Phase 2 |
| Car door | telegraphed dynamic hazard | switch | hinged animation | Stretch |
| Shopping cart | moving lateral hazard | timed dodge | existing | Stretch |
| Goose | short chase / lane disruption | timed reaction | character model+anim | Stretch |
| Rain puddle | brief handling change | avoid | material/decals | Stretch |

**Obstacle placement:** Spawn from prefabs in tested pattern templates, e.g. `[left: bin, center: clear, right: car]`. Record guaranteed clearance and jump timings. Add randomness to *pattern order*, not arbitrary full-lane blocking.

### Collectibles and power-ups
| Item | Effect | Asset complexity | Tier |
|---|---|---|---|
| City token | score / cosmetic currency | low | MVP |
| Helmet shield | absorb one collision | low | Phase 2 |
| Battery boost | brief speed + visual effect | low | Phase 2 |
| Magnet | pulls nearby collectibles | low | Phase 2 |
| Pretzel double-points | 2x score for short time | low | Phase 2 |
| Mini landmark collectible | secret unlock token | medium | Stretch |

### Vehicles
- **Primary:** Standing e-scooter, several recolorable variants; believable frame, two wheels, stem, handlebar, lights, deck.
- **Second:** City bicycle; different animation and cosmetic design, same basic runner controls.
- **Stretch:** Cargo bicycle or funny unlockable vehicle.

Keep underlying game collision/controller consistent across vehicle skins until gameplay is stable. Model rider poses and animations early enough to verify handlebar/reach proportions.

### Score and progression
- Distance + collected city tokens + optional stunt/near-miss bonuses.
- Rising difficulty by speed and obstacle-pattern complexity; cap difficulty to preserve fairness.
- End-of-run panel with distance, best distance, tokens and collisions.
- Cosmetics only for MVP progression; no economy complexity needed.

---

## 6. Complete asset inventory and sourcing decision

**Legend:** `CUSTOM` = should model as project work; `PROC` = Blender Python/MCP; `FIND` = download then adapt; `DECIDE` = scout first, custom if unsuitable.

| ID | Asset | Need | Method | Priority | Search keywords / notes |
|---|---|---:|---|---|---|
| LMK-001 | Kröpcke clock | 1 | CUSTOM | P0 | Hannover Kröpcke Uhr 3d model; photo reference |
| LMK-002 | Marktkirche simplified | 1 | CUSTOM | P1 | Marktkirche Hannover 3d Sketchfab |
| LMK-003 | Neues Rathaus simplified | 1 | CUSTOM | P1 | Neues Rathaus Hannover 3d model |
| ENV-001 | Road straight segment | 3–5 variants | PROC/FIND | P0 | modular asphalt road glTF |
| ENV-002 | Sidewalk / curb | 3–5 | PROC | P0 | german pavement modular |
| ENV-003 | Street junction / curve | 2–3 | PROC | P1 | road intersection modular |
| ENV-004 | Shop facade modules | 5–10 | FIND/PROC | P0 | european storefront 3d PBR |
| ENV-005 | Generic multi-story facades | 6–10 | FIND/PROC | P0 | German European city architecture PBR |
| ENV-006 | Trees and planters | 3–5 | FIND | P0 | game ready deciduous trees |
| ENV-007 | Street lamps/sign poles | 3–5 | FIND/PROC | P0 | German street lamp signpost |
| ENV-008 | Asphalt / paving / brick materials | 4–6 | FIND | P0 | tileable PBR CC0 |
| PROP-001 | Wheelie bins | 3–5 skins | PROC | P0 | 120l wheelie bin German |
| PROP-002 | Construction barrier | 2 | PROC | P0 | Absperrschranke Baustelle |
| PROP-003 | Traffic cone | 1 | PROC | P0 | pylone traffic cone |
| PROP-004 | Bench | 2 | FIND | P1 | city park bench PBR |
| PROP-005 | Café table and chairs | 2 sets | FIND | P1 | outdoor cafe furniture |
| PROP-006 | Bike rack / parked bikes | 2 | FIND | P1 | bicycle parking 3d |
| PROP-007 | Pothole and road decals | 3 | PROC/FIND | P0 | road crack pothole decal |
| PROP-008 | Shopping cart | 1 | FIND | P2 | trolley game ready |
| VEH-001 | Main e-scooter | 1 + skins | CUSTOM/DECIDE | P0 | electric standing scooter glb rigged |
| VEH-002 | City car | 2–3 | FIND | P0 | PBR hatchback game ready |
| VEH-003 | Delivery van | 1 | FIND | P1 | European delivery van |
| VEH-004 | Bicycle | 1 | DECIDE | P1 | city commuter bike 3d |
| VEH-005 | Hannover-like Stadtbahn | 1 | DECIDE/CUSTOM | P1 | Hannover Stadtbahn ÜSTRA 3d |
| CHR-001 | Rider character | 1 | FIND/DECIDE | P0 | rigged casual rider character |
| CHR-002 | Fictional pursuing officer | 1 | FIND/DECIDE | P1 | rigged cartoon semi-realistic officer |
| CHR-003 | Background pedestrians | 2–3 | FIND | P1 | low cost rigged pedestrians |
| CHR-004 | Goose | 1 | FIND | P2 | rigged goose walking animation |
| UI-001 | City token | 1 | PROC | P0 | custom Hannover coin |
| UI-002 | Shield / battery / magnet | 3 | PROC | P1 | simple game powerups |
| FX-001 | Dust / collision / pickup | 3 | ENGINE | P0 | use particles and shaders in engine |
| AUD-001 | Bells, traffic ambience, coin | 3–5 | FIND | P1 | verify audio licenses separately |

`P0 = MVP`, `P1 = polished demo`, `P2 = stretch`.

### Asset sourcing policy
1. First check repositories where licensing is uncomplicated; test one sample asset before batch downloading.
2. Inspect each model's **triangle count, file format, UVs, materials, textures, dimensions, rig/animation, editability and license**.
3. Favor *semi-realistic PBR* over aggressively low-poly/cartoon packs for the final look. Kenney can provide temporary prototypes even if final props are replaced.
4. For specific Hannover landmarks, search first, but expect to custom-model simplified silhouettes.
5. Record both the original model and every modification. Do not assume that online images or Google/Street View screenshots are free to redistribute.
6. Confirm whether university grading demands a minimum number of personally modeled original assets.

---

## 7. Places to look for existing assets

| Source | Website | Best use | Licensing reminder |
|---|---|---|---|
| Kenney City Kit Roads | https://kenney.nl/assets/city-kit-roads | modular roads, traffic signs, prototyping | CC0 per pack page |
| Kenney City Kit Commercial | https://kenney.nl/assets/city-kit-commercial | background city buildings | CC0 per pack page |
| Kenney City Kit Suburban | https://kenney.nl/assets/city-kit-suburban | generic buildings / layout | CC0 per pack page |
| Quaternius | https://quaternius.com/ | game-ready stylized vehicles, props, characters | inspect individual pack and license |
| Poly Haven | https://polyhaven.com/ | PBR materials, HDRIs, some models | check site's CC0 terms |
| Sketchfab | https://sketchfab.com/ | specific vehicles, recognizable architecture | **each model has its own license**; attribution often required |
| Poly Pizza | https://poly.pizza/ | quick low-poly drafts and placeholders | inspect each asset's license |
| BlenderKit | https://www.blenderkit.com/ | searchable Blender asset workflows | review asset access and license before redistribution |

**Search batches to run before creating each custom asset:**
- `"Kröpcke Uhr" 3D`, `"Neues Rathaus Hannover" 3d model`, `"Marktkirche Hannover" 3D`
- `German wheelie bin glb`, `construction barrier Germany 3d`, `electric scooter PBR FBX`
- `european shopfront modular PBR`, `German tram Stadtbahn 3d`, `city bicycle rigged gltf`

**Research outcome field:** `Not searched / No suitable model / Candidate found / Licensed / Imported / Adapted / Approved`. This document is a **sourcing plan**, not proof that those specific Hannover models are currently downloadable.

---

## 8. Blender + MCP workflow

### Proposed stack
- **Blender:** authoring, mesh editing, UV, PBR materials, source `.blend` files and export.
- **Blender MCP:** AI-driven Blender Python and scene inspection, not a substitute for visual checks.
- **Agent client:** Claude Code, Cursor, VS Code/Codex, or another MCP-capable client.
- **Game engine:** Unity, Godot or Unreal (TBD). Test glTF export with chosen engine immediately.
- **Version control:** Git for scripts/docs + Git LFS for binary assets and textures if using Git.

### Blender MCP installation reference (third-party community project)
Current project: https://github.com/ahujasid/mcp-for-blender  
The package is now called `mcp-for-blender` (formerly `blender-mcp`). If `uv` is installed:

```bash
uvx mcp-for-blender setup
```

Then restart the AI app, launch Blender, check the MCP add-on panel, and test with a simple mesh. Follow the repository's updated instructions for your platform. **Security:** MCP can execute arbitrary Blender Python; review scripts, use trusted repos, never expose its local control interface to untrusted networks, keep backups, and avoid destructive operations without approval.

### Repeatable per-asset process
1. **Brief:** purpose, target dimensions, materials, reference images, expected camera distance, max rough complexity.
2. **Search:** query asset libraries; log candidates, sources and licenses.
3. **Choose:** download and modify, build procedurally with MCP, or custom-model manually.
4. **Blockout:** correct dimensions, recognizable silhouette, consistent origin.
5. **Detail:** bevels, normals, UVs, optimized mesh, PBR textures/materials.
6. **Inspect:** front/side/top/three-quarter; look for floating pieces and shading errors.
7. **QA:** inspect transforms, manifold issues where relevant, triangulation, material slots, UVs, file paths.
8. **Export:** GLB; separately configure simplified collider/LODs if required.
9. **Import-test:** engine scale, normals, texture integrity, performance, and collision.
10. **Record:** status, artist, date, source/attribution, license, files and screenshots.

### Asset creation template prompt for the AI agent

```text
You are a Blender asset-production assistant for Hannover Rush Hour,
a third-person semi-realistic arcade runner set in Hannover.

Work on ONE reusable asset at a time. Before editing:
- Inspect the active scene and existing files.
- Do not delete or overwrite unrelated work.
- Check whether a suitable reusable model exists and report its source/license.
- If original modeling is needed, create game-ready geometry via Blender Python
  or focused mesh edits, not one uncontrolled whole-scene generation.

Style: believable real-world proportions, semi-realistic PBR materials,
simplified details, clean beveled edges, consistent late-afternoon lighting.

For the requested asset:
1. State assumptions (size, orientation, expected player distance).
2. Build a blockout and show multiple views.
3. Refine geometry and materials.
4. Validate dimension, triangle count, UVs, normals, naming and pivot.
5. Make a preview render and list issues you noticed.
6. Save source .blend, export .glb, and report the exact output paths.
7. Never claim an export succeeded without verifying the file exists.
```

### Starter prompt 1: first original model
```text
Create a semi-realistic 120-liter German wheelie bin (Mülltonne),
approximately 1 meter tall, with a hinged lid, two wheels, grips,
subtle plastic roughness, correctly scaled parts and clean bevels.
Make three material variants: anthracite, blue and brown.
Model for a game camera viewing it from 5–20 meters.
Save the .blend and export one GLB per variant after inspection.
```

### Starter prompt 2: landmark
```text
Help me build a semi-realistic game-ready approximation of the Kröpcke
clock in Hannover. Start with a reference checklist and simple silhouette
blockout. Do not invent intricate architectural detail unseen in refs.
Separate base, body, face and ornament materials. Put it at real-world
plausible scale and optimize for a third-person runner camera.
First produce a preview for approval before high-detail work.
```

### Starter prompt 3: modular street
```text
Create a reusable straight 20-meter Hannover-inspired street segment,
three gameplay lanes, sidewalks, curbs and repeated building-front anchor
points. Build in meters with snapping-friendly endpoints and editable
materials. Do not place unavoidable obstacle geometry on the road.
Add optional separate lamps, benches and sign placements.
Export the module and make a demo scene with three connected segments.
```

---

## 9. Suggested repository and Blender folder structure

```text
hannover-rush-hour/
├── README.md
├── docs/
│   ├── game-design.md             # This document
│   ├── asset-register.csv
│   ├── licensing.md
│   ├── art-style-guide.md
│   └── decisions.md
├── references/
│   ├── kroepcke/
│   ├── marktkirche/
│   ├── rathaus/
│   └── material-board/
├── assets/
│   ├── source-blend/
│   │   ├── landmarks/
│   │   ├── vehicles/
│   │   ├── props/
│   │   └── environment/
│   ├── incoming-third-party/
│   ├── textures/
│   ├── exports-glb/
│   └── previews/
├── blender-scripts/
│   ├── generators/
│   └── export/
├── game/
└── project-management/
    └── milestones.md
```

### Asset naming examples
- `PROP_TrashBin_120L_Blue_v01.blend`
- `LMK_KroepckeClock_Blockout_v01.blend`
- `VEH_EScooter_Main_v02.blend`
- `ENV_Road_Straight20m_v01.glb`

### Asset register fields
`ID, Asset, Zone, Priority, Owner, Method, Source URL, License, Attribution, Status, .blend path, .glb path, Dimensions, Triangles, Texture budget, QA notes`

---

## 10. Road generation and scene assembly design

**Recommendation:** build a modular lane-runner world with **track chunks** instead of a giant static mesh. Each chunk can consist of a straight/curved road mesh, decoration anchors, a landmark reference, and a list of safe obstacle configurations.

### Example track chunks
- `Road_Straight20m` — generic unobstructed section.
- `Road_BinZigzag20m` — bins create alternating safe lanes.
- `Road_Baustelle20m` — barriers with visible open bypass.
- `Road_CarParked20m` — one lane occupied by a car.
- `Road_LandmarkTransition40m` — scripted reveal of Kröpcke clock.

**First-person? No:** Third-person keeps the scooter/rider visible, shows more scenery and helps players see obstacles ahead.

**World scrolling vs moving player:** both are possible. Prototype simple forward player movement first; for endless running use chunk spawning/despawning or pooling. Coordinate with engine team before committing to a specific technical solution.

### Fairness requirements
- At least one reachable route through every obstacle pattern.
- Jumpable obstacles have consistent height and clear silhouettes.
- Dangers are visible at least a reaction window ahead, scaled to speed.
- Use signs/sounds before sudden tram movement or road closures.
- Street clutter should not disguise collider shapes.

---

## 11. Game systems and technical tasks

| System | Minimum implementation | Later extension |
|---|---|---|
| Runner controller | auto-forward, lanes, jump | smooth lean animation, trick moves |
| Camera | follow, smoothing, FOV tuning | dynamic camera during boost |
| Track manager | small set of repeating chunks | weighted zone transitions |
| Obstacle spawner | curated patterns | difficulty weights + moving hazards |
| Collision | fail and restart | stumble/pursuer distance/shields |
| Pickups | tokens and score | magnet, battery boost, rare landmarks |
| UI | start, pause, score, result | unlock garage, statistics |
| Audio | pickup, collision, ambient traffic | zone music, tram bell, goose chase |
| Save | local best score | cosmetics and progress |
| Performance | profile first playable zone | LODs, pooling, occlusion |

---

## 12. Production milestones

### Milestone 0 — Scope / setup (first working session)
- [ ] Confirm game engine, target hardware and course rubric.
- [ ] Confirm expected percentage of original modeling vs downloaded assets.
- [ ] Agree on art style with 6–10 references.
- [ ] Create repo and asset register.
- [ ] Set up Blender, MCP and a test export/import.

**Definition of done:** one Blender cube can be modified by the agent and imported into the engine with correct dimensions.

### Milestone 1 — Vertical slice (first playable demo)
- [ ] Make scooter blockout and rider placeholder.
- [ ] Build reusable road + curb + basic facades.
- [ ] Create 3 core hazards: wheelie bin, barrier, car.
- [ ] Implement lanes, jump, scoring, restart.
- [ ] Model rough Kröpcke clock and place it in background.
- [ ] Demonstrate 60–90 seconds of functional play.

**Definition of done:** coherent semi-realistic street, player control, fair obstacles, end-of-run loop.

### Milestone 2 — Visual polish
- [ ] Refine scooter and rider placement.
- [ ] Refine Kröpcke clock with photographed references.
- [ ] Use consistent PBR materials and color palette.
- [ ] Add environmental props, lighting, ambient sound.
- [ ] Improve collision cues and game readability.

**Definition of done:** game looks visually coherent in the engine, not only in Blender.

### Milestone 3 — Extra content (if time)
- [ ] Add Altstadt or Rathaus zone.
- [ ] Add bike option with a shared controller.
- [ ] Add one pursuer animation or goose chase event.
- [ ] Add one or two power-ups and basic cosmetics.
- [ ] Profile performance and fix obvious bottlenecks.

### Milestone 4 — Course submission
- [ ] Produce a build and short gameplay capture.
- [ ] Document contributions and which models were original.
- [ ] Produce labeled turnaround renders and topology/UV images for key original assets.
- [ ] Audit sources, licenses, credits and redistribution permissions.
- [ ] Save reproducible `.blend` sources and export files.

---

## 13. Suggested team allocation

Adjust depending on group size:

| Workstream | Responsibilities | Main output |
|---|---|---|
| Art direction / landmarks | references, style guide, landmark models | Kröpcke and Rathaus/Marktkirche |
| Vehicles / characters | scooter, bike, character pose/rig | player visuals |
| Modular environment | roads, props, facades, material consistency | track kit |
| Gameplay programming | controller, camera, track, pickups | playable build |
| Integration / QA | imports, collisions, license register, builds | stable playable demo |

If you have only 2–3 people, merge workstreams and protect the MVP. Each custom Blender model should have one owner and one reviewer.

---

## 14. Quality acceptance checklist (apply to every P0 model)

- [ ] Silhouette visually matches brief at actual game camera distance.
- [ ] Plausible scale and consistent metric units.
- [ ] Correct orientation, origin, applied/intentional transforms.
- [ ] UVs and materials import without missing textures.
- [ ] No visible broken normals, floating geometry or severe shading errors.
- [ ] Triangle count and material slots recorded.
- [ ] Appropriate separate collider defined.
- [ ] PBR roughness / metallic values appropriate for material.
- [ ] `.blend` and `.glb` paths verified.
- [ ] Three preview views captured.
- [ ] Source URL, license and attribution recorded if external.
- [ ] Tested in game engine with final gameplay camera.

---

## 15. Risk register

| Risk | Impact | Mitigation |
|---|---|---|
| Hannover reconstruction too ambitious | high | stylized landmark corridor, one zone first |
| Third-party models don't match semi-realistic style | medium-high | early reference scene and asset approval gate |
| Blender MCP produces messy geometry | medium | inspect generated Python, staged approvals, per-asset QA |
| Assets have unclear licensing | high | licensing register, avoid incompatible models |
| Too much art before gameplay | high | first playable vertical slice milestone |
| Imported models too heavy | medium | test performance in engine, optimize, reduce materials |
| Rider looks wrong on scooter | medium | prototype body/vehicle together in week one |
| University demands original modeling | high | confirm rubric; custom hero assets and document process |
| Procedural obstacle patterns become impossible | high | handcrafted pattern templates and validation |

---

## 16. Immediate next 10 actions

1. Choose engine and MCP AI client.
2. Create repo with this document as `docs/game-design.md`.
3. Download **Kenney City Kit Roads** as layout reference or placeholder.
4. Search Sketchfab for scooter, Stadtbahn and **Kröpcke Uhr**, documenting results only if the asset is actually downloadable and licensed.
5. Gather 6–10 Kröpcke photos from distinct viewing angles; keep usage rights in mind.
6. Make a 3D style test with road, sidewalk, facades, scooter and a bin.
7. Model **Mülltonne v01** with Blender MCP, inspect and export.
8. Make first **scooter blockout** and correct rider/handlebar dimensions.
9. Make **Kröpcke clock blockout** for silhouette recognition.
10. Import assets into game engine and test 60 seconds of runner gameplay.

### Decisions still open
- **Game engine:** Unity / Godot / Unreal?
- **MCP client:** Claude Code / Cursor / Codex / VS Code?
- **Project team:** members and modeling responsibilities?
- **Course duration and deadline:** how many weeks remain?
- **Assessment:** is original geometry required and are external models allowed?
- **Target platform:** desktop only or mobile?

---

## 17. Source links and notes

- Community Blender MCP: https://github.com/ahujasid/mcp-for-blender — current setup, Python interaction and supported clients (checked Oct 2026).
- Kenney Roads: https://kenney.nl/assets/city-kit-roads — current listing shows 90 files and CC0.
- Kenney Commercial: https://kenney.nl/assets/city-kit-commercial — current listing shows CC0.
- Kenney Suburban: https://kenney.nl/assets/city-kit-suburban — current listing shows CC0.
- Sketchfab model licensing guidance: https://sketchfab.com/developers/download-api/guidelines — attribution and license obligations; check the exact asset.
- Hannover official visitor references: links in Section 3.

**Notice:** Any architectural photo, real brand logo or model is subject to its own usage rights. Treat all model-finding entries as research suggestions until you confirm a specific asset is available, compatible and licensed. Technical geometry targets are estimates that must be validated against the chosen engine and target hardware.
