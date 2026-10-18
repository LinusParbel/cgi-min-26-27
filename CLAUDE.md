# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository context

This is a team fork (`origin` = github.com/LinusParbel/cgi-min-26-27) of the CGI course repository
(upstream: github.com/LarsMohrmann/cgi-min-26-27). It contains a minimal C#/OpenTK engine provided
by the lecturer plus our own game project.

- `Engine/` — course engine (library). Upstream receives lecture updates via tags
  (`git fetch upstream --tags && git merge --no-edit lecture-XX`), so keep local engine edits small
  and isolated to avoid merge conflicts. Engine changes meant for upstream follow `CONTRIBUTING.md`:
  one topic per PR, never rename/remove public classes, methods or shader uniforms, build with zero
  warnings, English only, and only add assets we are allowed to share.
- `Example/` — the lecturer's reference app. Leave it unchanged.
- `RunnerGame/` — **our university project**, a 3-lane endless runner ("Hannover Rush Hour").
  It started as a copy of `Example/` (namespace is still `Example`, window class `CubeWindow`).
  The game design draft is `RunnerGame/Hannover_Rush_Hour_Game_Design_and_3D_Asset_Plan.md`.
  That doc was written engine-agnostic (it mentions Unity/Godot/Unreal, glTF, PBR, LODs); the
  constraints of *this* engine, listed below, take precedence.

## Commands

Requires the .NET 10 SDK and an OpenGL 3.3 driver. There is no test project and no linter;
verification means a warning-free build plus actually running the app.

```powershell
dotnet build CgiMin.sln
dotnet run --project RunnerGame/RunnerGame.csproj
dotnet run --project Example/Example.csproj
```

VS Code: `Ctrl+Shift+B` builds the solution; `F5` offers "Example (OpenTK)" and "RunnerGame (OpenTK)".

## Engine architecture

**Frame loop** (`Engine/Application.cs`, derives from OpenTK `GameWindow`): a game overrides
`Initialize`, `FramebufferResized`, `FixedUpdate(dt)` (fixed 1/50 s, max 5 catch-up steps then the
remainder is dropped), `Update(dt)`, `Render()` and `Shutdown()`. The OpenTK `On*` callbacks are
sealed. `Render()` receives no time on purpose — all state changes happen in the update methods.
Input is read from OpenTK's `KeyboardState` (inherited from `GameWindow`) inside `Update`.

**Drawing** has exactly one path: `OpenGlRenderer.Draw(mesh, material, modelMatrix, camera)`.
There is no scene graph, entity system, batching or instancing — the game keeps its own list of
objects and calls `Draw` per object per frame. The renderer compiles each `ShaderSource` on first use,
caches it, and sets `uModel`, `uView`, `uProjection` (required in every shader) plus
`uCameraPosition` / `uLightPosition` only if the shader declares them. There is a single point light
(`renderer.LightPosition`); depth test and back-face culling (CCW front) are on, blending is off.

**Materials** (`Engine/Materials/Material.cs`): a material holds only uniform values and points to a
static `ShaderSource`; it owns no GPU resources. Textures are referenced, not owned — whoever creates
a `Texture`/`Mesh` disposes it in `Shutdown`. A new material is a folder `Materials/<Name>/` with the
class and its `.vert.glsl`/`.frag.glsl`; the csproj already embeds `Materials\**\*.glsl` as
`EmbeddedResource`. `ShaderSource` resolves resources by namespace and falls back to a *unique* file
name, so GLSL file names must be unique within an assembly.

**Math convention — easy to get wrong:** OpenTK uses row vectors. Shaders compute
`vec4(p,1) * uModel * uView * uProjection`, and C# matrices compose left-to-right in application
order: `Matrix4.CreateScale(s) * Matrix4.CreateRotationY(a) * Matrix4.CreateTranslation(t)`
scales first, then rotates, then translates. Normal matrix in shaders:
`localNormal * transpose(inverse(mat3(uModel)))`.

**Geometry and assets:**
- `MeshData` (CPU) → `Mesh` (GPU VAO/VBO/EBO). `Vertex` = position, normal, UV.
  `Primitives.CreateCube(size)` is the only built-in primitive.
- `ObjLoader` reads `.obj` only (`v`/`vt`/`vn`/`f`, polygons are triangulated). `.mtl` is ignored, so
  one OBJ = one mesh = one material; a multi-material model must be split into several OBJ files or
  use a single texture atlas. There is no glTF/FBX loader and no skeletal animation.
- `Texture.FromFile` uses StbImageSharp, uploads RGBA8 with repeat wrapping and mipmaps, no sRGB
  conversion.
- Files under `<Project>/Assets/` are copied to the output; load them with
  `Path.Combine(AppContext.BaseDirectory, "Assets", "...")`. Each project has its own `Assets/` folder.
- `Camera` defaults: FOV 50°, near 0.1, far **100** — raise `FarPlane` for long runner tracks.

**Not provided by the engine** (the game must implement it or we add it): text/UI rendering, audio,
collision, scene/transform hierarchy, transparency, shadows, multiple lights.

## Working notes

- Several `.obj` assets are tens of thousands of lines (e.g. `duck_flat.obj`); do not read them whole.
- Blender export for this engine: OBJ with normals and UVs, triangulated, Y-up / −Z forward, 1 unit = 1 m,
  plus PNG textures.
- The shell is Windows; the solution builds identically from PowerShell or Git Bash.

## Game models and asset workflow

- Finished models: `RunnerGame/Assets/Models/<Category>/<Asset>/` (`Baustelle/…`, `Mull/Tonne`), OBJ + one PNG each;
  `mounts.json` next to a carrier gives where the Warnleuchte lamp sits. Load with
  `Path.Combine(AppContext.BaseDirectory, "Assets", "Models", ...)`.
- Models are built by script in `tools/asset-spike/` (Blender 5.2 headless + shared `asset_lib.py`) and published with
  `python tools/asset-spike/publish_models.py`. Read `tools/asset-spike/WORKFLOW.md` before touching assets:
  it fixes the model per step (haiku for sorting, sonnet for builders/reviewers), the image budget (one engine sheet per
  iteration, ≤4 references per object), ≤3 parallel agents and max 3 iterations.
- Do not edit `RunnerGame/Art/` or `tools/asset-viewer/` — they belong to the photo-to-model (Voi scooter) session.
