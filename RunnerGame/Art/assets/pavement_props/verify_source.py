"""Evaluate source components and ensure each structural joint physically intersects."""
import sys,json
from pathlib import Path
import bpy
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H));import build

def check(parts):
 def named(k,n):return [o for o in parts[k] if o.name.startswith(n)]
 def bb(o):
  dg=bpy.context.evaluated_depsgraph_get();q=o.evaluated_get(dg);vs=[q.matrix_world@v.co for v in q.data.vertices]
  return [[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
 def contact(a,b):
  x,y=bb(a),bb(b);return all(min(x[1][i],y[1][i])-max(x[0][i],y[0][i])>=-1e-5 for i in range(3))
 def connected(k,n,m):
  a,b=named(k,n),named(k,m);assert a and b
  assert all(any(contact(x,y) for y in b) for x in a),(k,n,m)
 for k,n,c in [('rack','mounting_foot',2),('chair','foot_pad',4),('table','foot_pad',4)]:
  a=named(k,n);assert len(a)==c and all(abs(bb(o)[0][2])<1e-5 for o in a)
 for k,n,m in [('rack','mounting_foot','continuous_U'),('chair','leg','seat_bearer'),('chair','seat_slat','seat_bearer'),('chair','back_board','back_post'),('chair','back_post','seat_bearer'),('table','round_top','top_support'),('table','top_support','pedestal'),('table','splayed_base','pedestal'),('table','foot_pad','splayed_base')]:connected(k,n,m)
 assert abs(max(bb(o)[1][2] for o in named('chair','seat_slat'))-.45)<1e-5
 return True
p=build.build();check(p);negative=[]
for k,n in [('rack','continuous_U'),('chair','seat_bearer'),('chair','back_post'),('table','pedestal')]:
 broken={a:[o for o in objs if not(a==k and o.name.startswith(n))] for a,objs in p.items()}
 try:check(broken)
 except AssertionError:negative.append(k+':missing_'+n)
 else:raise AssertionError('missing component accepted')
o=next(o for o in p['chair'] if o.name.startswith('foot_pad'));o.location.z+=.1;bpy.context.view_layer.update()
try:check(p)
except AssertionError:negative.append('chair:raised_foot')
else:raise AssertionError('raised foot accepted')
(H/'out/structural_checks.json').write_text(json.dumps({'all_structural_contacts':True,'seat_top':.45,'negative_fixtures_rejected':negative},indent=2));print(negative)
