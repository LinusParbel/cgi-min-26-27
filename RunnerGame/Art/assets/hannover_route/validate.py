from pathlib import Path
import json,math,hashlib
import numpy as np
from PIL import Image
A=Path(__file__).resolve().parent;V=[];N=[];UV=[];faces=[]
for line in (A/'out/HannoverRoute.obj').read_text().splitlines():
 p=line.split()
 if not p:continue
 if p[0]=='v':V.append(list(map(float,p[1:])))
 elif p[0]=='vn':N.append(list(map(float,p[1:])))
 elif p[0]=='vt':UV.append(list(map(float,p[1:])))
 elif p[0]=='f':faces.append([list(map(int,x.split('/'))) for x in p[1:]])
V=np.array(V);N=np.array(N);UV=np.array(UV)
assert np.isfinite(V).all() and np.isfinite(N).all() and np.isfinite(UV).all()
assert np.max(np.abs(np.linalg.norm(N,axis=1)-1))<1e-8
for f in faces:
 assert len(f)==3
 for v,t,n in f:assert 1<=v<=len(V) and 1<=t<=len(UV) and 1<=n<=len(N)
 p=V[np.array([x[0] for x in f])-1];cross=np.cross(p[1]-p[0],p[2]-p[0]);assert np.linalg.norm(cross)>1e-10
 assert np.dot(cross,N[f[0][2]-1])>0
im=Image.open(A/'out/HannoverRoute.png');assert im.size==(512,512) and im.getextrema()[3]==(255,255)
r=json.loads((A/'verification.json').read_text());r['readback']={'vertices':len(V),'unit_normals':len(N),'uvs':len(UV),'triangles':len(faces),'normals_match_winding':True,'all_indices_valid':True,'all_geometry_finite':True,'texture_alpha_opaque':True,'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((A/'out').glob('*'))}}
(A/'verification.json').write_text(json.dumps(r,indent=2));print(json.dumps(r['readback'],indent=2))
