import json,math
from pathlib import Path
HERE=Path(__file__).resolve().parent
def bounds(v):return [[min(p[j] for p in v) for j in range(3)],[max(p[j] for p in v) for j in range(3)]]
def contract(v,faces):
 lo,hi=bounds(v);assert abs(lo[2])<1e-5
 assert abs(lo[0]+hi[0])<1e-5 and abs(lo[1]+hi[1])<1e-5
 assert hi[0]-lo[0]<=2.45 and abs(hi[2]-1.695)<1e-5
 # Triangle bounding boxes must not enter the 1.9m wide clear central prism below board.
 for f in faces:
  a,b=bounds([v[i] for i in f])
  assert not (a[0]<.95-1e-6 and b[0]>-.95+1e-6 and a[2]<1.43-1e-6),('opening blocked',a,b)
 central=[p[2] for f in faces if min(v[i][0] for i in f)<.5 and max(v[i][0] for i in f)>-.5 for p in [v[i] for i in f]]
 assert abs(min(central)-1.43)<1e-5 and abs(max(central)-1.68)<1e-5
 assert 1.316786<1.43<1.674661
 return {'bounds':[lo,hi],'duck_clearance_m':1.43-1.316786,'ride_overlap_m':1.674661-1.43,'opening_width_m':1.9}
def geometry(objs):
 import bpy
 dg=bpy.context.evaluated_depsgraph_get();v=[];faces=[]
 for o in objs:
  e=o.evaluated_get(dg);off=len(v);v.extend([tuple(e.matrix_world@q.co) for q in e.data.vertices]);faces.extend([tuple(off+i for i in f.vertices) for f in e.data.polygons])
 r=contract(v,faces);r['triangles']=sum(len(f)-2 for f in faces);assert r['triangles']<=5000
 rejected=[]
 for name,vs,fs in [('raised_ground',[(x,y,z+.1) for x,y,z in v],faces),('blocked_opening',v+[(-.2,0,.2),(.2,0,.2),(0,0,1)],faces+[(len(v),len(v)+1,len(v)+2)]),('wide_base',v+[(-1.3,0,0)],faces)]:
  try:contract(vs,fs)
  except AssertionError:rejected.append(name)
  else:raise AssertionError(name)
 r['negative_fixtures_rejected']=rejected;return r
def exported():
 from PIL import Image
 im=Image.open(HERE/'out/PROP_DuckBarrier.png');assert im.size==(512,512) and im.convert('RGBA').getextrema()[3]==(255,255)
 v=[];uv=[];ns=[];fs=[]
 for line in (HERE/'out/PROP_DuckBarrier_barrier.obj').read_text().splitlines():
  t=line.split()
  if not t:continue
  if t[0]=='v':v.append([float(t[1]),-float(t[3]),float(t[2])])
  elif t[0]=='vt':uv.append(list(map(float,t[1:3])))
  elif t[0]=='vn':ns.append(list(map(float,t[1:4])))
  elif t[0]=='f':
   ix=[list(map(int,s.split('/'))) for s in t[1:]];assert len(ix)==3 and all(len(i)==3 and 0<i[0]<=len(v) and 0<i[1]<=len(uv) and 0<i[2]<=len(ns) for i in ix);fs.append([i[0]-1 for i in ix])
 assert all(math.isfinite(c) for vs in [v,uv,ns] for q in vs for c in q)
 assert all(-1e-6<=c<=1.000001 for q in uv for c in q)
 assert all(abs(sum(c*c for c in q)-1)<.01 for q in ns)
 for f in fs:
  a,b,c=[v[i] for i in f];u=[b[j]-a[j] for j in range(3)];w=[c[j]-a[j] for j in range(3)];assert sum((u[(j+1)%3]*w[(j+2)%3]-u[(j+2)%3]*w[(j+1)%3])**2 for j in range(3))>1e-16
 r=contract(v,fs);assert len(fs)<=5000;r.update(triangles=len(fs),opaque_atlas=True,valid_indices_uv_normals_nondegenerate=True)
 (HERE/'out/export_checks.json').write_text(json.dumps(r,indent=2));print(r)
if __name__=='__main__':exported()
