"""Package verified engine assets and portable, packed Blender review sources."""
from pathlib import Path
import json, hashlib, zipfile
HERE=Path(__file__).resolve().parent; OUT=HERE/'out'; PREFIX='CHR_OrdnungsamtV2'
checks=json.loads((OUT/'export_checks.json').read_text())
assert checks['matching_topology_uv'] and checks['source_hashes_unchanged']
readme='''# Approved officer v2 - final export

Approved appearance and 40-frame running motion, with corrected hand orientation.

## Game assets

- CHR_OrdnungsamtV2_run_01.obj through _40.obj: 73,710 triangles per pose.
- CHR_OrdnungsamtV2.png: one shared opaque 2048 x 2048 atlas.
- CHR_OrdnungsamtV2_animation.json: loop order, 20 ms per frame, 800 ms total.
- *_parts.json: individual poses for the existing asset viewer.
- Metres, Y-up, character faces engine +Z (Blender -Y), common ground origin.
- All poses have matching vertex/face/UV layout. Normals vary with pose.

Display one pose at a time. The manifest describes playback; the current game does
not implement skeletal animation or automatically consume this manifest. These
files were approved in the engine viewer and installed over v1 on 2026-10-20.
The installed runtime retains the CHR_Ordnungsamt prefix (without V2); the package
uses CHR_OrdnungsamtV2 to distinguish it. The previous runtime has a verified backup
under checkpoints/runtime_v1_before_v2_install in the source asset folder.
This detailed version is substantially heavier than v1 (11,542 triangles/pose).

## Editable source

The separate source ZIP contains packed-texture neutral and animated Blender
files. Use officer_v2_run_preview.blend for the approved editable motion.
The run plays frames 1-40 at 50 fps; frame 41 duplicates frame 1 for the seam.
Export simplification and opaque hair trimming are confined to export.py memory.
Rebuilding from the original human generator additionally needs the local MPFB
research/bootstrap and official system asset pack described in the source README.

## Provenance

MakeHuman base, skin and official system wardrobe assets are CC0. MPFB software
has a separate licence. Hannover sleeve artwork is recorded as public domain
(PD-Coa-Germany). See provenance.json for detailed records and sources.
The face is fictional; the navy uniform and external vest combine Hannover and
Dortmund-inspired details. No reference-photo pixels are used in textures.

Runtime assets were installed after engine-view approval. No engine code changed.
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
runtime=[OUT/f'{PREFIX}.png',OUT/f'{PREFIX}_animation.json',OUT/'README.md',OUT/'validation.json',OUT/'export_checks.json']
runtime += [OUT/f'{PREFIX}_run_{i:02d}{suffix}' for i in range(1,41) for suffix in ('.obj','_parts.json')]
runtime += [HERE/'source/provenance.json']
runtime += [HERE/'previews/engine_run.gif',HERE/'previews/engine_review.png']
runtime += [HERE/'previews/runtime_installation.json']
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in runtime}
(OUT/'sha256.json').write_text(json.dumps(hashes,indent=2))
runtime.append(OUT/'sha256.json')
target=HERE/'ordnungsamt_v2_game_pack.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in runtime: z.write(p,p.name)
source_files=[HERE/'officer_v2.blend',HERE/'officer_v2_run_preview.blend',HERE/'README.md']
source_files+=list(HERE.glob('*.py'))+list((HERE/'source').glob('*'))
source_files += [HERE/'previews/officer_v2_run_natural_hands.gif',OUT/'README.md']
source_target=HERE/'ordnungsamt_v2_editable_source.zip'
with zipfile.ZipFile(source_target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in source_files:
        if p.is_file(): z.write(p,str(p.relative_to(HERE)))
for path in (target,source_target):
    with zipfile.ZipFile(path) as z: assert z.testzip() is None
print(json.dumps({'game_pack':str(target),'game_pack_bytes':target.stat().st_size,'source_pack':str(source_target),'source_pack_bytes':source_target.stat().st_size}))
