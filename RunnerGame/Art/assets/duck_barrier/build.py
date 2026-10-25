import sys,json
from pathlib import Path
import bpy
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'lib'));sys.path.insert(0,str(HERE))
import photo_lib as pl
al=pl.al
al.clear_scene()
bpy.context.scene.render.threads_mode='FIXED';bpy.context.scene.render.threads=8
m={k:al.material(k,c,dust=.025,grime=.035,scratches=.025) for k,c in {'white':(.82,.80,.72),'red':(.62,.018,.012),'steel':(.22,.25,.26),'rubber':(.045,.047,.043),'bolt':(.38,.40,.39)}.items()}
p=[]
def box(n,s,l,k,b=.003):
 o=al.box(n,s,l,m[k],bevel=b,segments=1);p.append(o);return o
for x in [-1.015,1.015]:
 box('weighted_base',(.25,.74,.13),(x+(0.06 if x>0 else -0.06),0,.065),'rubber',.025)
 box('base_socket',(.13,.22,.12),(x,0,.18),'steel',.009)
 box('upright',(.13,.13,1.48),(x,0,.93),'white',.006)
 box('top_cap',(.145,.145,.025),(x,0,1.6825),'red',.004)
 for y in [-.21,.21]:
  o=pl.tube('support_brace',(x,y,.13),(x,0,.53),.018,m['steel'],verts=8);p.append(o)
 for z in [.31,1.53]:
  for y in [-.072,.072]:
   o=al.cyl('fixing',.018,.012,(x,y,z),m['bolt'],axis='Y',verts=10,bevel=0);p.append(o)
box('overhead_crossbar',(2.16,.105,.25),(0,0,1.555),'white',.003)
# Diagonal red bands clipped exactly into the board face, small physical thickness.
def clip(poly,axis,value,keep):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=keep*(a[axis]-value)>=-1e-9;ib=keep*(b[axis]-value)>=-1e-9
  if ia:out.append(a)
  if ia!=ib:
   t=(value-a[axis])/(b[axis]-a[axis]);out.append(tuple(a[j]+t*(b[j]-a[j]) for j in range(2)))
 return out
for k in range(-5,6):
 x=k*.39
 poly=[(x,1.435),(x+.19,1.435),(x+.43,1.675),(x+.24,1.675)]
 poly=clip(clip(poly,0,-1.075,1),0,1.075,-1)
 if len(poly)<3:continue
 for side in [-1,1]:
  verts=[(a,side*.0535,z) for a,z in poly];faces=[tuple(range(len(verts))) if side==-1 else tuple(reversed(range(len(verts))))]
  me=bpy.data.meshes.new('stripe');me.from_pydata(verts,[],faces);me.materials.append(m['red']);o=bpy.data.objects.new('red_diagonal',me);bpy.context.collection.objects.link(o);p.append(o)
bpy.context.view_layer.update()
import verify
checks=verify.geometry(p);(HERE/'out/geometry_checks.json').write_text(json.dumps(checks,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'editable.blend'))
if '--export' in sys.argv:
 info=pl.bake_shared_and_export({'barrier':p},{'barrier':(0,0,0)},HERE/'out','PROP_DuckBarrier',res=512,samples=32)
 info.update({'units':'metres','source_axes':'Z up, front -Y','export_axes':'Y up, front +Z','dimensions':[2.4,.74,1.695],'clear_opening':{'width':1.9,'height':1.43},'gameplay_collider':False})
 (HERE/'out/PROP_DuckBarrier_parts.json').write_text(json.dumps(info,indent=2))
