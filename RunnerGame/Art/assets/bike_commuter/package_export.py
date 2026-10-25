"""Package checked bike exports and an editable source bundle, not old imports."""
from pathlib import Path
import json,zipfile
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent; OUT=HERE/'out'; PREV=HERE/'previews'
validation=json.loads((OUT/'validation.json').read_text())
assert validation['triangles']<=validation['budget']
sheet=Image.new('RGB',(1440,450),'#20252b'); draw=ImageDraw.Draw(sheet)
for i,(angle,label) in enumerate(((270,'RIGHT SIDE'),(35,'FRONT THREE-QUARTER'),(225,'REAR THREE-QUARTER'))):
    tile=Image.open(PREV/f'engine_{angle}.png').convert('RGB').crop((280,70,1000,700)).resize((480,420))
    sheet.paste(tile,(i*480,30)); draw.text((i*480+12,10),label,fill='white')
sheet.save(PREV/'engine_review.jpg',quality=95)
readme='''# Navy commuter bicycle - approved export

Source shape and baked engine view approved on 2026-10-20; runtime installed in
RunnerGame/Assets/Models/Fahrzeug/BikeCommuter with verified export hashes.

Three OBJ meshes share one opaque 2048 x 2048 PNG atlas:
- VEH_BikeCommuter_body.obj: 7,680 triangles.
- VEH_BikeCommuter_wheel_front.obj: 4,020 triangles.
- VEH_BikeCommuter_wheel_rear.obj: 4,020 triangles.
Total: 15,720 triangles, within the 25,000 target.

Load all three once using VEH_BikeCommuter_parts.json. Pivots are stored in
Blender coordinates and map to engine (x,z,-y). Body origin is on ground at
the midpoint of the axles. Each wheel's mesh is local to its own axle, ready
for rotation about local X. This package does not implement gameplay motion.
Front faces Blender -Y / engine +Z. Metres, Y-up OBJ, normals/UVs included.
Axle spacing 1.08 m; tyre diameter 0.68 m. The centre stand is deployed.

The design is based on local public-domain Batavus photo references, with
inferred cross-bike dimensions and simplified minor details. It is not a
measured factory replica. No reference-photo pixels are baked into textures.
New local geometry; no Bushido/PyBullet imported geometry included. Reference
credits and URLs are in refs.json (author Phillip, public domain as recorded).

Source: bike_commuter.blend, build.py, spec.json, measure_reference.py.
Rebuild uses existing repo photo_lib/asset_lib and Blender 5.2. Export:
blender --background --factory-startup --python-exit-code 1 --python build.py -- --export
Run check_export.py with system Python/Pillow to verify actual OBJ/PNG data.

Engine screenshots may show dotted subpixel spokes from the viewer's lack of
anti-aliasing. Geometry checks confirm solid wire meshes rather than alpha.
Runtime installed after engine-view approval. No engine code changed.
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
runtime=[OUT/name for name in validation['hashes']]+[OUT/'validation.json',OUT/'README.md',HERE/'refs.json',PREV/'engine_review.jpg']
source=[HERE/name for name in ('bike_commuter.blend','build.py','spec.json','refs.json','measure_reference.py','measurement_notes.json','blender_test_bike.py','check_export.py','package_export.py','README.md')]
source += [HERE/'ref/03.jpg',HERE/'ref/04.jpg',PREV/'build_contact_sheet.jpg',PREV/'geometry_validation.json']
for name,paths in (('bike_commuter_game_pack.zip',runtime),('bike_commuter_editable_source.zip',source)):
    target=HERE/name
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
        for p in paths: archive.write(p,p.name if name.endswith('game_pack.zip') else str(p.relative_to(HERE)))
    with zipfile.ZipFile(target) as archive: assert archive.testzip() is None
    print('PACKAGED',name,target.stat().st_size)
