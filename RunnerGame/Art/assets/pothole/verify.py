import json,math
from pathlib import Path
H=Path(__file__).resolve().parent
S=json.loads((H/'spec.json').read_text())
def check(vs,faces):
 lo=[min(v[j] for v in vs) for j in range(3)];hi=[max(v[j] for v in vs) for j in range(3)]
 assert 1.05<hi[0]-lo[0]<1.25 and .75<hi[1]-lo[1]<.9,(lo,hi)
 assert .002<=lo[2]<=.003 and .01<hi[2]<.02,(lo,hi)
 assert len(faces)<=S['budget']
 for f in faces:
  assert len(f)==3;a,b,c=[vs[i] for i in f];u=[b[j]-a[j] for j in range(3)];v=[c[j]-a[j] for j in range(3)];cross=[u[(j+1)%3]*v[(j+2)%3]-u[(j+2)%3]*v[(j+1)%3] for j in range(3)]
  assert sum(t*t for t in cross)>1e-18
  assert cross[2]>0,'visible surface must face upwards'
 return {'bounds_source':{'min':lo,'max':hi},'triangles':len(faces),'all_surface_above_opaque_road':True,'upward_nondegenerate_faces':True,'origin':[0,0,0]}
def geometry(obs):
 vs=[];fs=[]
 for o in obs:
  start=len(vs);vs.extend([tuple(o.matrix_world@v.co) for v in o.data.vertices]);fs.extend([tuple(start+i for i in p.vertices) for p in o.data.polygons])
 return check(vs,fs)
def exported():
 from PIL import Image
 im=Image.open(H/'out/PROP_Pothole.png');assert im.size==(512,512) and im.convert('RGBA').getextrema()[3]==(255,255)
 vs=[];uv=[];ns=[];fs=[]
 for line in (H/'out/PROP_Pothole_patch.obj').read_text().splitlines():
  t=line.split()
  if not t:continue
  if t[0]=='v':vs.append((float(t[1]),-float(t[3]),float(t[2])))
  elif t[0]=='vt':uv.append(list(map(float,t[1:3])))
  elif t[0]=='vn':ns.append(list(map(float,t[1:4])))
  elif t[0]=='f':
   ids=[list(map(int,i.split('/'))) for i in t[1:]];assert all(len(i)==3 and 0<i[0]<=len(vs) and 0<i[1]<=len(uv) and 0<i[2]<=len(ns) for i in ids);fs.append(tuple(i[0]-1 for i in ids))
 assert all(math.isfinite(c) and -1e-6<=c<=1.000001 for v in uv for c in v)
 assert all(abs(sum(c*c for c in v)-1)<.01 for v in ns)
 report=check(vs,fs);report.update(opaque_512_atlas=True,valid_uv_normals_indices=True)
 (H/'out/export_checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
if __name__=='__main__':exported()
