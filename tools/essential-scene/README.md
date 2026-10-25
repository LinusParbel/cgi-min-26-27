# Essential asset review scene

Interactive 3D model viewer and screenshot runner using the existing engine and gamma-lit asset-viewer material unchanged. It does not implement game behaviour.

Run `dotnet run --project tools/essential-scene -- <scene.json> <output.png>`.

Open the complete installed street scene interactively:

```powershell
dotnet run --project tools/essential-scene -- docs/art/street-props-runtime-scene.json --show
```

Controls: WASD moves the free camera; Q/E moves down/up; hold right mouse and drag, or use arrow keys, to look around. Shift moves faster. R restores the initial view. Esc closes the viewer. Camera movement has no collisions, allowing close inspection of any mesh.

Scene JSON has `camera`, `target`, optional `light` (engine XYZ), optional `fov`, and `models`. Each model contains either `manifest` (existing parts.json) or `obj` + `texture`; paths are relative to scene.json. Optional `offset` is engine XYZ, `yaw` is degrees about engine Y, and `scale` defaults to 1. A `parts` list selects mutually exclusive poses/modules. Manifest pivots use the established Blender-to-engine conversion. Meshes and textures are shared across repeated instances.
