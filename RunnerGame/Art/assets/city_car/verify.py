"""Independent checker for exported OBJ coordinates, normals, UVs and axle contract."""
import json,math,hashlib
from pathlib import Path
from PIL import Image
A=Path(__file__).resolve().parent
m=json.loads((A/'out/VEH_CityCar_parts.json').read_text());report={'parts':{},'triangles':0}
assert len(m['parts'])==5
for p in m['parts']:
 path=A/'out'/p['obj'];vs=[];uv=[];ns=[];fs=[]
 for line in path.read_text().splitlines():
  t=line.split()
  if not t:continue
  if t[0]=='v':vs.append(tuple(map(float,t[1:4])))
  if t[0]=='vt':uv.append(tuple(map(float,t[1:3])))
  if t[0]=='vn':ns.append(tuple(map(float,t[1:4])))
  if t[0]=='f':fs.append([tuple(map(int,x.split('/'))) for x in t[1:]])
 assert all(math.isfinite(x) for seq in (vs,uv,ns) for v in seq for x in v)
 assert all(-.001<=x<=1.001 for v in uv for x in v)
 for n in ns:assert .98<sum(x*x for x in n)<1.02
 for f in fs:
  assert len(f)==3
  assert all(1<=v<=len(vs) and 1<=u<=len(uv) and 1<=n<=len(ns) for v,u,n in f)
  a,b,c=[vs[i[0]-1] for i in f];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
  cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];assert sum(x*x for x in cross)>1e-20
 # OBJ coordinates x,z,-y; vertices relative to axle.
 bounds=[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)]
 if p['name']!='body':
  assert abs(bounds[1][0]+p['pivot'][2])<.001
  assert abs(sum(bounds[2]))<.003
 report['parts'][p['name']]={'triangles':len(fs),'local_obj_bounds':bounds,'pivot':p['pivot'],'sha256':hashlib.sha256(path.read_bytes()).hexdigest()};report['triangles']+=len(fs)
assert report['triangles']<=18000
im=Image.open(A/'out'/m['texture']);assert im.size==(2048,2048)
if im.mode=='RGBA':assert im.getchannel('A').getextrema()==(255,255)
report['texture']={'size':im.size,'mode':im.mode,'sha256':hashlib.sha256((A/'out'/m['texture']).read_bytes()).hexdigest()}
(A/'export-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
