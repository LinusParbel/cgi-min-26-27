# tools/asset-spike — scripted asset pipeline

Builds the game's 3D models with Blender (headless, Python) and checks them in the course engine.
Finished models live in `RunnerGame/Assets/Models/<Category>/<Asset>/` (OBJ + PNG, one texture per mesh).

| Folder / file | Purpose |
|---|---|
| `asset_lib.py` | shared helpers: weathered materials, box/cylinder/image-plane, bake colour×AO, OBJ export, previews |
| `baustelle/gen_*.py` | one generator per Baustelle asset (Leitbake, Absperrschranke, Leitkegel, Zeichen 123, Warnleuchte) |
| `gen_wheelie_bin_v3.py` | German wheelie bins (Restmüll, Bio, Papier, Gelbe Tonne) |
| `publish_models.py` | copies finished OBJ/PNG/`mounts.json` from `out/` (scratch, git-ignored) to `RunnerGame/Assets/Models` |
| `SpikeViewer/` | renders models with the course engine: screenshots or interactive scene (`show_baustelle.ps1`) |
| `engine_sheet.sh`, `fetch_refs.sh` | merge screenshots into one image; polite Wikimedia reference download |
| `ref/signs/` | official StVO sign graphics (public domain) used as textures |
| `WORKFLOW.md`, `baustelle/BRIEF.md` | how we work (model routing, image/CPU budget, checklist) |

Rebuild one asset: `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup --python tools/asset-spike/baustelle/gen_leitkegel.py`,
then `python tools/asset-spike/publish_models.py`. Requires Blender 5.2, Python 3 with Pillow (some scripts), .NET 10.

## Models (v0.1)

| Category | Asset | Variants | Tris |
|---|---|---|---|
| Baustelle | Leitbake (Z605) on foot plate | `_rechts`, `_links` | 1802 |
| Baustelle | Absperrschrankengitter | `_gelb`, `_rotweiss` | 3676 |
| Baustelle | Leitkegel (Z610) | `_50`, `_75` | 1036 |
| Baustelle | Verkehrszeichen 123 Arbeitsstelle | post, `_mobil` | 1612 / 1904 |
| Baustelle | Warnleuchte (+ `lens_*` overlay for blinking) | `_gelb`, `_rot` | 1444 (+320) |
| Mull | Mülltonne 120 L | `restmuell`, `bio`, `papier`, `gelb` | 6.8k–9k |

Conventions: 1 unit = 1 m, front faces −Y in Blender (towards the runner camera), origin bottom-centre.
`mounts.json` next to a carrier = where the Warnleuchte sits (Blender coordinates, Z up → engine Y up).

## Notes for the game

- Engine lighting shows colours ~0.72× darker until gamma-correct lighting exists; don't brighten textures.
- The lens overlay is 3 mm in front of the lamp lens: near plane ≥ 0.3 (or a depth bias) beyond ~40 m.
- Barrier gates in a row need ~2.25 m spacing (feet overhang).
- Reference photos (Wikimedia Commons, mixed CC licences) are not redistributed; only the models are ours.
  Official sign graphics in `ref/signs/` are public domain.
