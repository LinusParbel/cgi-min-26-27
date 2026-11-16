# CGI-MIN 26/27

A small starting point for computer graphics with C# and OpenTK: a scene graph
with deferred rendering of a wall with 1000 objects (some of them transparent) and
800 moving point lights, a mouse camera and frustum culling with an octree. The
engine also contains forward materials for plain texturing, wave distortion,
reflection mapping, Blinn-Phong lighting, normal mapping, cube mapping and
transparency.

## Structure

- `Engine/Application.cs` is the base class for a program. It separates logic
  and drawing, similar to Unity (see below).
- `Engine/Camera.cs` describes a view by position, target and projection.
  Multiple camera instances can exist independently of each other.
  `Engine/MouseCamera.cs` steers a camera with mouse and keyboard (right mouse
  button + mouse = look around, WASD = move, Q/E = down/up, Shift = faster),
  `Engine/FlyCamera.cs` with the keyboard only (arrow keys, W/S).
- `Engine/Frustum.cs` contains the six clipping planes of a camera's view frustum
  (Hessian normal form), the sphere-in-frustum test for frustum culling and the
  box-in-frustum test for the octree; `renderer.GetFrustum(camera)` creates it with
  the current aspect ratio.
- `Engine/Scenes/` contains the scene graph: `SceneNode` (name, optional mesh and
  material, position, rotation, scale relative to the parent, children, world
  matrix), `Scene` (root node, `Update()` calculates all world matrices,
  `CollectVisible` fills a `RenderList`, `BuildOctree` sorts the static nodes into an
  octree), `RenderList` (visible opaque nodes and transparent nodes sorted from back
  to front) and `Octree<T>` (spatial index: elements are sorted by their bounding
  sphere into areas; the query skips every area outside the frustum).
- `Engine/Materials/` contains the abstract base class `Material` and one
  subfolder per material type with its class and GLSL files: `UnlitTexture/`
  (texture without lighting), `WaveDistortion/` (texture without lighting,
  vertices displaced by a sine wave; the phase `Wobble` is increased in `Update`),
  `ReflectionMapping/` (texture coordinates calculated from the normal in view
  space, so an environment texture appears reflected on the surface) and
  `AmbientDiffuseSpecular/` (texture lit by a directional light: ambient, diffuse
  and specular with the halfway vector, Blinn-Phong), `NormalMapping/` (like
  AmbientDiffuseSpecular, but the normal of every pixel comes from a normal map in
  tangent space), `CubeReflection/` (mirror: the reflected view direction picks
  the color from a cube map), `NormalMappingCubeSpecular/` (normal mapping with
  the cube map reflection as specular part) and `LitTexture/` (texture with Phong
  lighting using the reflection vector, contributed by a student),
  `TransparentTexture/` (texture with an alpha value, without lighting) and
  `TransparentLitTexture/` (texture with an alpha value, lit by the directional
  light). Every material has a `BlendMode` (`Opaque`, `AlphaBlend`, `Additive`); for
  transparent materials the renderer enables blending and disables depth writes.
  The shaders are embedded into `Engine.dll` as `EmbeddedResource`.
- `Engine/Deferred/` contains deferred rendering: `GBuffer` (framebuffer with
  three textures: color, world position, normal + shininess, and a depth buffer)
  and `DeferredRendering` (geometry pass into the G-buffer, then the light pass on
  the screen: the directional light on a fullscreen quad, every point light on a
  sphere as light volume with additive blending; `BeginTransparentPass()` copies
  the depth buffer to the screen for transparent objects drawn afterwards). The matching materials are in
  `Engine/Materials/Deferred/`: `GBufferMaterial` (color texture, normal map and
  shininess for the geometry pass) and the internal light pass materials.
- `Engine/Geometry/` contains geometry in main memory, without OpenGL: `Vertex`
  (position, normal, texture coordinate, tangent, bitangent), `MeshData` (vertices
  and triangle indices; it calculates the tangents and bitangents from positions
  and UVs and averages them at shared vertices, plus a bounding radius for
  frustum culling) and `Primitives` (`CreateCube()`, `CreateFullscreenQuad()`, `CreateSphere()`). `Loaders/ObjLoader` reads the
  geometry from Wavefront .obj files (`v`, `vt`, `vn`, `f`, including polygons and
  faces without UVs or normals) and also returns `MeshData`; `.mtl` files are ignored.
- `Engine/OpenGL/` contains `Mesh` (vertex and index buffer on the GPU),
  `Texture` (image as RGBA texture, loaded with StbImageSharp), `CubeTexture`
  (cube map from six images), `ShaderSource`
  (where a shader comes from), `ShaderProgram` (GLSL compilation and uniforms) and
  `OpenGlRenderer` (OpenGL state, shader management and draw call).
- `Example/` is the executable OpenTK application and references `Engine`.
  Images and other files in `Example/Assets/` are copied next to the application
  during the build.
- `CgiMin.sln` loads both projects together.

The example builds a scene graph: a wall with 1000 static objects (cube, stone,
torus and transparent pyramids) in front of it and a rotating carousel whose planets
carry moons. The static nodes are sorted into an octree once. The scene is lit by a
directional light and 800 moving point lights. In `Update` the nodes are moved, the
world matrices are calculated, and the visible nodes are collected in a render list
(static nodes via the octree, moving nodes one by one); `Render` only draws them:

```csharp
_scene.Update();                                   // in Update: world matrices
_scene.CollectVisible(frustum, camera.Position, _renderList);

_deferred.BeginGeometryPass();                     // in Render: 1. geometry pass
foreach (SceneNode node in _renderList.Opaque)
    _renderer.Draw(node, camera);
_deferred.DrawDirectionalLight(camera);            // 2. light pass on the screen
foreach (PointLight light in _visibleLights)
    _deferred.DrawPointLight(light, camera);
_deferred.BeginTransparentPass();                  // 3. transparent objects, back to front
foreach (SceneNode node in _renderList.Transparent)
    _renderer.Draw(node, camera);
```

The window title shows how many nodes and lights are visible and how many visibility
tests were needed. Keys: right mouse button + mouse = look around, WASD = move,
Q/E = down/up, Shift = faster, O = octree on/off, 1 = final image, 2/3/4 = color,
normal and position texture of the G-buffer, Escape = quit. The example of lecture 7
without scene graph is still available in the tag `lecture-07`, the forward rendering
example in the tag `lecture-06`. A single mesh can still be drawn with
`renderer.Draw(mesh, material, modelMatrix, camera)`; the camera is not a global
static class, and materials and cameras do not draw themselves.

A material only holds surface values and refers to its `ShaderSource`. It only
references textures; whoever created a texture has to dispose of it. The renderer
compiles each material shader once on the first `Draw` and releases it in
`Dispose`. The renderer sets `uModel`, `uView`, `uProjection`, `uCameraPosition`
and the light uniforms only if the shader uses them (a fullscreen quad needs no
matrices).

The light of the scene is a `DirectionalLight` (`Engine/Lighting/`): a direction
towards the light and an ambient, diffuse and specular color. It is set on the
renderer (`renderer.DirectionalLight = …`), and the renderer passes it as
`uLightDirection`, `uLightAmbientColor`, `uLightDiffuseColor` and
`uLightSpecularColor` to every shader that uses these uniforms.

## Frame sequence

A program derives from `Engine.Application` and only overrides these methods:

| Method | When | What for |
|---|---|---|
| `Initialize()` | once at startup | create renderer, meshes, materials |
| `FramebufferResized(width, height)` | after `Initialize` and on resize | adjust the viewport |
| `FixedUpdate(fixedDeltaTime)` | 0…n times per frame, fixed time step `FixedDeltaTime` (default 1/50 s) | physics, simulation |
| `Update(deltaTime)` | once per frame | animation, input, game logic |
| `Render()` | once per frame, after `Update` | drawing only |
| `Shutdown()` | once on exit | release GPU resources |

`Render()` deliberately receives no time: everything that moves is calculated in
`Update` or `FixedUpdate`, and `Render` only draws it. The OpenTK callbacks
(`OnUpdateFrame`, `OnRenderFrame`, etc.) are sealed. If `FixedUpdate` would have
to catch up more than five steps after a stutter, the remaining time is discarded.

## Running

Requirements: .NET 10 SDK, a graphics driver supporting OpenGL 3.3 and NuGet
access for the first build.

```powershell
dotnet build CgiMin.sln
dotnet run --project Example/Example.csproj
```

In Visual Studio Code, open the **repository folder** and confirm that you trust
it. `Ctrl+Shift+B` builds both projects; `F5` with the configuration
"Example (OpenTK)" starts the example. `Engine` is a library and is not run on
its own.

## Your own project

Do not work in the course repository. Clone it once, keep it as `upstream` and
push your work to your own Git repository:

```bash
git clone https://github.com/LarsMohrmann/cgi-min-26-27.git MyGame
cd MyGame
git remote rename origin upstream
git remote add origin https://github.com/<your-name>/<your-game>.git
git push -u origin main
```

Create your game as a copy of the example and leave `Example/` unchanged:

1. Copy the folder `Example/` to `MyGame/` and rename `Example.csproj` to `MyGame.csproj`.
2. Add it to the solution: `dotnet sln CgiMin.sln add MyGame/MyGame.csproj`
3. Run it: `dotnet run --project MyGame` (for `F5`, change the path in
   `.vscode/launch.json` to `MyGame/bin/Debug/net10.0/MyGame.dll`).

### Engine updates

The engine grows with every lecture. Each lecture state is tagged (`lecture-03`,
`lecture-04`, …), see [CHANGELOG.md](CHANGELOG.md). Update to a tagged state on
purpose, not just to the newest commit:

```bash
git fetch upstream --tags
git merge --no-edit lecture-03
```

Treat `Engine/` as read-only: if you do not change engine files, updates merge
without conflicts. Extend the engine in your own project instead. For example,
write your own material like `Example/Materials/NormalColor`: derive from
`Engine.Materials.Material`, put the `.glsl` files next to the class and embed
them with `<EmbeddedResource Include="Materials\**\*.glsl" />` in your `.csproj`.

Want to add something to the engine itself? Contributions are welcome as pull
requests, see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

The code is licensed under the [MIT License](LICENSE).
