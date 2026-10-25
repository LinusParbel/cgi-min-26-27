"""Original generic furniture. Headless Blender, --export performs one atlas bake."""
import sys,json,math,random
from pathlib import Path
import bpy
from mathutils import Vector
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'lib'));sys.path.insert(0,str(HERE))
import photo_lib as pl
import verify
al=pl.al
S=json.loads((HERE/'spec.json').read_text());D=S['dims']
def build():
 al.clear_scene(); random.seed(S['seed'])
 mats={k:al.material(k,c,dust=.07,grime=.12,scratches=.08,streaks=.12,mottle=.12) for k,c in {'wood':(.28,.125,.046),'steel':(.055,.072,.075),'concrete':(.34,.32,.28),'soil':(.065,.043,.025),'leaf':(.075,.17,.035),'lens':(.63,.69,.64),'bolt':(.22,.24,.23)}.items()}
 parts={k:[] for k in ['bench','planter','lamp']}
 def box(part,name,size,loc,mat,bevel=.008):
  o=al.box(name,size,loc,mats[mat],bevel=bevel,segments=2);parts[part].append(o);return o
 def tube(part,name,a,b,r,mat='steel',verts=12):
  o=pl.tube(name,a,b,r,mats[mat],verts=verts);parts[part].append(o);return o
 def cyl(part,name,r,h,loc,mat,r2=None):
  o=al.cyl(name,r,h,loc,mats[mat],verts=16,bevel=.004,segments=1,r2=r2);parts[part].append(o);return o
 # Five broad seat boards and four gently reclined back boards.
 for i in range(5):box('bench','seat_slat', (D['bench_width'],.085,.04),(0,-.235+i*.1,.43),'wood',.006)
 for i in range(4):
  o=box('bench','back_slat',(1.8,.04,.073),(0,.235+i*.018,.56+i*.085),'wood',.006);o.rotation_euler.x=math.radians(-12)
 for x in [-.68,.68]:
  box('bench','foot',(.13,.53,.035),(x,-.015,.0175),'steel')
  for y in [-.205,.185]:tube('bench','splayed_leg',(x,y, .035),(x,y*.65,.405),.028)
  tube('bench','seat_rail',(x,-.27,.394),(x,.23,.394),.027)
  tube('bench','back_upright',(x,.18,.37),(x,.325,.855),.024)
  # Raised hand rails slope gently into backrest; grounded support at front.
  tube('bench','arm_front',(x,-.245,.40),(x,-.245,.635),.019)
  tube('bench','armrest',(x,-.245,.635),(x,.25,.675),.023)
  for y in [-.2,.18]:cyl('bench','fixing',.012,.008,(x,y,.456),'bolt')
 tube('bench','crossbrace',(-.68,.12,.24),(.68,.12,.24),.019)
 # Closed thick-walled planter, actual cavity to soil surface.
 w=D['planter_width'];h=D['planter_height'];wall=D['planter_wall']
 box('planter','bottom',(.82,.82,.08),(0,0,.04),'concrete',.015)
 for x in [-1,1]:box('planter','sidewall', (wall,w,h-.12),(x*(w-wall)/2,0,(h+.04)/2),'concrete',.012)
 for y in [-1,1]:box('planter','endwall',(w-2*wall,wall,h-.12),(0,y*(w-wall)/2,(h+.04)/2),'concrete',.012)
 for x in [-1,1]:box('planter','rim',(wall+.025,w+.025,.06),(x*(w-wall)/2,0,h-.03),'concrete',.009)
 for y in [-1,1]:box('planter','rim',(w-2*wall-.025,wall+.025,.06),(0,y*(w-wall)/2,h-.03),'concrete',.009)
 box('planter','soil',(.73,.73,.045),(0,0,.665),'soil',.009)
 for k in range(9):
  angle=k*2.399;x=.22*math.cos(angle);y=.22*math.sin(angle);top=.99+random.random()*.22
  tube('planter','twig',(0,0,.68),(x,y,top),.009,'wood',6)
  verts=[];faces=[]
  for i in range(16):
   a=random.random()*math.tau;z=.79+random.random()*(top-.73);r=random.random()*.15
   c=Vector((x+r*math.cos(a),y+r*math.sin(a),z));u=Vector((math.cos(a),math.sin(a),.25))*.07;v=Vector((-.3*math.sin(a),.3*math.cos(a),1))*.035
   n=len(verts);verts.extend([c-u,c+v,c+u,c-v]);faces.extend([(n,n+1,n+2),(n,n+2,n+3),(n+2,n+1,n),(n+3,n+2,n)])
  mesh=bpy.data.meshes.new('opaque_leaves');mesh.from_pydata(verts,[],faces);mesh.materials.append(mats['leaf']);o=bpy.data.objects.new('two_sided_leaves',mesh);bpy.context.collection.objects.link(o);parts['planter'].append(o)
 # Profiled mast with an explicitly sampled curved arm, not a straight elbow.
 cyl('lamp','baseplate',.18,.045,(0,0,.0225),'steel')
 cyl('lamp','basecollar',.13,.25,(0,0,.17),'steel',.095)
 cyl('lamp','mast',.075,5.10,(0,0,2.84),'steel',.043)
 for x in [-.105,.105]:
  for y in [-.105,.105]:cyl('lamp','anchor',.014,.02,(x,y,.055),'bolt')
 points=[(0,0,5.36)]
 for i in range(1,13):
  a=(math.pi/2)*i/12;points.append((0,-.6*(1-math.cos(a)),5.36+.6*math.sin(a)))
 points.append((0,-.92,5.96))
 for a,b in zip(points,points[1:]):tube('lamp','curved_arm',a,b,.041)
 box('lamp','head',(.27,.60,.08),(0,-1.02,5.96),'steel',.035)
 box('lamp','underside_lens',(.205,.46,.018),(0,-1.04,5.911),'lens',.007)
 box('lamp','access_door',(.09,.013,.25),(0,-.074,.66),'steel',.006)
 bpy.context.view_layer.update();return parts
if __name__=='__main__':
 parts=build();checks=verify.geometry(parts);(HERE/'out/geometry_checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks))
 bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'editable.blend'))
 if '--export' in sys.argv:
  offsets={k:(i*12,0,0) for i,k in enumerate(parts)}
  for k,objs in parts.items():
   for o in objs:o.location.x+=offsets[k][0]
  bpy.context.view_layer.update()
  info=pl.bake_shared_and_export(parts,offsets,HERE/'out','PROP_StreetFurniture',res=1024,samples=32)
  (HERE/'out/bake_offsets.json').write_text(json.dumps(info,indent=2))
  for p in info['parts']:p['pivot']=[0,0,0]
  (HERE/'out/PROP_StreetFurniture_parts.json').write_text(json.dumps(info,indent=2))
  import finish_export
  finish_export.finish()
