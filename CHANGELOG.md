# Changelog

Each lecture state is tagged in Git. Update your own project with
`git fetch upstream --tags` and `git merge --no-edit lecture-XX`.
Changes that can break your own code are marked with **Breaking**.

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
