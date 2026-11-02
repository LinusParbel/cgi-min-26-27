# Runtime maps

Each map is a complete package under `Assets/Maps/<Map>/` containing `map.json`,
`route.json`, part manifests, OBJ meshes, PNG textures and source credits.
Manifest paths are relative to the map folder. Keep those files together.

From the repository root:

```powershell
dotnet run --project RunnerGame -- --map RunnerGame/Assets/Maps/HannoverPedestrianBlockout --overview
dotnet run --project RunnerGame -- --map RunnerGame/Assets/Maps/HannoverPublicRealm --inspect 245
```

The project copies maps to the build output under `Assets/Maps/`. Editable
sources and provenance remain under `RunnerGame/Art/assets/`; their generated
`out/` folders are ignored. Python generation scripts are local tooling.
