import bpy,json,math
from pathlib import Path
A=Path(__file__).resolve().parent
def verify(parts,pivots):
 dg=bpy.context.evaluated_depsgraph_get();total=0;report={}
 for key,objs in parts.items():
  vs=[];nt=0;bad=[]
  for o in objs:
   ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();nt+=len(me.loop_triangles)
   vs.extend([o.matrix_world@v.co for v in me.vertices])
   for t in me.loop_triangles:
    a,b,c=[me.vertices[i].co for i in t.vertices]
    if (b-a).cross(c-a).length<1e-12:bad.append(o.name)
   ev.to_mesh_clear()
  assert not bad,('degenerate evaluated geometry',bad[:5])
  bounds=[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)]
  if key!='body':
   p=pivots[key];assert abs(bounds[2][0])<1e-5
   assert abs((bounds[1][0]+bounds[1][1])/2-p[1])<.001
   assert abs((bounds[2][1]+bounds[2][0])/2-p[2])<.001
   assert .75<bounds[2][1]<.82
  else:
   assert bounds[0][1]-bounds[0][0]<=2.45
   assert 5.5<bounds[1][1]-bounds[1][0]<5.9
   assert 2.4<bounds[2][1]<2.6
  report[key]={'triangles':nt,'bounds':bounds,'pivot':pivots[key]};total+=nt
 assert set(parts)=={'body','front_left','front_right','rear_left','rear_right'}
 assert total<=18000,total
 report['total_triangles']=total
 (A/'pre-bake-independent.json').write_text(json.dumps(report,indent=2));print('INDEPENDENT_PRECHECK',total)
