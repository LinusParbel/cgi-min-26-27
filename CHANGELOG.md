# Changelog

Each lecture state is tagged in Git. Update your own project with
`git fetch upstream --tags` and `git merge --no-edit lecture-XX`.
Changes that can break your own code are marked with **Breaking**.

## lecture-06

- New: `CubeTexture` (cube map from six images, +X, -X, +Y, -Y, +Z, -Z) and
  `ShaderProgram.SetCubeTexture`.
- New: `CubeReflectionMaterial` (normal map + cube map reflection) and
  `NormalMappingCubeSpecularMaterial` (normal mapping, cube map as specular part).
- New: `Frustum` with the sphere-in-frustum test, `renderer.GetFrustum(camera)` and
  `MeshData.BoundingRadius` / `Mesh.BoundingRadius` for frustum culling.
- New: `FlyCamera` – a camera steered with the keyboard.
- Example: 200 rotating objects with frustum culling, fly camera and three materials
  (keys 1/2/3); the hall scene of lecture 5 is still available in the tag `lecture-05`.

## lecture-05

- New: `NormalMappingMaterial` (color texture + normal map in tangent space, lit by the
  directional light like `AmbientDiffuseSpecularMaterial`).
- `Vertex` has two new fields, `Tangent` and `Bitangent` (attribute locations 3 and 4).
  `MeshData` calculates them automatically from positions and UVs and averages them at
  shared vertices. The existing `Vertex(position, normal, texCoord)` constructor still works.
- Example: a hall (`hall.obj`, `hall_color.png`, `hall_normal.png`) and a rotating cube
  (`blur_colors.png`, `pattern_normal.png`) with normal mapping; the camera circles around.
- The renderer resets the active texture unit to 0 after each draw call
  (materials may now use several textures).

## lecture-04

- New: `DirectionalLight` (`Engine/Lighting/`) with direction, ambient, diffuse and
  specular color; set it with `renderer.DirectionalLight = new DirectionalLight { … }`.
- New: `AmbientDiffuseSpecularMaterial` – texture lit by the directional light
  (ambient + diffuse + specular with the halfway vector, Blinn-Phong) and a `Shininess`.
- Example: the duck is drawn with `AmbientDiffuseSpecularMaterial` and the new
  `Assets/duck_texture.png`; the light is set in `Initialize`.
- New (pull request #1, thanks to Linus Parbel): `LitTextureMaterial` – texture with Phong
  lighting (reflection vector), plus `monkey.obj`, `monkey-smooth.obj` and `monkey.png`.
  It uses the directional light (`uLightDirection`) instead of the former `uLightPosition`.
- **Breaking:** `PhongMaterial` was removed, use `AmbientDiffuseSpecularMaterial`
  (it needs a texture).
- **Breaking:** `OpenGlRenderer.LightPosition` and the `uLightPosition` uniform were
  removed, use `OpenGlRenderer.DirectionalLight`.

## lecture-03

First tagged state of the engine.

- `Application` base class with `Initialize`, `FixedUpdate`, `Update`, `Render`, `Shutdown`
- Geometry: `Vertex`, `MeshData`, `Primitives.CreateCube`, `ObjLoader` (.obj files)
- OpenGL: `Mesh`, `Texture`, `ShaderProgram`, `ShaderSource`, `OpenGlRenderer`
- Materials: `UnlitTexture`, `WaveDistortion`, `ReflectionMapping`, `Phong`
- Example: own material in the application project (`Example/Materials/NormalColor`)
- `ShaderSource` also finds embedded shaders when the project's root namespace
  differs from the code's namespace (e.g. after copying `Example` to `MyGame`)
