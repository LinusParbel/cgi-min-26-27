# Model folder convention

Installed game models use one layout:

```text
RunnerGame/Assets/Models/<Category>/<Asset>/
    <model>.obj
    <texture>.png
    <model>_parts.json       (when required)
    <model>_animation.json   (for animated models)
    mounts.json             (when required)
```

Keep meshes, their shared textures and runtime metadata together in the asset
folder. Existing categories are `Baustelle`, `Charakter`, `Fahrzeug`, `Gebaeude`,
`Mull`, `Pickup`, `Umgebung` and `Wahrzeichen`. Reuse those categories and the
existing asset names; game code refers to these paths. Existing mesh prefixes
such as `PROP_`, `PRP_`, `VEH_`, `CHR_` and `BLD_` are preserved.

Asset references, editable sources, specifications and provenance live in
`RunnerGame/Art/assets/<asset>/`. The asset register is
`RunnerGame/Art/ASSETS.md`; licensing is documented in `RunnerGame/CREDITS.md`
and the asset source records. Keep these records with the project.

Python generation, export, preview and geometry test scripts under
`RunnerGame/Art/`, `tools/asset-spike/` and `docs/art/` are local tooling. They
are ignored by Git and are not required for a clean checkout to run the game.
Historical build instructions in art handoffs refer to that local tooling.
The C# gameplay, input, rendering and route tests remain tracked.

## Map packages

Runtime map packages use `RunnerGame/Assets/Maps/<Map>/`:

```text
RunnerGame/Assets/Maps/HannoverPedestrianBlockout/
RunnerGame/Assets/Maps/HannoverPublicRealm/
```

Their meshes, textures, route metadata and credits remain together in each map
folder. They are runtime inputs to `--map` and are copied into the build output
alongside the model assets. Generation sources stay under `Art/assets/`.
