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

Two experimental maps currently use the older delivery paths:

```text
RunnerGame/Art/assets/hannover_pedestrian_blockout/out/
RunnerGame/Art/assets/hannover_public_realm/out/
```

Their meshes, textures and route metadata are runtime inputs to `--map` and
remain tracked. They are complete map packages rather than individual model
folders. A future move to `RunnerGame/Assets/Maps/<Map>/` must update map launch
commands, test inputs and any path references together.
