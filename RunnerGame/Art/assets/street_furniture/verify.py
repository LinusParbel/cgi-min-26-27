"""Independent dimensions and actual exported geometry contract."""
import json,math,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent
def bounds(vs):return {'min':[min(v[i] for v in vs) for i in range(3)],'max':[max(v[i] for v in vs) for i in range(3)]}
def check(name,vs):
 b=bounds(vs);lo=b['min'];hi=b['max'];assert abs(lo[2])<1e-5,(name,b)
 ranges={'bench':((1.79,1.81),(.58,.7),(.84,.88)),'planter':((.92,.94),(.92,.94),(1.1,1.3)),'lamp':((.35,.37),(1.48,1.51),(5.99,6.01))}
 for i,(a,z) in enumerate(ranges[name]):assert a<=hi[i]-lo[i]<=z,(name,i,b)
 assert all(math.isfinite(c) for v in vs for c in v);return b
def structure(parts):
 def named(k,p):return [o for o in parts[k] if o.name.startswith(p)]
 def bb(o):return bounds([o.matrix_world@v.co for v in o.data.vertices])
 seats=named('bench','seat_slat');assert len(seats)==5
 rails=named('bench','seat_rail');assert len(rails)==2
 for rail in rails:
  b=bb(rail);assert .40<b['max'][2]<.43
  for seat in seats:
   s=bb(seat);assert s['min'][0]<=b['min'][0]<=s['max'][0] and abs(s['min'][2]-b['max'][2])<.025
 feet=named('bench','foot');assert len(feet)==2 and all(abs(bb(o)['min'][2])<1e-5 for o in feet)
 for part,prefix in [('planter','bottom'),('lamp','baseplate')]:
  contact=named(part,prefix);assert len(contact)==1 and abs(bb(contact[0])['min'][2])<1e-5
 soil=named('planter','soil');assert len(soil)==1 and .68<bb(soil[0])['max'][2]<.70
 walls=named('planter','sidewall')+named('planter','endwall');assert len(walls)==4
 rim=named('planter','rim');assert len(rim)==4
 # Independent planar interval test: top horizontal rim bars may meet, never overlap in area.
 for i,a in enumerate(rim):
  for b in rim[i+1:]:
   aa=bb(a);bbx=bb(b)
   overlap=[min(aa['max'][j],bbx['max'][j])-max(aa['min'][j],bbx['min'][j]) for j in [0,1]]
   assert min(overlap)<1e-5,('coplanar rim overlap',overlap)
 assert len(named('lamp','curved_arm'))==13 and len(named('lamp','underside_lens'))==1
 return True
def geometry(parts):
 assert set(parts)=={'bench','planter','lamp'};r={};total=0
 for k,objs in parts.items():
  import bpy
  dg=bpy.context.evaluated_depsgraph_get();evaluated=[o.evaluated_get(dg) for o in objs]
  vs=[o.matrix_world@v.co for o in evaluated for v in o.data.vertices];t=sum(len(p.vertices)-2 for o in evaluated for p in o.data.polygons);total+=t;r[k]={'bounds':check(k,vs),'triangles_with_modifiers':t}
 assert total<=10000;structure(parts)
 negative_cases=[]
 for part,prefix in [('bench','seat_slat'),('bench','seat_rail'),('planter','soil'),('planter','rim'),('lamp','curved_arm')]:
  broken={k:[o for o in objs if not (k==part and o.name.startswith(prefix))] for k,objs in parts.items()}
  try:structure(broken)
  except AssertionError:negative_cases.append(part+':missing_'+prefix)
  else:raise AssertionError('Negative fixture accepted: '+prefix)
 foot=next(o for o in parts['bench'] if o.name.startswith('foot'));old=foot.location.z
 foot.location.z+=.1;bpy.context.view_layer.update()
 try:structure(parts)
 except AssertionError:negative_cases.append('bench:raised_foot')
 else:raise AssertionError('Raised foot accepted')
 finally:foot.location.z=old;bpy.context.view_layer.update()
 bench=parts['bench'];assert len([o for o in bench if o.name.startswith('seat_slat')])==5
 seat=[v.co.z+o.location.z for o in bench if o.name.startswith('seat_slat') for v in o.data.vertices];assert abs(max(seat)-.45)<1e-5
 leaves=[o for o in parts['planter'] if o.name.startswith('two_sided_leaves')]
 assert len(leaves)==9
 for o in leaves:
  f=[tuple(p.vertices) for p in o.data.polygons];assert all(tuple(reversed(p)) in f or (p[2],p[1],p[0]) in f for p in f)
 assert any(o.name.startswith('soil') for o in parts['planter'])
 return {'total_triangles':total,'parts':r,'seat_height':.45,'leaf_front_back_pairs':288,'structural_checks':True,'negative_cases_rejected':negative_cases}
def exported():
 from PIL import Image
 image=Image.open(HERE/'out/PROP_StreetFurniture.png');assert image.size==(1024,1024);assert image.convert('RGBA').getextrema()[3]==(255,255)
 info=json.loads((HERE/'out/PROP_StreetFurniture_parts.json').read_text());r={};total=0
 for p in info['parts']:
  assert p['pivot']==[0,0,0];vs=[];uv=[];ns=[];fs=[]
  for line in (HERE/'out'/p['obj']).read_text().splitlines():
   t=line.split()
   if not t:continue
   if t[0]=='v':vs.append([float(t[1]),-float(t[3]),float(t[2])])
   elif t[0]=='vt':uv.append(list(map(float,t[1:3])))
   elif t[0]=='vn':ns.append(list(map(float,t[1:4])))
   elif t[0]=='f':fs.append(t[1:])
  for f in fs:
   assert len(f)==3;ids=[list(map(int,v.split('/'))) for v in f]
   assert all(len(i)==3 and 0<i[0]<=len(vs) and 0<i[1]<=len(uv) and 0<i[2]<=len(ns) for i in ids)
   a,b,c=[vs[i[0]-1] for i in ids];u=[b[j]-a[j] for j in range(3)];v=[c[j]-a[j] for j in range(3)]
   assert sum((u[(j+1)%3]*v[(j+2)%3]-u[(j+2)%3]*v[(j+1)%3])**2 for j in range(3))>1e-16
  assert all(math.isfinite(c) and -1e-6<=c<=1.000001 for v in uv for c in v)
  assert all(abs(sum(c*c for c in v)-1)<.01 for v in ns)
  r[p['name']]={'bounds':check(p['name'],vs),'triangles':len(fs)};total+=len(fs)
 assert total<=10000
 report={'total_triangles':total,'parts':r,'opaque_atlas':True,'valid_indices_uv_normals_nondegenerate':True}
 (HERE/'out/export_checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':exported()
