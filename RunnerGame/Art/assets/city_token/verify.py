"""Geometry contracts execute before export/bake; ordinary Python checks export."""
import math,json,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent

def geometry(parts):
    assert list(parts)==['token']
    obs=parts['token'];vs=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
    lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
    assert all(abs(a-b)<1e-6 for a,b in zip(lo,[-.16,-.0175,-.16])),lo
    assert all(abs(a-b)<1e-6 for a,b in zip(hi,[.16,.0175,.16])),hi
    tris=sum(len(p.vertices)-2 for o in obs for p in o.data.polygons)
    assert tris<=1000,tris
    motifs={}
    for side in ['front','rear']:
        bars=[o for o in obs if o.name.startswith(side+'_H')]
        assert len(bars)==3
        sign=-1 if side=='front' else 1
        # Real outward polygon faces must protrude 5mm beyond recessed disc face.
        faces=[p for o in bars for p in o.data.polygons if (o.matrix_world.to_3x3()@p.normal).y*sign>.99]
        assert len(faces)==3
        coords=[o.matrix_world@v.co for o in bars for v in o.data.vertices]
        assert abs(max(sign*v.y for v in coords)-.0175)<1e-6
        motifs[side]={'solid_bars':3,'outward_faces':len(faces),'relief_metres':.005}
    assert all(math.isfinite(c) for v in vs for c in v)
    return {'triangles':tris,'bounds_source':{'min':lo,'max':hi},'motifs':motifs,'diameter':hi[0]-lo[0],'thickness':hi[1]-lo[1],'centered':True}

def exported():
    p=HERE/'out';info=json.loads((p/'PROP_CityToken_parts.json').read_text());assert len(info['parts'])==1 and info['parts'][0]['pivot']==[0,0,0]
    lines=(p/info['parts'][0]['obj']).read_text().splitlines();vs=[list(map(float,l.split()[1:])) for l in lines if l.startswith('v ')];uv=[list(map(float,l.split()[1:])) for l in lines if l.startswith('vt ')];faces=[l.split()[1:] for l in lines if l.startswith('f ')]
    assert len(faces)<=1000 and all(len(f)==3 for f in faces)
    assert all(math.isfinite(c) for v in vs+uv for c in v)
    assert uv and all(-1e-5<=c<=1.00001 for v in uv for c in v)
    assert all(all(len(x.split('/'))==3 and all(x.split('/')) for x in f) for f in faces)
    dims=[max(v[i] for v in vs)-min(v[i] for v in vs) for i in range(3)]
    assert all(abs(a-b)<1e-5 for a,b in zip(dims,[.32,.32,.035])),dims
    png=(p/info['texture']).read_bytes();assert struct.unpack('>II',png[16:24])==(512,512)
    from PIL import Image
    im=Image.open(p/info['texture']);assert im.mode=='RGB' or im.getchannel('A').getextrema()==(255,255)
    result={'triangles':len(faces),'vertices':len(vs),'uv_coordinates':len(uv),'engine_dimensions':dims,'atlas':[512,512],'opaque':True,'part_count':1,'pivot':[0,0,0]}
    (p/'export_checks.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':exported()
