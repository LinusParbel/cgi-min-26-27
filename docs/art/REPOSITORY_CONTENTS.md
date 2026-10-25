# Repository contents

The repository contains both the original street runner and the evolving Hannover pedestrian map. The two root `Play-*.cmd` launchers use the preserved local checkpoint when available, and otherwise build the requested mode with the .NET 10 SDK.

Committed material includes game and engine source, console test harnesses, installed runtime models/textures, the complete installed 40-pose officer animation, both map deliveries, asset builders/specifications, editable character rigs, licensed reference packs, provenance, credits and the professor-facing method note. The current renderer samples four of the officer poses; all forty remain available through the installed animation manifest.

Ignored material stays on disk: local playable snapshots, downloaded geodata and Python/add-on caches under `.model-research`, local app settings, compilation output, generated review images, duplicate export ZIPs, Blender autosaves and reproducible intermediate Blender files. Ignoring a previously tracked file does not remove it from history.

The committed map `out` directories are deliberate exceptions to the general art-output ignore rule: the game loads those files directly. Other asset exports are installed under `RunnerGame/Assets` before delivery.

A fresh clone can build and play both modes without the download cache or Blender. Rebuilding art from source may require Blender, MakeHuman/MPFB, the original licensed downloads and Python geometry packages described by each asset's instructions. Historical reports can refer to ignored local previews or research files; these are not runtime requirements. The printable HTML method note embeds its review images.

Frozen executable checkpoints remain local and are not uploaded to Git. The source and runtime art committed here preserve both game modes; copy `preserved-game-states` separately when backing up the exact local binary checkpoint.
