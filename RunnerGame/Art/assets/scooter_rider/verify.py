"""Independent exported OBJ/atlas/manifest and measured contact contract checks."""
from pathlib import Path
import json, math, hashlib
from PIL import Image
HERE=Path(__file__).resolve().parent; OUT=HERE/'out'; PREFIX='CHR_ScooterRider'
def read_obj(path):
    v=[]; uv=[]; normal=[]; faces=[]
    for line in path.read_text().splitlines():
        bits=line.split()
        if not bits: continue
        if bits[0]=='v': v.append(tuple(map(float,bits[1:4])))
        elif bits[0]=='vt': uv.append(tuple(map(float,bits[1:3])))
        elif bits[0]=='vn': normal.append(tuple(map(float,bits[1:4])))
        elif bits[0]=='f': faces.append([tuple(int(j) if j else 0 for j in s.split('/')) for s in bits[1:]])
    assert all(math.isfinite(x) for data in (v,uv,normal) for row in data for x in row)
    assert 0<len(faces)<=35000 and all(len(f)==3 for f in faces)
    assert all(1<=a[0]<=len(v) and len(a)>=2 and 1<=a[1]<=len(uv) and (len(a)<3 or 1<=a[2]<=len(normal)) for f in faces for a in f)
    assert all(-1e-5<=x<=1.00001 for t in uv for x in t)
    # Every triangle has nonzero area in exported engine coordinates.
    for face in faces:
        a,b,c=[v[x[0]-1] for x in face]; ab=[b[i]-a[i] for i in range(3)]; ac=[c[i]-a[i] for i in range(3)]
        cross=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]]
        assert sum(x*x for x in cross)>1e-20
    return v,uv,faces
def main():
    data={n:read_obj(OUT/f'{PREFIX}_{n}.obj') for n in ('ride','duck')}
    a,b=data.values(); assert len(a[0])==len(b[0]); assert a[1]==b[1]
    assert [[(i[0],i[1]) for i in f] for f in a[2]]==[[(i[0],i[1]) for i in f] for f in b[2]]
    assert a[0]!=b[0]
    image=Image.open(OUT/f'{PREFIX}.png'); assert image.size==(2048,2048)
    if image.mode=='RGBA': assert image.getchannel('A').getextrema()==(255,255)
    descriptor=json.loads((OUT/f'{PREFIX}_poses.json').read_text()); assert descriptor['display']=='mutually_exclusive'
    for name,manifestname in descriptor['poses'].items():
        m=json.loads((OUT/manifestname).read_text()); assert (OUT/m['texture']).is_file(); assert len(m['parts'])==1
        assert m['parts'][0]['pivot']==[0,0,0]; assert (OUT/m['parts'][0]['obj']).is_file()
    contacts=json.loads((HERE/'previews/contact_measurements.json').read_text())
    for pose in contacts.values():
        for foot in pose['feet_native_bounds'].values():
            assert foot['sole_supported_fraction']>=.99; assert abs(foot['lowest_sole_z']-.184)<.001
    drop=contacts['ride']['head_top']-contacts['duck']['head_top']; assert drop>=.30
    result={'status':'PASS','triangles_per_pose':len(a[2]),'resident_triangles_both':len(a[2])*2,'vertices_per_pose':len(a[0]),'same_topology':True,'same_uvs':True,'opaque_atlas':True,'head_drop_m':drop,'export_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('CHR*') if p.suffix in ('.png','.obj','.json')}}
    (OUT/'validation.json').write_text(json.dumps(result,indent=2)); print(json.dumps(result,indent=2))
if __name__=='__main__': main()
