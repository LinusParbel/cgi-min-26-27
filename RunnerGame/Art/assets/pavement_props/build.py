"""Original generic pavement props; single isolated shared-atlas bake."""
import sys,math,json
from pathlib import Path
import bpy
from mathutils import Vector
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parents[1]/'lib'))
import photo_lib as pl
al=pl.al

def build():
 al.clear_scene()
 mats={k:al.material(k,c,dust=.05,grime=.08,scratches=.05,mottle=.09) for k,c in {'steel':(.075,.095,.10),'wood':(.29,.16,.075),'fixing':(.24,.25,.24)}.items()}
 p={k:[] for k in ['rack','table','chair']}
 def box(k,n,s,l,m='steel',bev=0):
  o=al.box(n,s,l,mats[m],bevel=bev,segments=1);p[k].append(o);return o
 def tube(k,n,a,b,r=.018,m='steel',v=12):
  o=pl.tube(n,a,b,r,mats[m],verts=v);p[k].append(o);return o
 def cyl(k,n,r,h,l,m='steel',v=24):
  o=al.cyl(n,r,h,l,mats[m],verts=v,bevel=0);p[k].append(o);return o
 # Continuous swept tube with tangent quarter bends, no exposed section caps.
 pts=[(-.375,0,.015),(-.375,0,.65)]
 for i in range(1,9):
  a=math.pi-math.pi/2*i/8;pts.append((-.25+.125*math.cos(a),0,.65+.125*math.sin(a)))
 pts.append((.25,0,.775))
 for i in range(1,9):
  a=math.pi/2-math.pi/2*i/8;pts.append((.25+.125*math.cos(a),0,.65+.125*math.sin(a)))
 pts.append((.375,0,.015))
 vs=[];fs=[]
 for i,c in enumerate(pts):
  tangent=Vector(pts[min(i+1,len(pts)-1)])-Vector(pts[max(0,i-1)]);tangent.normalize();u=Vector((0,1,0));v=tangent.cross(u).normalized()
  for j in range(12):vs.append(Vector(c)+.025*(u*math.cos(j*math.tau/12)+v*math.sin(j*math.tau/12)))
 for i in range(len(pts)-1):
  for j in range(12):a=i*12+j;b=i*12+(j+1)%12;fs.append((a,b,b+12,a+12))
 fs.extend([tuple(reversed(range(12))),tuple(range((len(pts)-1)*12,len(pts)*12))])
 me=bpy.data.meshes.new('swept_steel');me.from_pydata(vs,[],fs);me.materials.append(mats['steel']);o=bpy.data.objects.new('continuous_U',me);bpy.context.collection.objects.link(o);p['rack'].append(o)
 for x in [-.375,.375]:
  box('rack','mounting_foot',(.13,.15,.02),(x,0,.01))
  for y in [-.05,.05]:cyl('rack','anchor',.009,.008,(x,y,.024),'fixing',8)
 # Round timber tabletop: solid edge with subtle inset decorative grain slats.
 cyl('table','round_top',.35,.035,(0,0,.7225),'wood',48)
 cyl('table','top_support',.135,.025,(0,0,.6925))
 cyl('table','pedestal',.035,.66,(0,0,.35))
 for a in [0,math.pi/2,math.pi,3*math.pi/2]:
  d=Vector((math.cos(a),math.sin(a),0));tube('table','splayed_base',(0,0,.09),(.29*d.x,.29*d.y,.025),.022)
  box('table','foot_pad',(.085,.065,.02),(.29*d.x,.29*d.y,.01))
 # Four metal legs, bearer rails, five wooden seat slats and three back boards.
 for x in [-.18,.18]:
  for y in [-.17,.17]:
   tube('chair','leg',(x*1.08,y*1.1,.018),(x,y,.414),.018)
   cyl('chair','foot_pad',.022,.018,(x*1.08,y*1.1,.009),'steel',12)
  tube('chair','seat_bearer',(x,-.215,.415),(x,.215,.415))
  tube('chair','back_post',(x,.17,.41),(x,.235,.80),.016)
 for i in range(5):box('chair','seat_slat',(.45,.077,.025),(0,-.174+i*.087,.4375),'wood',.003)
 for z in [.60,.69,.78]:
  o=box('chair','back_board',(.45,.025,.08),(0,.17+(z-.41)/.39*.065,z),'wood',.003);o.rotation_euler.x=math.radians(-9.46)
 tube('chair','front_stretcher',(-.18,-.17,.20),(.18,-.17,.20),.012)
 # Rack long axis +Y; its plane is YZ, matching a bicycle parallel to the pavement.
 for o in p['rack']:
  x,y,z=o.location;o.location=(-y,x,z);o.rotation_euler.z+=math.pi/2
 bpy.context.view_layer.update();return p
if __name__=='__main__':
 p=build();bpy.ops.wm.save_as_mainfile(filepath=str(H/'editable.blend'))
 if '--source-only' in sys.argv:sys.exit(0)
 offsets={k:(i*4,0,0) for i,k in enumerate(p)}
 for k,objs in p.items():
  for o in objs:o.location.x+=offsets[k][0]
 bpy.context.view_layer.update()
 info=pl.bake_shared_and_export(p,offsets,H/'out','PROP_Pavement',res=1024,samples=32)
 (H/'out/bake_offsets.json').write_text(json.dumps(info,indent=2))
 for part in info['parts']:
  part['pivot']=[0,0,0]
  (H/'out'/('review_'+part['name']+'.json')).write_text(json.dumps({'texture':info['texture'],'parts':[part]},indent=2))
 (H/'out/PROP_Pavement_parts.json').write_text(json.dumps(info,indent=2))

 # Remove zero-area faces created by six-decimal OBJ serialization.
 import finish_export
 finish_export.clean()
