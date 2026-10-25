"""Check actual OBJ pose data, opaque atlas, timing and unchanged sources."""
from pathlib import Path
import json, hashlib, math
from PIL import Image
HERE=Path(__file__).resolve().parent; OUT=HERE/'out'; PREFIX='CHR_OrdnungsamtV2'
manifest=json.loads((OUT/(PREFIX+'_animation.json')).read_text())
validation=json.loads((OUT/'validation.json').read_text())
assert len(manifest['frames'])==40 and sum(f['duration_ms'] for f in manifest['frames'])==800
baseline=None; report=[]
for frame in manifest['frames']:
    vs=[]; uvs=[]; ns=[]; faces=[]
    for line in (OUT/frame['obj']).read_text().splitlines():
        f=line.split()
        if not f: continue
        if f[0]=='v': vs.append(tuple(map(float,f[1:4])))
        elif f[0]=='vt': uvs.append(tuple(map(float,f[1:3])))
        elif f[0]=='vn': ns.append(tuple(map(float,f[1:4])))
        elif f[0]=='f': faces.append([tuple(map(int,v.split('/'))) for v in f[1:]])
    topology=[[(v[0],v[1]) for v in face] for face in faces]
    if baseline is None: baseline=(topology,uvs,len(vs))
    assert (topology,uvs,len(vs))==baseline,frame['obj']
    assert all(len(f)==3 for f in faces) and len(faces)<80000
    assert all(math.isfinite(c) for v in vs+uvs+ns for c in v)
    assert all(1<=v[0]<=len(vs) and 1<=v[1]<=len(uvs) and 1<=v[2]<=len(ns) for f in faces for v in f)
    floor=min(v[1] for v in vs)
    assert floor>-.001 and floor<.35,(frame['obj'],floor)
    report.append({'obj':frame['obj'],'triangles':len(faces),'vertices':len(vs),'min_y':floor})
with Image.open(OUT/manifest['texture']) as im:
    assert im.size==(2048,2048)
    assert im.convert('RGBA').getchannel('A').getextrema()==(255,255)
for name,digest in validation['source_sha256'].items(): assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest
(OUT/'export_checks.json').write_text(json.dumps({'matching_topology_uv':True,'valid_normals':True,'opaque_2048_atlas':True,'duration_ms':800,'source_hashes_unchanged':True,'poses':report},indent=2))
print('EXPORT_VERIFIED',len(report),'frames;',len(faces),'triangles; shared UV/topology; opaque 2048 atlas; sources unchanged')
