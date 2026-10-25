import json,math,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent
NAMES={'shop_ground','sandstone_upper','brick_upper'}
def bounds(vs):
 lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
 assert all(math.isfinite(c) for v in vs for c in v)
 assert all(abs(a-b)<1e-5 for a,b in zip(lo+hi,[-3,-.4,0,3,.4,3.2])),(lo,hi)
 return [lo,hi]
def geometry(parts):
 import bmesh
 assert set(parts)==NAMES
 result={};total=0
 for key,objs in parts.items():
  vs=[o.matrix_world@v.co for o in objs for v in o.data.vertices]
  tris=sum(len(p.vertices)-2 for o in objs for p in o.data.polygons);total+=tris
  for o in objs:
   bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges),o.name;bm.free()
   for m in o.data.materials:
    bs=m.node_tree.nodes.get('Principled BSDF');assert bs.inputs['Alpha'].default_value==1;assert bs.inputs['Transmission Weight'].default_value==0
  panes=[o for o in objs if '_glass_' in o.name];assert panes
  for o in panes:
   assert o.location.y>-.22,('glass must recess behind front wall',o.name)
  assert any('_back' in o.name for o in objs)
  # Front-facing surfaces at the advertised negative-Y side, back and both side closures.
  polys=[(o.matrix_world@p.center,p.normal) for o in objs for p in o.data.polygons]
  assert any(c.y<-.2 and n.y<-.99 for c,n in polys)
  assert any(abs(c.y-.4)<1e-5 and n.y>.99 for c,n in polys)
  for sign in [-1,1]:assert any(abs(c.x-sign*3)<1e-5 and n.x*sign>.99 for c,n in polys)
  result[key]={'bounds':bounds(vs),'triangles':tris,'closed_solids':True,'recessed_glass':True,'opaque_materials':True}
 assert total<=6000
 return {'parts':result,'total_triangles':total}
def side_overlap(vs,triangles):
 # Convex clipping in Y/Z checks actual exported triangles on each extreme X plane.
 def area(poly):return sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2 if len(poly)>2 else 0
 def cross(a,b,p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
 def overlap(a,b):
  if area(b)<0:b=b[::-1]
  poly=a
  for j in range(3):
   edge0,edge1=b[j],b[(j+1)%3];new=[]
   if not poly:break
   for i,p in enumerate(poly):
    q=poly[(i+1)%len(poly)];cp=cross(edge0,edge1,p);cq=cross(edge0,edge1,q)
    if cp>=-1e-10:new.append(p)
    if (cp>0 and cq<0) or (cp<0 and cq>0):
     t=cp/(cp-cq);new.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
   poly=new
  return abs(area(poly))
 for sign in [-1,1]:
  patches=[]
  for f in triangles:
   pts=[vs[i] for i in f]
   if all(abs(v[0]-3*sign)<2e-6 for v in pts):patches.append([(v[1],v[2]) for v in pts])
  for i,a in enumerate(patches):
   for b in patches[i+1:]:assert overlap(a,b)<1e-8,('positive-area side face overlap',sign,overlap(a,b))
 return True

def exported():
 info=json.loads((HERE/'out/AR_Shopfront_parts.json').read_text());assert {p['name'] for p in info['parts']}==NAMES
 png=(HERE/'out'/info['texture']).read_bytes();assert struct.unpack('>II',png[16:24])==(2048,2048)
 result={};total=0
 for p in info['parts']:
  assert p['pivot']==[0,0,0]
  vs=[];uv=[];ns=[];fs=[]
  for line in (HERE/'out'/p['obj']).read_text().splitlines():
   t=line.split()
   if not t:continue
   if t[0]=='v':vs.append([float(t[1]),-float(t[3]),float(t[2])])
   elif t[0]=='vt':uv.append(list(map(float,t[1:3])))
   elif t[0]=='vn':ns.append(list(map(float,t[1:4])))
   elif t[0]=='f':fs.append(t[1:])
  for f in fs:
   assert len(f)==3
   ids=[list(map(int,a.split('/'))) for a in f]
   assert all(len(a)==3 and 0<a[0]<=len(vs) and 0<a[1]<=len(uv) and 0<a[2]<=len(ns) for a in ids)
   a,b,c=[vs[i[0]-1] for i in ids];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
   assert sum((u[(i+1)%3]*v[(i+2)%3]-u[(i+2)%3]*v[(i+1)%3])**2 for i in range(3))>1e-16
  assert all(math.isfinite(c) for v in uv+ns for c in v)
  assert all(-1e-6<=c<=1.000001 for v in uv for c in v)
  assert all(abs(sum(c*c for c in n)-1)<.01 for n in ns)
  side_overlap(vs,[[int(a.split('/')[0])-1 for a in f] for f in fs])
  result[p['name']]={'bounds':bounds(vs),'triangles':len(fs),'no_side_face_overlap':True};total+=len(fs)
 assert total<=6000
 report={'total_triangles':total,'parts':result,'atlas':[2048,2048],'valid_indices_uv_normals':True}
 (HERE/'out/export_checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
if __name__=='__main__':exported()
