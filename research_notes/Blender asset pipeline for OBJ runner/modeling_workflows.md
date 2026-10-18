# Beginner-friendly, time-efficient Blender modeling workflows for game-ready low/mid-poly assets (Hannover Rush Hour, OBJ + PNG engine)

Scope note: research done 2026-10-16. The current Blender manual is "Blender 5.2 LTS" ([Blender manual](https://docs.blender.org/manual/en/latest/files/import_export/obj.html)). Several tutorial sources found are Blender 4.0 to 4.5; the core modeling UI has been stable across 4.2 to 5.x, but version differences (auto smooth, extensions) are flagged below. Web search yielded mostly listings and secondary write-ups for tutorial content; where only an aggregator (Class Central, BlenderNation) was found, that is said explicitly. **Time estimates in this document are NOT from sources** (none of the sources gave beginner time figures); they are the researcher's own inferences and are labelled as such.

Engine facts checked directly in this repo (primary source, `Engine/Geometry/Loaders/ObjLoader.cs`): the loader supports `v`, `vt`, `vn`, `f` in all four index forms, triangulates polygons with more than three corners **as a fan**, supports negative indices, and **ignores** `mtllib`/`usemtl`, `o`/`g` groups and `s` smoothing groups; "All objects of a file end up in one common mesh." Vertices are deduplicated by the (position, UV, normal) triple, so hard edges exported as split normals survive.

## 1. Fastest learning path for absolute beginners (~1 week) and best current resources

### Takeaway
Do not do the full 4.5-hour Blender Guru donut; instead do one short "interface + first low-poly model" course (Polygon Runway's free Blender 4 beginners course or Grant Abbitt's Blender 4.2 low-poly well series), then go straight to small game props with Grant Abbitt / Imphenzia videos, modeling the actual project props as practice.

### Cited Findings
- Blender Guru's beginner donut series was fully reworked for Blender 4.0 (episodes released from Nov 2023); it covers interface, modelling, sculpting, shading, geometry nodes, lighting, compositing, animation and rendering, and the chapter list runs to about 4 h 29 min — [Blender Guru](https://www.blenderguru.com/tutorials/blender-4-beginner-donut-tutorial); [BlenderNation](https://www.blendernation.com/2023/11/18/blender-guru-blender-4-0-tutorial/). No 4.2-specific version found.
- A community GitHub repo works through the 14 donut lessons in Blender 4.0 with a .blend per lesson (useful to recover if stuck) — [GitHub thecrazymage/Blender-Donut-Tutorial](https://github.com/thecrazymage/Blender-Donut-Tutorial).
- Grant Abbitt has a free beginner YouTube series "Beginner Blender 4.2 Tutorial – Modelling a Low-Poly Well", parts of roughly 13 min each, aimed at beginners and game development — [Class Central listing](https://www.classcentral.com/course/youtube-beginner-blender-4-2-tutorial-modelling-a-low-poly-well-part4-326168); video: [YouTube "Create A Low Poly Well"](https://www.youtube.com/watch?v=OlnkGCdtGEw).
- A written (Substack) version of the well targets Blender 4.5.1 and assumes basic interface familiarity — [Grant Abbitt Substack: Low-Poly Well in Blender 4.5](https://grantabbitt.substack.com/p/create-a-low-poly-well-in-blender); also a written low-poly axe tutorial using modifiers, knife and bevel tools — [Substack: Low-Poly Axe](https://grantabbitt.substack.com/p/crafting-a-low-poly-axe-in-blender).
- Grant Abbitt "Essential Tips for Low Poly Scenes" (~12 min, Nov 2024): complexity reduction, triangles vs n-gons, object count, empties for organisation — [BlenderNation](https://www.blendernation.com/2024/11/05/essential-tips-for-low-poly-scenes-blender-tutorial/); [Class Central](https://www.classcentral.com/course/youtube-essential-tips-for-low-poly-scenes-blender-tutorial-366750).
- Grant Abbitt's paid GameDev.tv/Udemy "Low Poly Characters" and "Low Poly Landscapes" bite-size courses target Blender 3.0 (older but still usable) — [Udemy Low Poly Characters](https://www.udemy.com/course/blender-low-poly-characters/); [GameDev.tv Low Poly Characters](https://www.gamedev.tv/courses/1526965).
- Polygon Runway offers a free "Full Blender 4 Course for Complete Beginners 2024" covering core concepts and a first low-poly illustration start to finish (chapters include subdivision, array modifier, orthographic camera) — [BlenderNation Bazaar listing](https://bazaar.blendernation.com/listing/full-blender-4-course-for-complete-beginners-2024-polygon-runway/). Paid flagship "Become a 3D Illustrator" (25+ h, listed at $99) — [Polygon Runway Teachable](https://polygonrunway.teachable.com). Older free isometric scene tutorials are Blender 2.8 — [Class Central Polygon Runway](https://www.classcentral.com/institution/polygon-runway).
- Imphenzia: long-running free "10 minute" speed-modeling videos with on-screen keys and voiceover, e.g. "10 low poly cars in 10 minutes" — [BlenderNation](https://www.blendernation.com/2020/07/07/speed-modeling-10-low-poly-cars-in-10-minutes/); a newer "Step by Step Low Poly Modeling in Blender 4.4" whose palette texture is public domain — [YouTube 0GPJCdYCLnA](https://www.youtube.com/watch?v=0GPJCdYCLnA); "Low Poly Characters in Blender – Beginner Tutorial" — [YouTube K84MA4e7S38](https://www.youtube.com/watch?v=K84MA4e7S38); full "LEARN LOW POLY Character Modeling – Blender 3.5" course (modeling, rigging, animating, exporting, May 2023) — [YouTube PTWV67qUX2k](https://www.youtube.com/watch?v=PTWV67qUX2k), stage .blend files on [Patreon](https://www.patreon.com/imphenzia/posts/blend-files-from-82796714).
- A "Crash Course: Low Poly Fantasy Props in Blender 5" listing was surfaced only by a low-quality aggregator page; attribution to Imphenzia unconfirmed — [aggregator](https://irc.pcper.com/low-poly-3d-props.html) (treat as unverified).

### Inferences
- Suggested 1-week path (researcher's inference, ~2 h/day per person):
  - Day 1: Polygon Runway free Blender 4 beginners course (interface, navigation, G/R/S, edit mode, extrude, loop cut, modifiers) OR Blender Guru donut parts 1 to 3 only (skip sculpting/rendering/compositing chapters, irrelevant for OBJ export).
  - Day 2: Grant Abbitt Blender 4.2 low-poly well series (beginner prop workflow end to end).
  - Day 3: Grant Abbitt "Essential Tips for Low Poly" + Imphenzia "Step by Step Low Poly Modeling in Blender 4.4" (palette-texture workflow, which maps perfectly to "one PNG per mesh").
  - Days 4 to 5: model 2 to 3 real project props (cone, bin, barrier) and push them through OBJ export into the engine to validate the pipeline early.
  - Days 6 to 7: one bigger asset (scooter or facade module) with Mirror/Array/Bevel.
- Imphenzia's palette-texture (flat colour atlas) approach is the best fit for this engine's "one OBJ = one mesh = one texture" constraint: all props can share a single small palette PNG, UVs are just dragged onto colour swatches, no unwrapping skill required.
- Blender Guru donut is high quality but its rendering/shading half (Cycles, nodes, compositing) does not transfer to a Phong OBJ engine; time-boxing to the modeling chapters saves ~2 h.

### Gaps
- Could not confirm a dedicated CG Boost low-poly game-asset course for Blender 4.x (search did not surface it).
- No Kenney-authored modeling tutorial found (Kenney is relevant as an asset source / style reference, see section 4/5).
- No sourced beginner time-to-productivity figures; the 1-week plan is inference.

## 2. Core techniques and modifiers for hard-surface props; which are safe for game export

### Takeaway
Blockout from primitives, then Mirror, Array (optionally + Curve), Bevel (1 to 2 segments, angle-limited), Solidify and simple Booleans are all safe because the OBJ exporter has "Apply Modifiers" on export; shading is controlled with Shade Flat / Shade Smooth by Angle (a modifier since Blender 4.1) or Weighted Normal, and the resulting split/custom normals are written to OBJ when "Normals" is ticked.

### Cited Findings
- Blender OBJ exporter options (5.2 manual): Selected Only, Scale, Forward/Up Axis (Blender is Y forward, Z up), UV Coordinates, Normals ("face or vertex normals, depending on the smooth setting"), Colors, Curves as NURBS, **Triangulated Mesh**, **Apply Modifiers** ("exports the mesh after modifiers are evaluated"), **Apply Transform** (vertices in world space; off = local object space), Object/Material/Vertex Groups, Smooth Groups, Write MTL, PBR extensions, Path Mode (Auto/Absolute/Relative/Match/Strip/Copy) — [Blender manual: Wavefront OBJ](https://docs.blender.org/manual/en/latest/files/import_export/obj.html).
- Blender 4.1: the mesh "Auto Smooth" option was removed and replaced by a "Smooth by Angle" modifier node-group asset; "Custom normals are used if available"; "The base state of meshes is now the same as having 'Auto Smooth' on with an angle of 180 degrees in older versions"; in Edit Mode there is a new "Set Sharpness by Angle" operator, elsewhere "Shade Smooth by Angle" — [Blender 4.1 release notes, Modeling](https://developer.blender.org/docs/release_notes/4.1/modeling/).
- The right-click "Shade Smooth by Angle" is a one-shot operation; the interactive equivalent is the Smooth by Angle modifier (Modifiers > Normals) with an angle and "ignore sharp edges" option; community advice is to keep it last in the stack (after Subdivision/Bevel) — [BlenderArtists](https://blenderartists.org/t/blender-4-1-auto-smooth-is-now-a-modifier-only/1488922); [GameDev.tv community](https://community.gamedev.tv/t/blender-4-1-changes-to-auto-smooth/245474); [Blender issue #116922](https://projects.blender.org/blender/blender/issues/116922). The 4.3 manual describes "Shade Auto Smooth" as adding a Smooth By Angle modifier — [Blender 4.3 manual, shading](https://docs.blender.org/manual/id/4.3/scene_layout/object/editing/shading.html).
- Implication for old tutorials: pre-4.1 videos tell you to tick "Auto Smooth" in Object Data > Normals; that checkbox no longer exists — [CG Cookie blog](https://blog.cgcookie.com/?p=17205).
- Weighted Normal modifier improves bevel shading and allows lower-resolution bevels; it stores custom normal data; OBJ export carries it if "Normals" is checked (forum, anecdotal) — [BlenderArtists bevel best practice](https://blenderartists.org/t/bevel-best-practice/1529225).
- Common hard-surface stack advice: Bevel with "Angle" limit method (~30 to 40 degrees), 1 to 2 segments, "Clamp Overlap" on, then Weighted Normals (vendor blog, lower quality source) — [Tripo3D blog](https://www.tripo3d.ai/blog/explore/smart-mesh-weighted-normals-workflow-for-low-poly).
- Game engines do not read Blender modifiers, they must be applied (or applied on export) — [StraySpark checklist](https://www.strayspark.studio/blog/game-ready-asset-checklist-blender-2026).
- Grant Abbitt's low-poly axe tutorial is a short worked example of modifiers + knife + bevel on a game prop — [Substack](https://grantabbitt.substack.com/p/crafting-a-low-poly-axe-in-blender).

### Inferences
- Safe-for-this-engine summary (inference from manual + engine loader):
  - **Mirror** (scooter, bench, barrier, rider): safe; keep "Clipping" on, apply-on-export.
  - **Array** (fence posts, facade windows, street segments of 20 m): safe; with "Merge" on for continuous pieces. Array + **Curve** is safe geometry-wise but beginners should avoid it except for e.g. a curved railing.
  - **Bevel**: safe; keep to 1 to 2 segments for low/mid-poly so silhouettes catch Phong highlights without raising tri counts.
  - **Solidify**: safe (signs, canopy roofs, bin lid); watch for flipped normals if thickness is negative.
  - **Boolean**: geometry is exported fine, but produces n-gons and long thin triangles; because the engine fan-triangulates n-gons, concave n-gons from Booleans can render wrongly unless "Triangulated Mesh" is ticked on export (Blender then does a proper triangulation). Rule: always tick Triangulated Mesh.
  - **Subdivision Surface**: avoid or keep level 1; it multiplies tri count by 4 per level.
  - **Decimate**: only for downloaded high-poly assets; it destroys UVs/topology on hand-made low-poly models.
  - **Smooth by Angle / Weighted Normal**: safe; the exported `vn` per face corner is deduplicated by the loader per (pos, uv, normal) triple, so hard edges survive. Smooth groups (`s`) are ignored by the engine, so "Smooth Groups" export option is irrelevant; "Normals" must be on.
- Because Phong lighting with one point light exposes faceting, the "stylized low/mid poly" look is best achieved either with pure flat shading (Shade Flat, faceted look, cheapest) or with Smooth by Angle ~30 to 40 degrees plus small bevels on hard edges.

### Gaps
- Did not verify whether Blender's OBJ "Apply Modifiers" correctly includes custom normals from Weighted Normal in 5.x (only forum evidence); should be tested once in-engine.

## 3. Concrete approaches and (inferred) beginner time estimates per asset class

### Takeaway
Everything should start as a primitive blockout at real-world scale on the 1 m grid; props are 1 to 3 h each for beginners, the scooter ~1 day, a modular facade kit ~2 to 3 days, and the Kröpcke clock ~1 day from photos. (All durations are researcher inference, not sourced.)

### Cited Findings
- Modular kit principles (from Bethesda's GDC 2013 "Modular Level Design for Skyrim" by Joel Burgess and Nate Purkeypile): a kit is a system typically snapped to a grid; keep grid snaps large; use non-uniform footprint sizes sparingly — [Slides (SlideShare)](https://www.slideshare.net/slideshow/gdc2013-kit-buildingfinal/17728576); [Game Developer write-up](https://gamedeveloper.com/design/skyrim-s-modular-approach-to-level-design).
- The Level Design Book (based on Burgess's talks): "DO NOT MAKE VARIANTS YET, just build basic pieces first"; set units and build to human scale; keep each module inside a defined footprint/bounding box; agree on a naming pattern; typical module types include walls, doorways, windows, corners and "glue" pieces; texture variations are a cheap way to add variety without retesting geometry; stress-test loops, stacks, gaps — [The Level Design Book: Modular kits](https://book.leveldesignbook.com/process/blockout/metrics/modular).
- Polycount practitioners: model to a fixed grid instead of relying on vertex snapping; one kit used power-of-two sizes (32/64/128 units); for an off-grid width (1.25 m window wall in a 1 m/2 m kit) add filler pieces of 25/50/75 cm — [Polycount thread](https://polycount.com/discussion/comment/2688497); [Polycount thread](https://polycount.com/discussion/comment/2688653).
- Example free kit on a strict 1 m grid: 24 pieces, floors/walls from 1x1 to 8x8 — [Modular Blueprint Kit (itch.io)](https://tuily.itch.io/modular-blueprint-kit).
- Kenney City Kit (Roads), CC0, ships OBJ (and FBX/DAE/STL/glTF), roads with separate barriers, highways, lightposts, construction fences, road signs, traffic lights (65+ to 90 models; count differs between listings) — [itch.io](https://kenney-assets.itch.io/city-kit-roads); [OpenGameArt](https://opengameart.org/content/city-kit-roads). Companion City Kit (Suburban) and (Commercial) are designed to fit with Roads — [OpenGameArt Suburban](https://opengameart.org/content/city-kit-suburban); [OpenGameArt Commercial](https://opengameart.org/content/city-kit-commercial).
- E-scooter: no free dedicated low-poly scooter tutorial was found; the closest is a paid vintage (Vespa-style) scooter course, but it is a 53K-tri high-to-low-poly PBR bake pipeline (not suitable here) — [Superhive Market](https://superhivemarket.com/products/vintage-retro-scooter---aaa-game-ready-asset--3d-model--full-tutorial). Generic low-poly vehicle tutorials (primitives, extrude, loop cuts, mirror) transfer — [BlenderNation Low Poly Vehicles (2.8)](https://www.blendernation.com/2019/09/02/low-poly-vehicles-easy-blender-2-8-tutorial/); [Imphenzia 10 cars in 10 min](https://www.blendernation.com/2020/07/07/speed-modeling-10-low-poly-cars-in-10-minutes/).
- Kröpcke clock (Kröpcke-Uhr): original 1885 multifunctional weather column ("Wettersäule") by architect Conrad Oertel, designed to match the dome of the adjacent Café Robby; its top was a helmet-like cap over the clockwork; substructure of steel profile frames, shaped sheet metal and glazed side panels; demolished 1954, replaced 1955 by a Karl Cravatzo design; the current clock is a 1977 replica of the 1885 original and since ~2005 serves as a display case for art exhibitions — [de.wikipedia: Kröpcke-Uhr](https://de.wikipedia.org/wiki/Kr%C3%B6pcke-Uhr); [en.wikipedia: Kröpcke](https://en.wikipedia.org/wiki/Kr%C3%B6pcke). It stands where Georgstraße, Karmarschstraße, Bahnhofstraße and Rathenaustraße meet — [hannover.de / visit-hannover](https://www.visit-hannover.com/en/Media/visit-hannover/Teaserlinks/Hannover-inside/Top-10/Wo-man-sich-in-Hannover-verabredet).

### Inferences
(All time estimates = researcher inference for a beginner after the 1-week learning phase, including UV-onto-palette and test export; double them for the first asset of each type.)
- **(a) Simple props**, each from 1 to 3 primitives, ~200 to 1,500 tris:
  - Traffic cone (~0.5 to 1 h): Cylinder with 8 to 12 sides, scale top verts to a point/small radius (cone), separate thin square base (cube, bevel 1 seg). Colour bands = separate faces assigned to palette colours (loop cut + UV to swatch).
  - Wheelie bin / Mülltonne (~1.5 to 2.5 h): cube blockout 0.6 x 0.75 x 1.05 m, taper bottom (scale bottom loop), inset + extrude for the lid rim, Bevel small; wheels = 8 to 12-sided cylinders, axle; Mirror on X. Use Solidify for the lid overhang.
  - Construction barrier (Baustellenbake / barrier fence) (~1 to 2 h): plane/cube board with stripes via palette UV (or a tiny striped PNG), Array for the feet/posts, Mirror.
  - Bench (~1 to 2 h): one slat (cube + bevel), Array x4 for seat and backrest, legs Mirrored.
  - Street lamp (~1 to 2 h): cylinder pole (8 sides), extrude-and-scale for base and top, arm as extruded cube, lamp head as a flattened cube/cylinder. Emissive look can be faked with a bright palette colour (engine has one point light, no emission).
- **(b) E-scooter (~4 to 8 h)**: blockout with real dimensions (approx. 1.1 to 1.2 m long, deck ~0.15 m high, handlebar ~1.1 to 1.2 m; dimensions are approximate common-knowledge values, verify against a photo/spec sheet). Deck = cube with bevel; stem = cylinder (8 to 12 sides) tilted; handlebar = cylinder with Mirror; wheels = 12 to 16-sided cylinders with inset hub. Keep wheels and handlebar/stem as **separate OBJ files** so code can spin wheels and lean/steer (the engine merges all objects of an OBJ into one mesh and has no hierarchy). Origin of each wheel at its axle centre.
- **(c) Modular facades / street segments (~2 to 3 days for a starter kit)**:
  - Set Scene units Metric, unit scale 1.0; grid = 1 m; snap to Increment/Grid (Absolute Grid Snap) while blocking.
  - Pick a fixed module set, e.g. facade wall modules 4 m wide x 3.5 m per storey (ground floor shop module, upper-floor window module, corner module, roof/cornice strip), plus street segment 20 m long x (3 lanes x ~3 m + sidewalks). Lane width ~3 m is inference consistent with typical road lanes.
  - Model one module, put the origin at a consistent corner (e.g. bottom-left-front or segment start at z=0) so the game code can place pieces at integer metre offsets; make variants only after the base pieces tile (Level Design Book rule).
  - Use Array (relative offset 1.0, or constant offset = module width) to preview tiling in Blender; check seams by placing two copies end to end.
  - Variety cheaply through texture/palette swaps rather than new geometry (Level Design Book). Kenney City Kit pieces can serve as filler/background and as a scale reference (CC0), while the team's own modules are the graded, Hannover-specific foreground.
- **(d) Kröpcke clock from photo references (~5 to 10 h)**: gather front/side photos, load as Reference/Background images in orthographic views; block out as stacked cylinders/octagonal prisms (base plinth, glazed shaft = column with inset window panels, clock section with faces on each side, domed "helmet" cap from a UV sphere half or a spun profile via Screw modifier). Clock faces = a separate small texture (or palette + a dedicated clock-face PNG; since one mesh = one texture, put clock faces and the column on one atlas, or export clock faces as a separate OBJ with its own PNG). Stylise: fewer segments (8 to 16), exaggerate the cap and clock faces for readability at speed.

### Gaps
- No source found for beginner time-per-asset figures; all estimates are inference.
- Exact height/dimensions and number of clock faces of the Kröpcke-Uhr not found in the sources fetched (neither Wikipedia nor hannover.de results stated it); the team should estimate from photos (e.g. compare with a person of ~1.75 m in a photo).
- E-scooter real dimensions not sourced; verify against a manufacturer spec sheet.

## 4. Stylized rider/character cheaply, given no skeletal animation

### Takeaway
Model a blocky "segmented" low-poly rider (Imphenzia/Grant Abbitt low-poly character style, PS1-style), exported as separate rigid OBJ parts (torso, head, upper/lower arms, legs) and animated by code transforms; this is cheap (~1 to 2 days, inference) and counts as own work, while CC0 packs are a fallback.

### Cited Findings
- Imphenzia "Low Poly Characters in Blender – Beginner Tutorial" builds a simple template then three characters from it — [YouTube K84MA4e7S38](https://www.youtube.com/watch?v=K84MA4e7S38); full low-poly character course (Blender 3.5) covers modeling, rigging, animation, export — [YouTube PTWV67qUX2k](https://www.youtube.com/watch?v=PTWV67qUX2k).
- Grant Abbitt "PlayStation 1 Characters in Blender" (~19 min, beginner): reference images, mirrored modeling, UV unwrapping, painting a retro texture — [Class Central](https://www.classcentral.com/course/youtube-playstation-1-characters-in-blender-486471).
- Imphenzia also sells "Crispoly Characters Mini" (135 rigged colourised characters with Blender files) — paid; rigs would be useless in this engine — [imphenzia.com](https://imphenzia.com/crispoly-characters-mini).
- Engine fact: ObjLoader merges all objects in one file into one mesh and ignores groups — `Engine/Geometry/Loaders/ObjLoader.cs` (this repository).

### Inferences
- Since there is no skeleton, the cheapest approach is "rigid-part puppet": model the rider in a riding pose (standing on deck, hands on handlebar) with Mirror, then split into ~6 to 10 parts (Separate by selection, P), set each part's origin at its joint pivot (shoulder, elbow, hip, knee, neck), and export each part as its own OBJ with "Selected Only". In code, compose parent-child matrices manually (e.g. lowerArm = local * upperArm * torso * scooter) using the engine's left-to-right row-vector convention. Animations needed for a runner (lean left/right for lane switch, crouch for duck, hop for jump) are just a few rotations, which is very feasible.
- Caveat on part export: with "Apply Transform" on, vertices are written in world space; to have each part's mesh centred on its pivot, either move the part to the world origin before export or export with Apply Transform off (local space). The team should pick one rule and document it.
- Even simpler fallback: rider as a single rigid mesh welded to the scooter, with whole-body lean/bob in code; then only the jump/duck needs a different pose or a squash scale.
- Skipping the rider is not recommended: it is the most visible asset, and a blocky stylized character in a helmet hides face-modelling difficulty (helmet = UV sphere half, visor = palette colour).
- Downloaded CC0 characters (e.g. from Kenney or Quaternius) are a fallback only; rigged models would need to be posed and split in Blender anyway, and graded work should be self-made.

### Gaps
- Did not verify current Kenney/Quaternius character pack licences/formats in this research pass (asset-source research likely covered by another researcher).

## 5. Add-ons that speed up beginners; are Geometry Nodes worth it?

### Takeaway
Since Blender 4.2 most formerly bundled add-ons (LoopTools, Bool Tool, Extra Mesh Objects, etc.) must be installed with one click from the Extensions platform inside Preferences; for beginners LoopTools (Circle/Relax), Bool Tool and Extra Mesh Objects are useful, Building Tools is a GitHub add-on for quick buildings; Geometry Nodes are generally not worth learning in a 4 to 6 week project except possibly via ready-made assets.

### Cited Findings
- Blender 4.2 LTS launched the Extensions Platform (extensions.blender.org) for free/open-source GPL-compatible add-ons and themes, installable and updatable from within Blender — [Blender 4.2 LTS release](https://www.blender.org/?p=92674); [desdelinux coverage](https://blog.desdelinux.net/en/blender-4-2-lts-arrives-with-unification-of-extensions-and-themes%2C-improvements-in-eevee-cycles-and-more/).
- Most add-ons that used to ship with Blender are no longer pre-installed; install them from the Extensions tab of Preferences — [CG Cookie: everything new in 4.2](https://cgcookie.com/posts/everything-new-in-blender-4-2).
- LoopTools is no longer in the default add-ons list since 4.2 and must be installed from Extensions (community-maintained) — [Blender manual issue #104878](https://projects.blender.org/blender/blender-manual/issues/104878); [LoopTools on extensions.blender.org](https://extensions.blender.org/add-ons/looptools/reviews/?page=3).
- Bool Tool is on the Extensions platform (by nickberckley), formerly bundled up to 4.1 — [Renderjuice: Bool Tool](https://www.renderjuice.com/blender/extensions/bool-tool). Extra Mesh Objects is listed on Extensions as a community add-on — [extensions.blender.org community](https://extensions.blender.org/team/community/) (move date not confirmed).
- Building Tools (ranjian0/building_tools): installed from the GitHub release zip via Preferences > Add-ons, then used from the N-panel tab "Building Tools"; wiki last edited May 2022; not found on extensions.blender.org — [GitHub wiki: Installation](https://github.com/ranjian0/building_tools/wiki/Installation/images/source_code_zip.png) (repo: github.com/ranjian0/building_tools).
- Blender Guru's 4.0 donut includes a Geometry Nodes chapter (sprinkles scattering), i.e. beginners do meet GN early — [Blender Guru](https://www.blenderguru.com/tutorials/blender-4-beginner-donut-tutorial).

### Inferences
- Recommended minimal add-on set (inference): LoopTools (Circle for round holes/wheels, Relax), Bool Tool (fast cut-outs for windows/doors), Extra Mesh Objects (gears, rounded cubes, etc.). Built-in features that matter more than any add-on: Snap to grid/increment, Mirror/Array/Bevel modifiers, 3D Print Toolbox-style checks are replaced by the built-in Select > Select All by Trait > Non Manifold and the Face Orientation overlay.
- Archimesh (walls/windows/doors generator) is architectural-interior oriented; its output is high in object count and not stylized; not verified for 5.x in this research. Building Tools could produce quick facades but is unmaintained-looking (2022 wiki) and its output may need cleanup (n-gons, many objects); try it for 30 minutes and drop it if fiddly.
- Geometry Nodes: for 2 beginners in 4 to 6 weeks (code + art), learning procedural buildings is a poor time investment; Array modifiers + a hand-made modular kit gives the same result for a runner. GN output must be applied (it is, via OBJ "Apply Modifiers") but procedural UVs are an extra hurdle.
- Note: grading rewards own models; add-on-generated buildings may be judged as less "own work" than hand-modelled modules.

### Gaps
- No 2024 to 2026 Reddit/forum consensus on "Geometry Nodes for beginners in game projects" was retrieved; recommendation is inference.
- Did not confirm Building Tools / Archimesh compatibility with Blender 4.2+/5.x.

## 6. Common beginner mistakes that break game export, and how to avoid them

### Takeaway
Apply scale/rotation (Ctrl+A), avoid negative scale, check Face Orientation (blue = outside), recalculate normals (Shift+N), tick Triangulated Mesh + Normals + UV + Apply Modifiers in the OBJ exporter, place origins deliberately, and keep one mesh per texture; test-export the first prop into the engine on day 4 or 5.

### Cited Findings
- Unapplied scale is the most-reported import problem; apply scale and rotation (Ctrl+A) before export — [Unity Discussions](https://discussions.unity.com/t/blender-to-unity-normals-just-fine-in-blender-but-screwed-up-in-unity/177468); [StraySpark game-ready checklist 2026](https://www.strayspark.studio/blog/game-ready-asset-checklist-blender-2026).
- Negative scale (mirroring by scaling across the origin) flips normals; check with the Face Orientation overlay (blue = correct, red = flipped) and recalculate outside — [Unity Discussions](https://discussions.unity.com/t/blender-to-unity-normals-just-fine-in-blender-but-screwed-up-in-unity/177468).
- A misplaced pivot/origin makes the asset rotate around an arbitrary point in-engine — [StraySpark checklist](https://www.strayspark.studio/blog/game-ready-asset-checklist-blender-2026).
- Engines don't evaluate Blender modifiers; apply them (or use "Apply Modifiers" on export) — [StraySpark checklist](https://www.strayspark.studio/blog/game-ready-asset-checklist-blender-2026); OBJ exporter "Apply Modifiers", "Apply Transform", "Triangulated Mesh", "Normals", "UV Coordinates", Forward/Up axis options — [Blender manual: OBJ](https://docs.blender.org/manual/en/latest/files/import_export/obj.html).
- Community export checklist thread (GameDev.tv) — [GameDev.tv community: My export checklist](https://community.gamedev.tv/t/my-export-checklist/49951).
- Grant Abbitt's low-poly tips video covers triangles vs n-gons and object count management — [BlenderNation](https://www.blendernation.com/2024/11/05/essential-tips-for-low-poly-scenes-blender-tutorial/).
- Engine: n-gons are fan-triangulated; materials/usemtl ignored; all objects in one file merged; smoothing groups ignored — `Engine/Geometry/Loaders/ObjLoader.cs` (this repo).

### Inferences
Project-specific export checklist (inference combining manual + engine code + CLAUDE.md conventions):
1. Units: Metric, 1 unit = 1 m; model at real size (bin ~1 m tall), never fix size via object scale.
2. Ctrl+A > All Transforms (or at least Rotation & Scale) before export; no negative scale (use Mirror modifier instead of scaling by -1).
3. Overlays > Face Orientation: everything blue; fix with Mesh > Normals > Recalculate Outside (Shift+N). Back-face culling is ON in the engine (CCW front), so a flipped face becomes invisible, not just dark.
4. Select > Select All by Trait > Non Manifold / Loose Geometry to find holes and stray verts; Mesh > Clean Up > Merge by Distance (M > By Distance) to remove duplicate vertices from Mirror/Array.
5. Export with: Triangulated Mesh ON (avoids fan-triangulating concave n-gons from Booleans/insets), Normals ON, UV Coordinates ON, Apply Modifiers ON, Write MTL OFF (ignored anyway), Forward -Z / Up Y (as in CLAUDE.md), Selected Only when exporting parts.
6. One OBJ = one mesh = one texture: everything in a file shares one PNG; join parts into one object or export separately where code needs to move them (wheels, rider limbs).
7. Every face needs UVs mapped into the texture (unmapped UVs default to (0,0) or overlapping, giving wrong colours); with a palette texture, just scale UV islands down and drop them on the right swatch.
8. Origin: put it where code expects it (ground contact at y=0 centred for props; module corner for kit pieces; axle for wheels; joint for rider limbs).
9. Keep the .blend source and the exported .obj/.png under `RunnerGame/Assets/`, and re-export after every change; don't hand-edit OBJ files.
10. The first test should happen early: export a cube-level prop, load via ObjLoader, view in engine with the single point light, and confirm orientation, scale and shading before modeling everything.
- PNG colour: the engine does no sRGB conversion (CLAUDE.md), so palette colours may look slightly different (lighter/washed out) in-engine than in Blender; tweak palette in the PNG rather than in Blender.

### Gaps
- Did not find an official Blender manual page that lists "beginner export mistakes" as such; sources are community/vendor checklists (quality mixed) plus the manual's option list.
- Did not test whether Blender's "Forward -Z / Up Y" export exactly matches the engine's camera/track convention; this should be verified by the team with one asymmetric test object (e.g. a cone with an arrow).
