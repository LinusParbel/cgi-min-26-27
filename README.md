# CGI-MIN 26/27

A small starting point for computer graphics with C# and OpenTK: a rotating
model lit by a directional light (ambient, diffuse and specular, Blinn-Phong).
The engine also contains materials for plain texturing, wave distortion and
reflection mapping.

## Structure

- `Engine/Application.cs` is the base class for a program. It separates logic
  and drawing, similar to Unity (see below).
- `Engine/Camera.cs` describes a view by position, target and projection.
  Multiple camera instances can exist independently of each other.
- `Engine/Materials/` contains the abstract base class `Material` and one
  subfolder per material type with its class and GLSL files: `UnlitTexture/`
  (texture without lighting), `WaveDistortion/` (texture without lighting,
  vertices displaced by a sine wave; the phase `Wobble` is increased in `Update`),
  `ReflectionMapping/` (texture coordinates calculated from the normal in view
  space, so an environment texture appears reflected on the surface) and
  `AmbientDiffuseSpecular/` (texture lit by a directional light: ambient, diffuse
  and specular with the halfway vector, Blinn-Phong) and `LitTexture/` (texture
  with Phong lighting using the reflection vector, contributed by a student). The shaders are embedded into
  `Engine.dll` as `EmbeddedResource`.
- `Engine/Geometry/` contains geometry in main memory, without OpenGL: `Vertex`
  (position, normal, texture coordinate), `MeshData` (vertices and triangle
  indices) and `Primitives` (e.g. `CreateCube()`). `Loaders/ObjLoader` reads the
  geometry from Wavefront .obj files (`v`, `vt`, `vn`, `f`, including polygons and
  faces without UVs or normals) and also returns `MeshData`; `.mtl` files are ignored.
- `Engine/OpenGL/` contains `Mesh` (vertex and index buffer on the GPU),
  `Texture` (image as RGBA texture, loaded with StbImageSharp), `ShaderSource`
  (where a shader comes from), `ShaderProgram` (GLSL compilation and uniforms) and
  `OpenGlRenderer` (OpenGL state, shader management and draw call).
- `Example/` is the executable OpenTK application and references `Engine`.
  Images and other files in `Example/Assets/` are copied next to the application
  during the build.
- `CgiMin.sln` loads both projects together.

The example loads the duck from `Assets/duck_smooth.obj` with `ObjLoader` and
draws it with the `AmbientDiffuseSpecularMaterial` and `Assets/duck_texture.png`,
lit by the directional light that is set in `Initialize`. The other textures,
materials and meshes (cube, star, flat-shaded duck) are commented out in
`Initialize` and can be switched quickly. The mesh is drawn with
`renderer.Draw(mesh, material, modelMatrix, camera)`. The animation only changes
the model matrix; the camera is not a global static class. Materials and cameras
do not draw themselves. A scene model will follow in a later step.

A material only holds surface values and refers to its `ShaderSource`. It only
references textures; whoever created a texture has to dispose of it. The renderer
compiles each material shader once on the first `Draw` and releases it in
`Dispose`. Every material shader must use `uModel`, `uView` and `uProjection`;
`uCameraPosition` and the light uniforms are optional.

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
