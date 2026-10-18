# Blender texturing and OBJ export for a "one OBJ + one PNG per mesh" engine

Scope: getting textured models from Blender 4.2+/5.x into the course engine (C#/OpenTK, `ObjLoader` + `Texture.FromFile`), and converting downloaded multi-material assets to single-texture OBJ. Engine facts below were checked directly in the repository source (cited as local file paths).

Verified engine behavior (from repo source, relevant to all questions below):
- `ObjLoader` supports `v`, `vt`, `vn`, `f` in all four corner forms and negative indices. It fan-triangulates polygons and ignores `mtllib`/`usemtl`, `o`/`g` and `s`. **All objects in one file are merged into one mesh.** — [Engine/Geometry/Loaders/ObjLoader.cs](C:/Users/Saturn/Desktop/Studium/Master/ws_26_27/CGI/cgi-min-26-27/Engine/Geometry/Loaders/ObjLoader.cs)
- If a face corner has no `vn`, the loader gives every triangle its own flat face normal (so flat shading). Corners with no `vt` get UV (0,0). — same file
- `vt` origin is bottom-left, as in OpenGL. — same file
- `Texture.FromFile` calls `stbi_set_flip_vertically_on_load(1)`, uploads `PixelInternalFormat.Rgba8` (not sRGB), wrap = Repeat, min filter = `LinearMipmapLinear`, mag filter = `Linear`, and generates mipmaps. The comment says "there is no color space conversion (sRGB/gamma) for now." — [Engine/OpenGL/Texture.cs](C:/Users/Saturn/Desktop/Studium/Master/ws_26_27/CGI/cgi-min-26-27/Engine/OpenGL/Texture.cs)

---

## 1. Texturing strategies that fit "one texture per mesh" (palette, atlas, trim sheet, bake)

### Takeaway
For two beginners on a 4–6 week schedule, the best default is **palette/gradient texturing**: one small shared palette PNG, with each model's UVs scaled down onto color swatches. It needs almost no UV skill, keeps "one material per OBJ", and lets every prop share one texture. Use **baking to a single texture** only to convert downloaded multi-material models (or the occasional hero asset). A **trim sheet** is worth it only if facades become the visual focus and someone has spare time. In this engine, the linear and mipmap filtering means swatches must be large and padded, or colors bleed at a distance.

### Cited Findings
**(a) Palette / gradient texturing (Imphenzia-style)**
- The technique: scale a face's or object's UVs "down to a tiny number and drag the entire thing into the color [you] want" on a palette image. A user tied this to Imphenzia's low-poly videos. The same thread reports colors **bleeding** after export, which they suspected came from baking margins or GLB compression. — [Babylon.js forum](https://forum.babylonjs.com/t/uv-mapping-seems-to-be-blending-colors-from-the-texture/31632)
- Imphenzia sells a ready-made palette ("PixPal") "as seen in Imphenzia videos". v1.3 lists Blender 5, Unity 6.3, Unreal 5.7.3 and Godot 4.6.1 support. — [Payhip PixPal listing](https://payhip.com/b/8KOlD)
- A GitHub palette-texture generator credits Imphenzia for the method and links one of his videos. — [pateman/palette-texture-generator](https://github.com/pateman/palette-texture-generator)
- 80.lv describes gradient texturing as using small palette textures with gradient strips to suggest lighting and shadow on low-poly models. It argues this costs far less memory than a unique 2K/4K texture per asset. — [80.lv: Elevating gradient texturing](https://80.lv/articles/elevating-gradient-texturing-to-a-standard-workflow-in-blender)
- Commercial low-poly packs such as Synty "typically use one material with a texture atlas containing color palettes laid out in a grid". — [Unity Discussions: Palette Modifier](https://discussions.unity.com/t/released-palette-modifier-change-the-colors-of-low-poly-models-directly-inside-unity/760556)
- A free CC0 gradient atlas (1024x2304, 74 vertical gradients) claims "no UV mapping required" because UVs just point at a strip. — [itch.io Texture Gradient Palette](https://tenebra23.itch.io/texture-gradient-palette)
- Blender add-ons automate it. **UV Colorize** uses "a single material containing the png-colorpalette and the shifting of the UVs to the respective colors" and warns that scaling UVs to zero can break lightbaking. — [GitHub RouBroeck/UV-Colorize](https://github.com/RouBroeck/UV-Colorize). **Dynamic Color Palette** (official extensions platform): all faces share one material, and color comes from UV position. — [extensions.blender.org](https://extensions.blender.org/add-ons/dynamic-color-palette/). **Palette Grid** (paid). — [Superhive](https://superhivemarket.com/products/palettegrid/faq)
- A tutorial on the same idea recommends setting image interpolation to **Closest** for crisp edges. — [BlenderNation Bazaar "this blender scene uses only one texture"](https://bazaar.blendernation.com/listing/this-blender-scene-uses-only-one-texture-texture-atlas-colour-palette-tutorial/). The engine hard-codes `Linear` mag and `LinearMipmapLinear` min filtering, so Closest is not available without an engine change. — [Engine/OpenGL/Texture.cs](C:/Users/Saturn/Desktop/Studium/Master/ws_26_27/CGI/cgi-min-26-27/Engine/OpenGL/Texture.cs)

**(b) Texture atlases**
- An atlas is the same concept as a palette sheet. "I'd also call it a texture atlas", and gradients are just one way to paint it. — [Polycount comment](https://polycount.com/discussion/comment/2774452)
- Kenney Shape has an "atlas" texture export option that produces a texture of color swatches. — [Kenney Shape documentation](https://www.kenney.nl/knowledge-base/tools/kenney-shape-documentation)
- Material atlasing can't handle UVs outside 0–1 (tiling textures). glTF-Transform can merge materials only when their properties match exactly or differ only in base color. — [Babylon.js forum: Draft Atlas Material](https://forum.babylonjs.com/t/draft-atlas-material/60370)

**(c) Trim sheets**
- Polycount forum consensus: trims "don't remove texel density; the useless pixels are simply removed from the texture map". That shifts the burden onto UV layout. Unique maps suit instanced props, and tileables/trims suit large unique world geometry. Trim bevels tolerate being stretched, but wildly different densities are noticeable. For modular pieces, "model to the grid". — [Polycount 1](https://polycount.com/discussion/comment/2593030), [Polycount 2](https://polycount.com/discussion/comment/2593443/), [Polycount 3](https://polycount.com/discussion/comment/2592840), [Polycount trim-sheet tag](https://polycount.com/discussions/tagged/trim-sheet/p1)
- Uniform texel density across a level is the general goal, "but that rule doesn't hold for every asset". Density can vary to focus detail. — [Polycount](https://polycount.com/discussion/comment/2800746), [Polycount](https://polycount.com/discussion/comment/2800914)

**(d) Bake multiple materials or procedurals into one diffuse texture**
- Cycles bake type **Diffuse** has Influence toggles. Lighting: *Direct*, *Indirect*. Contributions: *Color*. "Color alone gives the surface's base pass color, independent of sampling." Without Color, Direct/Indirect come out grayscale. — [Blender 5.2 Manual: Render Baking](https://docs.blender.org/manual/en/latest/render/cycles/baking.html)
- The bake target is "the image of the active, selected Image Texture node. If a material lacks one, nothing is baked for it." The mesh needs a UV map. — [Blender Manual: Render Baking](https://docs.blender.org/manual/en/latest/render/cycles/baking.html)
- **Lightmap Pack** "places each face separately, maximizing texture use". The result is disconnected and distorted, so it suits baking, not manual texturing. Its options include *New UV Map*, *Share Texture Space* and *Margin*. — [Blender Manual: UV unwrapping operators](https://docs.blender.org/manual/en/latest/modeling/meshes/editing/uv.html)
- The native workflow from a forum thread: add a second UV map, then bake into it. The poster calls it fiddly. — [Blender Artists](https://blenderartists.org/t/can-i-bake-multiple-materials-on-an-object-into-a-single-texture/1342354)
- A free video tutorial covers combining materials into one diffuse texture (made in 2.9, said to work in 2.8/3.0). — [BlenderNation Bazaar](https://bazaar.blendernation.com/listing/how-to-bake-multiple-materials-into-one-texture/)
- Paid one-click add-ons: **Multi-Mat Baker** creates a second UV channel, packs it, bakes diffuse/normal/roughness and restores the original materials (Blender 3.0–4.x). — [Superhive docs](https://superhivemarket.com/products/bake-multiple-materials-into-one-pbr-texture-set-in-one-click/docs). **Easy Texture Baker** is listed as Blender 5.x compatible. — [Superhive](https://superhivemarket.com/products/easy-bake). **MultiBake** (Blender 3.5–4.5) can join objects first. — [Gumroad](https://shift4cube.gumroad.com/l/MultiBake)

### Inferences
- **Recommendation and time cost (estimate, not sourced):**
  - *Palette:* about 1 hour to learn, then minutes per prop. Best fit for a low-poly runner (cars, trams, Litfaßsäule, benches, signs).
  - *Atlas of real image textures:* moderate effort. Useful when bundling a few downloaded textures.
  - *Trim sheet:* high upfront effort (designing the sheet plus careful UVs), but pays off for many facades. Probably overkill for 4–6 weeks unless one person owns "buildings".
  - *Bake-to-one:* 15–60 min per model while learning, and it is the only way to flatten procedural or multi-material sources.
- **Palette rules for this engine.** The engine uses bilinear filtering with trilinear mipmaps. A UV point that sits exactly on a swatch boundary will blend neighbors, and higher mip levels average adjacent swatches together. So:
  - Use few, large swatches, e.g. a 256x256 or 512x512 PNG with 16–32 px solid blocks, or 8x8 blocks of 32 px.
  - Keep collapsed UVs in the swatch center.
  - Optionally duplicate edge pixels.
  This matches the "colors blending" complaint in the Babylon thread.
- Because the engine merges all objects in an OBJ into one mesh with one texture, a palette lets a team combine e.g. a whole bus with wheels into one OBJ with zero extra materials.
- Gradient strips (dark-to-light within a swatch) give a cheap fake-AO look, which partly compensates for the missing shadows (see Q3).

### Gaps
- I could not locate Imphenzia's specific video URL or title through search. The GitHub generator README links one, and his YouTube channel is the primary source. The report writer should not cite a specific video title.
- I found no Polycount *wiki* page (only forum threads) on trim sheets or texel density in the search results.
- I found no source on whether Material Combiner handles procedural or node-heavy materials (see Q5).

---

## 2. UV unwrapping basics for beginners

### Takeaway
Beginners should rely on four operators: **Mark Seam + Unwrap (U)** for organic or curved props, **Smart UV Project** for hard-surface or architectural props, **Project from View** for flat facades and signs, and **Lightmap Pack** (on a new UV map) only for baking. For palette texturing, UV quality barely matters, because faces are scaled onto swatches. Margin between islands matters mainly for baked textures.

### Cited Findings
- **Unwrap (U)** "cuts along seams, flattens, and lays out the faces". It overwrites existing UVs. Methods: *Angle Based*, *Conformal* (LSCM, better on simpler objects) and *Minimum Stretch* (SLIM). Options include *Fill Holes*, *Correct Aspect*, and *Margin Method* (Scaled / Add / Fraction). — [Blender Manual: UV operators](https://docs.blender.org/manual/en/latest/modeling/meshes/editing/uv.html)
- **Smart UV Project** cuts at sharp edges and projects each group along its average normal. It is "suited to mechanical objects and architecture". Options: *Angle Limit* (higher means fewer, larger, more distorted islands), *Margin Method*, *Island Margin*, *Rotation Method*, *Area Weight*, *Correct Aspect*, *Scale to Bounds*. — [Blender Manual](https://docs.blender.org/manual/en/latest/modeling/meshes/editing/uv.html)
- **Project from View** projects faces onto the view plane and stretches areas that recede from the viewer. *Project from View (Bounds)* turns on Scale to Bounds by default. **Cube / Cylinder / Sphere Projection** exist. Cube sides overlap unless you run Pack Islands. **Follow Active Quads** extends from an active quad, ignores non-quads and may go out of bounds. — [Blender Manual](https://docs.blender.org/manual/en/latest/modeling/meshes/editing/uv.html)
- Bake **Margin** extends pixels past UV islands "to prevent seam artifacts from filtering and mip-mapping". *Type*: Extend or Adjacent Faces. *Size* is in pixels. — [Blender Manual: Render Baking](https://docs.blender.org/manual/en/latest/render/cycles/baking.html)
- Texel density: keep it roughly uniform between assets in a level, with deliberate exceptions. — [Polycount](https://polycount.com/discussion/comment/2800746)

### Inferences
- **Beginner workflow:**
  1. Tab into Edit Mode and select all (A).
  2. Run UV > Smart UV Project (or press U > Smart UV Project). Use the default angle and an Island Margin of about 0.01–0.02 if the result will be baked.
  3. In the UV Editor, run UV > Average Islands Scale, then UV > Pack Islands with a margin.
  4. Check the result with a checker texture (Image > New > Generated Type: UV Grid or Color Grid).
- Because the engine uses mipmaps, island margins need to be a few pixels at the base resolution. Bake margin of about 8–16 px at 1024² is a common rule of thumb (not sourced here).
- Wrap mode is Repeat, so UVs outside 0–1 tile. That is useful for tiling road or pavement textures on a single-texture mesh, but it breaks atlasing.

### Gaps
- The manual excerpt I fetched did not list numeric defaults (e.g. the Smart UV Angle Limit default) or the *Pack Islands* and *Average Islands Scale* options. Verify these in the Blender UI.
- I did not retrieve dedicated beginner video tutorial URLs (e.g. Grant Abbitt or Blender Guru UV series) in this session. The report writer should add these only if separately verified.

---

## 3. Baking AO or lighting into the diffuse texture to fake shadows

### Takeaway
Baking **ambient occlusion** (grayscale) and multiplying it into the base color is a good, cheap trick for static props and buildings in a runner. It adds contact darkening and grounding that the engine's single-point-light Phong cannot produce. Do **not** bake full direct lighting (Combined, or Diffuse with Direct). In a runner, objects pass a moving light and camera, so baked directional light would contradict the engine's dynamic Phong light. AO is light-direction-independent, which is why it is safe.

### Cited Findings
- Bake type **Ambient Occlusion** "uses the settings in the World panel and ignores scene lights". **Shadow** bakes shadows and lighting. **Combined** includes materials, textures and lighting (not specularity). — [Blender Manual: Render Baking](https://docs.blender.org/manual/en/latest/render/cycles/baking.html)
- **Diffuse** with *Direct/Indirect* plus *Color* gives colored lit results. *Color* alone gives the unlit base color. — [Blender Manual: Render Baking](https://docs.blender.org/manual/en/latest/render/cycles/baking.html)
- Gradient palettes are used precisely to suggest lighting and shadow on low-poly models without unique textures. — [80.lv](https://80.lv/articles/elevating-gradient-texturing-to-a-standard-workflow-in-blender)
- UV Colorize warns that zero-scaled palette UVs can break light baking. — [UV-Colorize README](https://github.com/RouBroeck/UV-Colorize)

### Inferences
- **Practical AO-into-diffuse steps:**
  1. Give the model a proper non-overlapping UV map (Smart UV or Lightmap Pack).
  2. Bake Diffuse > Color only into image A.
  3. Bake Ambient Occlusion into image B.
  4. Combine them, either in the Compositor or Shader Editor with a MixRGB "Multiply" node feeding an Emission shader, then bake Emit; or in GIMP/Krita with a Multiply layer.
  5. Save the combined image as the PNG.
- AO baking **conflicts with palette texturing**. Collapsed palette UVs have no unique texel space, so AO needs a unique UV layout and its own texture per mesh. Choose per asset: palette (shared texture, no AO) or unique baked texture (AO possible). Gradient swatches are the palette-world substitute.
- A simpler alternative that needs no baking: a fake blob shadow (a dark quad under cars and props). That requires blending, which is off in the engine, so use an opaque dark decal mesh slightly above the ground instead.
- Baked AO on the *ground* tiles around buildings only works if those tiles are unique, not repeated. Usually skip that for an endless track.

### Gaps
- I found no source specifically evaluating baked AO in endless-runner games. The recommendation is reasoned from bake semantics and the engine's lighting model.

---

## 4. Exact OBJ export settings (Blender 4.x/5.x C++ "Wavefront (.obj)" exporter) and pre-export prep

### Takeaway
Use **File > Export > Wavefront (.obj)** with:
- Forward Axis **-Z**, Up Axis **Y** (these match this engine, and to my knowledge they are the exporter defaults)
- Scale 1.0
- Apply Modifiers **on**, Properties: Viewport or Render
- UV Coordinates **on**, Normals **on**
- **Triangulated Mesh on**
- Write MTL / PBR Extensions off (ignored anyway)
- Selected Only on when exporting one prop from a shared .blend

Before export: apply transforms (Ctrl+A > All Transforms), set the origin to bottom-center, and put the object at the world origin. The "Apply Transform" export option bakes world-space positions into the vertices, and the engine merges all objects in the file into one mesh.

### Cited Findings
- Export options in the Blender 5.2 manual (File > Export > Wavefront .obj):
  - **General:** *Include: Selected Only*; *Scale* (global scale); *Forward Axis / Up Axis* ("Blender uses Y Forward, Z Up"); *Apply Modifiers* (export the evaluated mesh); **Apply Transform** ("bakes location, rotation, and scale into world-space vertices; when off, vertices stay in local object space"); *Properties* (Viewport or Render evaluation, e.g. Subdivision levels).
  - **Geometry:** *UV Coordinates* (writes the **active** UV layer); *Normals* ("writes face and vertex normals, depending on the smooth setting"); *Colors* (vertex colors as the "xyzrgb" extension); *Curves as NURBS*; *Triangulated Mesh* (splits quads into two triangles).
  - **Grouping:** *Object Groups*, *Material Groups*, *Vertex Groups*, *Smooth Groups*, *Smooth Group Bitflags*.
  - **Materials:** *Write MTL file*, *PBR Extensions*, *Path Mode* (Auto / Absolute / Relative / Match / Strip Path / Copy).
  - **Animation:** one numbered OBJ per frame.
  - **Notes:** OBJ does not support armatures, lights, cameras, empties, parenting or transforms. NURBS surfaces, text and metaballs are converted to meshes.
  — [Blender 5.2 LTS Manual: Wavefront OBJ](https://docs.blender.org/manual/en/latest/files/import_export/obj.html)
- **Blender 4.1 normals change:** the "Auto Smooth" option was removed and "replaced by a modifier node group asset" ("Smooth by Angle"). Meshes now behave as if Auto Smooth were on at 180°. Face-corner split normals are computed automatically when sharp and smooth elements are mixed, and custom normals are used when present. In Edit Mode use **"Set Sharpness by Angle"**; in Object Mode use **"Shade Smooth by Angle"**. — [Blender 4.1 Release Notes: Modeling](https://developer.blender.org/docs/release_notes/4.1/modeling/)
- Engine side: without `vn`, each triangle gets a flat face normal. With `vn`, identical (position, UV, normal) corners are shared. Polygons are fan-triangulated, which is only correct for convex polygons. — [Engine/Geometry/Loaders/ObjLoader.cs](C:/Users/Saturn/Desktop/Studium/Master/ws_26_27/CGI/cgi-min-26-27/Engine/Geometry/Loaders/ObjLoader.cs)
- The Python API equivalent is the operator `bpy.ops.wm.obj_export`. Its parameter list should be checked with `help(bpy.ops.wm.obj_export)` in Blender's console. — [Blender Python API: bpy.ops.wm](https://docs.blender.org/api/current/bpy.ops.wm.html) (the page was too large to extract the signature in this session)

### Inferences
- **Pre-export checklist:**
  1. Ctrl+A > All Transforms, so scale reads 1.0 and rotation 0, and normals and UV scale are clean.
  2. Set the origin to bottom-center. In Edit Mode, select the bottom face or vertices and press Shift+S > Cursor to Selected. Back in Object Mode, run Object > Set Origin > Origin to 3D Cursor.
  3. Move the object to (0,0,0), with Shift+S > Selection to World Origin or Alt+G. This step is essential when *Apply Transform* is on, otherwise the world offset is baked into the vertices.
  4. Set 1 unit = 1 m.
  5. Run Mesh > Clean Up > Merge by Distance.
  6. Check face orientation: Viewport Overlays > Face Orientation, then Mesh > Normals > Recalculate Outside (Shift+N). This matters because the engine culls back faces (CCW front).
- **Flat vs smooth:**
  - *Shade Flat* means each face has its own normal. The exporter writes split normals, the file gets more `vn` entries and more engine vertices, and the look is faceted. This is the typical low-poly style.
  - *Shade Smooth* means shared normals, which give a soft look.
  - *Shade Smooth by Angle* (4.1+), or marked sharp edges, gives smooth surfaces with hard edges. The exporter writes the split normals, and the engine respects `vn`, so this works.
  - Unchecking *Normals* also yields flat shading in this engine, because the loader computes face normals.
- **Triangulate in Blender** (export option, or a Triangulate modifier with Apply Modifiers). Blender triangulates n-gons robustly. The engine's fan triangulation can produce wrong triangles on concave n-gons.
- **File size:** OBJ is text. Flat shading and UV seams multiply `vn`/`vt` lines, and every vertex line is roughly 30–40 bytes. A 2–5k-triangle prop stays well under 1 MB. Avoid Subdivision Surface modifiers with Apply Modifiers on, because they multiply polycount.
- The axis defaults (-Z forward, Y up) are, to my knowledge, the defaults of the 3.x+ C++ exporter. They match the CLAUDE.md convention, but confirm them in the dialog.
- If several parts (e.g. car body plus wheels) are exported together, they become one static mesh in the engine. Animate wheels separately by exporting them as separate OBJs. Then use a local origin, not world-baked: export each part individually at the world origin.

### Gaps
- The manual excerpt did not state default values for the OBJ export options. Default states for Apply Modifiers, Normals, UV, Triangulate and Materials should be confirmed in the Blender 4.2/5.x dialog.
- The removal of the legacy Python OBJ exporter in Blender 4.0 (the C++ exporter arrived in 3.2/3.3) was not re-verified with a source in this session, though it is widely known. The report writer should cite the Blender 4.0 release notes (Import/Export) if stating it.
- The exact `bpy.ops.wm.obj_export` keyword names (e.g. `forward_axis='NEGATIVE_Z'`, `up_axis='Y'`, `export_triangulated_mesh`, `export_materials`, `export_selected_objects`, `apply_modifiers`, `export_uv`, `export_normals`) come from memory and were not verified against the API page.

---

## 5. Converting downloaded multi-material GLB/FBX/glTF into a single-texture OBJ

### Takeaway
First check whether the pack already uses a single shared texture. Many modern Kenney packs ship a texture per pack, and those models become single-texture OBJs with a straight import and export. Otherwise:
1. Import the GLB into Blender.
2. Join the parts (Ctrl+J).
3. If every material is just a flat color, either reassign UVs onto a palette or bake Diffuse Color to one image.
4. If materials are textured, use Material Combiner (free, GPL) or a bake to a new Lightmap-Pack UV map.
5. Export OBJ.

Command-line tools (assimp, gltf-transform) convert formats but do not merge materials into one texture for you.

### Cited Findings
- Kenney ships OBJ, FBX and GLB. "FBX and GLB (glTF) files are equal in features but GLB is smaller". Kenney advises avoiding OBJ unless it is the only supported format. Each pack has its own texture set in a "Textures" folder, and missing colors usually mean the included texture wasn't assigned. — [Kenney: Importing 3D models into game engines](https://kenney.nl/knowledge-base/game-assets-3d/importing-3d-models-into-game-engines)
- Older Kenney packs have no texture file and use multiple flat-colored materials. — [GDevelop forum](https://forum.gdevelop.io/t/auto-importing-glb-textures/60374)
- A Construct 3 plugin devlog notes support for GLB with a single embedded diffuse texture only. A forum tip says to export models referencing the shared texture rather than embedding it, so each model doesn't carry a copy. — [itch.io devlog](https://itch.io/devlog/343359/glb-and-gltf-support-with-single-embedded-texture.amp), [Construct forum](https://www.construct.net/en/forum/users/andrea-nedra-1698359/posts)
- **Material Combiner** (GPL-3.0) combines materials into a texture atlas to reduce draw calls "without quality loss" and avoids problems with UVs larger than 0–1.
  - It mixes diffuse colors with textures, with a configurable atlas size and per-texture size. Materials without an image default to 32 px.
  - Install: download the **master branch zip** (not Releases), then Preferences > Add-ons > Install from file.
  - Use: in the 3D Viewport press N, open the **MatCombiner** tab, tick materials per object, then click "Save atlas to..".
  - Limitations: packed textures must be unpacked (File > External Data); only supported shaders work; non-English UI can break node detection; multi-map atlasing exists only in old versions; the Windows Store Blender may not work; the Pillow dependency sometimes needs a manual pip install.
  — [GitHub Grim-es/material-combiner-addon](https://github.com/Grim-es/material-combiner-addon)
- **gltf-transform** CLI (`npm i -g @gltf-transform/cli`) offers commands such as `join`, `flatten`, `prune` and `dedup`. — [gltf-transform.dev/cli](https://gltf-transform.dev/cli), [skills.cat asset pipeline summary](https://skills.cat/skills/anthemflynn/dwc/asset-pipeline-3d). An `atlas` command existed in very old versions (0.0.11) and may not exist in v4. — [socket.dev](https://socket.dev/npm/package/@gltf-transform/cli/diff/0.0.11). Material merging works only for materials that are identical or differ only in base color. — [Babylon.js forum](https://forum.babylonjs.com/t/draft-atlas-material/60370)
- **assimp** CLI converts formats: `assimp export input.glb output.obj` (format from the extension), with `assimp listexport` to list formats. It ships in the `assimp-utils` package on Debian/Ubuntu. — [TechOverflow 2025](https://techoverflow.net/2025/03/31/how-to-convert-dae-file-to-obj-on-the-command-line/), [LinuxCommandLibrary](https://linuxcommandlibrary.com/man/assimp). One user reports per-vertex color lost (greyscale) when exporting OBJ. — [LinuxQuestions](https://linuxquestions.org/questions/programming-9/simple-assimp-import-and-export-problem-4175734652/)
- Paid bake add-ons for multi-material to one texture: Multi-Mat Baker, Easy Texture Baker (5.x), MultiBake. — see Q1 links.
- Bake target rule: every material on the object needs the active Image Texture node pointing at the target image, "if a material lacks one, nothing is baked for it". — [Blender Manual: Render Baking](https://docs.blender.org/manual/en/latest/render/cycles/baking.html)

### Inferences
**Step list A: model already uses one shared texture** (newer Kenney packs, and many Quaternius/KayKit-style packs; verify per pack)
1. File > Import > glTF 2.0 (.glb/.gltf).
2. Select all mesh parts and press Ctrl+J to join them (the engine merges them anyway).
3. Confirm that only one material and image remain (Material Properties).
4. Ctrl+A > All Transforms, then set the origin to bottom-center at the world origin.
5. Export OBJ with the Q4 settings.
6. Copy the pack's PNG into `RunnerGame/Assets/`.

**Step list B: flat-color multi-material model** (old Kenney packs, many Quaternius models)
- **Option 1, palette remap (fast, no baking):**
  1. Make or download a palette PNG.
  2. Join the parts.
  3. In Edit Mode, select faces by material: Material Properties > select slot > *Select*.
  4. In the UV Editor, scale those faces to about 0 (S 0) and move them onto the matching swatch.
  5. Repeat for each slot.
  6. Remove all material slots except one, and point it at the palette.
  7. Export.
- **Option 2, bake:**
  1. Join the parts.
  2. Add a new UV map (Object Data > UV Maps > +), make it active, then run UV > Lightmap Pack (or Smart UV Project) with a margin.
  3. Create an image (e.g. 512² or 1024², non-alpha).
  4. In *every* material, add an Image Texture node with that image and make it the active (selected) node. Do not connect it.
  5. Switch Render Engine to Cycles, set Bake Type: Diffuse, Influence: Color only (Direct/Indirect off), Margin about 8–16 px, then click Bake.
  6. Save the image as PNG (Image > Save As).
  7. Replace all materials with one that samples the image via the new UV map.
  8. Delete the old UV map, so that the exported *active* UV layer is the baked one.
  9. Export.

**Step list C: textured multi-material model** (Sketchfab): use Material Combiner (atlas) or Step B option 2. Baking also flattens procedural nodes.

- **Metallic gotcha (unsourced):** the Diffuse color pass of a fully metallic Principled BSDF bakes as black. Set Metallic to 0 before baking, or bake via Emission (connect Base Color to an Emission shader and bake *Emit*).
- **Headless batch option (unsourced detail):** run `blender -b -P convert.py -- in.glb out.obj`. The script calls `bpy.ops.import_scene.gltf(filepath=...)`, joins meshes, then `bpy.ops.wm.obj_export(filepath=..., forward_axis='NEGATIVE_Z', up_axis='Y', export_triangulated_mesh=True, export_materials=False)`. This converts geometry but does not merge textures, unless the script also bakes.
- assimp or gltf-transform alone are useful only when the source already uses one texture. They also lack Blender's origin and transform fixes.

### Gaps
- I could not confirm the specific texture file names in Kenney packs (e.g. "colormap.png") or how Quaternius packs are textured. Search returned nothing authoritative. Check individual pack contents.
- I did not determine the latest Blender version Material Combiner supports. Its README does not state it.
- I could not verify whether current gltf-transform (v4) has any atlas or texture-merge command.
- License compatibility of downloaded assets (CC0 Kenney/Quaternius vs Sketchfab CC-BY) was out of scope but matters for upstream sharing per CONTRIBUTING.md.

---

## 6. PNG texture pipeline gotchas (power-of-two, V flip, color space, file size)

### Takeaway
**Flip:** Blender's OBJ `vt` and the engine are both bottom-left-origin, and the engine flips images on load. So textures exported from Blender should appear correct with **no manual flip**. If a texture looks upside down, the cause is an extra flip somewhere, not the exporter.

**Color space:** the engine does no sRGB decode or encode. A PNG authored in sRGB, as everything painted or baked-and-saved from Blender is, is sent to the screen roughly as-is. Unlit or ambient-dominated colors therefore look like they do in an image viewer. Lit shading is "gamma-incorrect" (harsher falloff) and won't match Blender's Filmic/AgX viewport. That is acceptable for a course project and consistent as long as the engine never enables sRGB on only one side.

**Size:** use power-of-two sizes (256–1024) because of mipmaps, and RGB PNGs, which are small.

### Cited Findings
- The engine flips vertically on load because "Image files start at the top left, OpenGL expects the first row at the bottom". — [Engine/OpenGL/Texture.cs](C:/Users/Saturn/Desktop/Studium/Master/ws_26_27/CGI/cgi-min-26-27/Engine/OpenGL/Texture.cs). The OBJ loader treats `vt` origin as bottom-left "as in OpenGL". — [Engine/Geometry/Loaders/ObjLoader.cs](C:/Users/Saturn/Desktop/Studium/Master/ws_26_27/CGI/cgi-min-26-27/Engine/Geometry/Loaders/ObjLoader.cs)
- Textures are uploaded as `Rgba8` with no sRGB conversion. Mipmaps are generated, and filters are LinearMipmapLinear and Linear. — [Engine/OpenGL/Texture.cs](C:/Users/Saturn/Desktop/Studium/Master/ws_26_27/CGI/cgi-min-26-27/Engine/OpenGL/Texture.cs)
- The sRGB texture format and the sRGB framebuffer must match so each conversion happens exactly once:
  - Correct linear workflow: GL_SRGB8_ALPHA8 textures plus GL_FRAMEBUFFER_SRGB.
  - Turning sRGB off entirely is "also correct", but lighting is then computed on gamma-encoded values.
  - An sRGB texture without an sRGB framebuffer looks too dark.
  - An sRGB framebuffer without an sRGB texture looks washed out (gamma applied twice).
  — [Handmade Hero forum](https://hero.handmade.network/forums/code-discussion/t/1071/p/6090), [Khronos forum: OpenGL and sRGB confusion](https://community.khronos.org/t/opengl-and-srgb-confusion/76300), [Khronos forum: sRGB and normals](https://community.khronos.org/t/srgb-and-normals/66688)
- Kenney notes engine-specific color issues (Godot "High Quality" import, Unity "RGBA 32 Bit"). Texture compression and format can visibly shift palette colors. — [Kenney knowledge base](https://kenney.nl/knowledge-base/game-assets-3d/importing-3d-models-into-game-engines)

### Inferences
- **Color space consequences:** the engine has neither sRGB textures nor (presumably) an sRGB framebuffer, so it is consistently in "Fix B: no sRGB" mode. Texture colors display as authored. Blender's viewport uses a linear workflow plus a view transform (Filmic/AgX in 4.x/5.x), so lit renders in Blender look softer and brighter than in the engine. For color matching, preview in Blender with Color Management > View Transform = **Standard**. Do not use 16-bit or "Non-Color" data PNGs for albedo.
- **Bake save gotcha (unsourced):** saving a baked image as PNG writes 8-bit sRGB-encoded values. That is what the engine expects for albedo. Don't save albedo as EXR or float.
- **Power-of-two:** OpenGL 3.3 supports non-power-of-two textures, but with mipmaps and repeat wrapping, power-of-two sizes (128/256/512/1024) avoid filtering seams and waste. Use 256² or 512² for palettes and 1024² at most for hero props. VRAM per texture = w·h·4·1.33 (with mips): 1024² is about 5.3 MB and 512² about 1.3 MB.
- **PNG alpha:** blending is off, so alpha is ignored. Save as RGB (no alpha) to shrink files, and avoid relying on cut-out transparency (leaves, fences) unless a shader with `discard` is added.
- **Normal maps** won't work without a custom shader. Bake detail into the albedo (AO or cavity) instead.
- **JPG** also loads via StbImageSharp, but compression artifacts blur palette swatch edges. Use PNG for palettes.

### Gaps
- I did not verify whether the engine's default framebuffer is sRGB-enabled. Assumed not, because the texture comment says no conversion exists "for now". A future lecture update may add sRGB, which would change how textures should be authored. Re-check after `git merge lecture-XX`.
- I found no authoritative source quantifying the visual difference between gamma-space and linear Phong for this use case.
