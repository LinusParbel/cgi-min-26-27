"""Independent actual OBJ/PNG validation; normal Python, no Blender dependencies."""
from pathlib import Path
import json,math,hashlib,sys
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent; O=P/'out'; v=[];uv=[];n=[];faces=[]
for line in (O/'ENV_StreetTree.obj').read_text().splitlines():
    a=line.split()
    if not a:continue
    if a[0]=='v':v.append(list(map(float,a[1:4])))
    if a[0]=='vt':uv.append(list(map(float,a[1:3])))
    if a[0]=='vn':n.append(list(map(float,a[1:4])))
    if a[0]=='f':faces.append([tuple(int(x)-1 for x in q.split('/')) for q in a[1:]])
V=np.array(v);U=np.array(uv);N=np.array(n)
if '--negative-fixture' in sys.argv:
    # Strip reverse faces by geometric triangle identity, reproducing the initial export bug.
    seen=set(); fixture=[]
    for f in faces:
        key=tuple(sorted(tuple(V[q[0]]) for q in f))
        if key not in seen: fixture.append(f); seen.add(key)
    faces=fixture
assert all(np.isfinite(a).all() for a in [V,U,N]);assert (U>=-1e-6).all() and (U<=1.000001).all()
assert np.max(np.abs(np.linalg.norm(N,axis=1)-1))<1e-4
assert len(faces)<=12000 and all(len(f)==3 for f in faces)
pairs={}; opposed=0
for f in faces:
    assert all(len(q)==3 and q[0]<len(V) and q[1]<len(U) and q[2]<len(N) for q in f)
    p=V[[q[0] for q in f]]; c=np.cross(p[1]-p[0],p[2]-p[0]); area=np.linalg.norm(c)
    assert area>1e-9
    normal=c/area
    assert all(np.dot(normal,N[q[2]])>.99 for q in f)
    key=tuple(sorted(tuple(x) for x in p))
    if key in pairs:
        assert np.dot(normal,pairs[key])<-.999;opposed+=1
    else:pairs[key]=normal
print('actual opposed leaf triangle pairs:',opposed)
assert opposed==4000
lo=V.min(0);hi=V.max(0)
assert abs(lo[1])<1e-6 and abs(hi[1]-6.5)<1e-5
assert np.allclose(hi-lo,[3.5,6.5,3.5],atol=1e-5)
# Source trunk grounded at origin maps to engine Y-up; ground ring is centred there.
ground=V[np.abs(V[:,1])<1e-6];assert len(ground)>=10 and np.linalg.norm(ground.mean(0))<1e-5
img=Image.open(O/'ENV_StreetTree.png'); assert img.size==(1024,1024)
rgba=np.asarray(img.convert('RGBA'));assert rgba[:,:,3].min()==255
assert len(np.unique(rgba[:,:,:3].reshape(-1,3),axis=0))>100
r={'triangles':len(faces),'opposed_leaf_triangle_pairs':opposed,'bounds_engine':[lo.tolist(),hi.tolist()],'ground_vertices':len(ground),'texture':{'size':list(img.size),'opaque':True},'finite_positions_normals_uv':True,'unit_normals':True,'nonzero_triangles':True,'obj_sha256':hashlib.sha256((O/'ENV_StreetTree.obj').read_bytes()).hexdigest()}
(O/'export_checks.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
