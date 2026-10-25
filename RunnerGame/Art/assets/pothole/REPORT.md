Approved and installed2026-10-23; source/runtime SHA256 verified via docs/art/street-props-install-plan.json.

# Pothole candidate report

Original procedural visual damage patch, no external source assets. One completed atlas bake session via read-only photo_lib (512 square, 32 samples, Blender 5.2.2, 8 threads). Editable source saved as editable.blend. No game installation or gameplay changes.

Actual export: 528 triangles (1500 ceiling), 1.191315 x 0.872024 m footprint, all surfaces at source Z 0.002502 to 0.014320 m. XY silhouette centred at ground origin. Jagged continuous five-ring surface with dark shallow bowl impression and 24 sparse angular aggregate pieces. Geometry deliberately remains above the current road rather than claiming excavation. Atlas fully opaque. All triangle areas positive, visible faces upward, normals unit length, UV/index ranges valid. Independent exported checks in out/export_checks.json; pre-bake geometry in out/geometry_checks.json.

Engine review standalone.png and road.png use the actual exported OBJ and texture, the latter on approved ST_Street_road.obj at unchanged road height 0. Readable dark centre, jagged lip and aggregate; no road occlusion or coplanar surface. Limit: shallow visual depression only; no hole collision, displaced road or trigger. Damage has slightly warmer asphalt tones than approved road and intentionally darker centre. No second bake needed. Final XY centring translated source/export together and preserved atlas/UV; original generated material coordinates are bbox-relative.

Commands (repository cwd, all native exit 0):

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --threads 8 --python-exit-code 1 --python RunnerGame/Art/assets/pothole/build.py -- --export
# Final source-only save after deterministic XY centring, no bake:
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --threads 8 --python-exit-code 1 --python RunnerGame/Art/assets/pothole/build.py
python RunnerGame/Art/assets/pothole/verify.py
.\tools\essential-scene\bin\Debug\net10.0\EssentialScene.exe RunnerGame/Art/assets/pothole/previews/standalone.json RunnerGame/Art/assets/pothole/previews/standalone.png
.\tools\essential-scene\bin\Debug\net10.0\EssentialScene.exe RunnerGame/Art/assets/pothole/previews/road.json RunnerGame/Art/assets/pothole/previews/road.png
```

Current build.py includes centring, so a fresh export reproduces the final geometry directly. Build logs preserve initial bake and final source-only exit. No modifiers, zero-area triangle filtering or shared library edits were required.
