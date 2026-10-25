"""Original generic architecture; spec-driven construction, no external textures."""
import sys,json
from pathlib import Path
import bpy
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'lib'));sys.path.insert(0,str(HERE))
import photo_lib as pl
import verify
al=pl.al

def build(s):
 al.clear_scene();m={}
 for key in s.colors:
  m[key]=al.material(key,s.c(key),roughness=.82,dust=.10,streaks=.07,grime=.08,scratches=.02,mottle=.12)
 # Brick shader uses physical world X/Z coordinates, original procedural staggered bonds.
 mat=m['brick'];n=mat.node_tree.nodes;l=mat.node_tree.links;geo=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],sep.inputs[0]);vec=n.new('ShaderNodeCombineXYZ');l.new(sep.outputs['X'],vec.inputs['X']);l.new(sep.outputs['Z'],vec.inputs['Y']);l.new(sep.outputs['Y'],vec.inputs['Z']);brick=n.new('ShaderNodeTexBrick');l.new(vec.outputs[0],brick.inputs['Vector']);brick.inputs['Scale'].default_value=1;brick.inputs['Brick Width'].default_value=.32;brick.inputs['Row Height'].default_value=.105;brick.inputs['Mortar Size'].default_value=.007;brick.inputs['Color1'].default_value=(*s.c('brick'),1);brick.inputs['Color2'].default_value=(.40,.16,.085,1);brick.inputs['Mortar'].default_value=(.28,.24,.19,1);l.new(brick.outputs['Color'],n.get('Principled BSDF').inputs['Base Color'])
 parts={}
 w=s.d('width');h=s.d('height');d=s.d('depth');front=s.d('front_wall_y');gy=s.d('glass_y')
 for key in ['shop_ground','sandstone_upper','brick_upper']:
  obs=[];parts[key]=obs;wall=m['brick' if key=='brick_upper' else 'sandstone']
  def box(name,x0,x1,y0,y1,z0,z1,mat):
   o=al.box(key+'_'+name,(x1-x0,y1-y0,z1-z0),((x0+x1)/2,(y0+y1)/2,(z0+z1)/2),mat,bevel=0);obs.append(o);return o
  box('back',-w/2,w/2,.24,d/2,0,h,wall)
  if key=='shop_ground':
   openings=[(-2.6,-.85,.32,2.55),(-.58,.58,.08,2.55),(.85,2.6,.32,2.55)]
  else:
   ww=s.d('window_width');openings=[(x-ww/2,x+ww/2,s.d('window_bottom'),s.d('window_top')) for x in [-1.95,0,1.95]]
  cursor=-w/2
  for i,(a,b,z0,z1) in enumerate(openings):
   box('pier'+str(i),cursor,a,front,.24,0,h,wall);cursor=b
   box('below'+str(i),a,b,front,.24,0,z0,wall);box('above'+str(i),a,b,front,.24,z1,h,wall)
   box('glass_'+str(i),a+.06,b-.06,gy,gy+.045,z0+.06,z1-.06,m['glass'])
   # Deep visible returns and crisp dark frames set behind the masonry opening.
   f=.055
   for x in [a+.03,b-.085]:box('frame'+str(i),x,x+f,front+.045,gy+.02,z0+.025,z1-.025,m['frame'])
   for z in [z0+.025,z1-.08]:box('frame'+str(i),a+.03,b-.03,front+.045,gy+.02,z,z+f,m['frame'])
   box('mullion'+str(i),(a+b)/2-.022,(a+b)/2+.022,front+.07,gy+.02,z0+.05,z1-.05,m['frame'])
   box('transom'+str(i),a+.06,b-.06,front+.07,gy+.02,z0+(z1-z0)*.72,z0+(z1-z0)*.72+.035,m['frame'])
   box('sill'+str(i),a-.065,b+.065,-.35,-.05,max(0,z0-.075),z0+.015,m['trim'])
   if key!='shop_ground':box('lintel'+str(i),a-.08,b+.08,-.30,-.10,z1,z1+.12,m['trim'])
  box('pier_end',cursor,w/2,front,.24,0,h,wall)
  box('base',-w/2+.005,w/2-.005,-.30,.23,0,.16,m['plinth' if key=='shop_ground' else 'trim'])
  box('cornice_lower',-w/2+.005,w/2-.005,-.32,.23,h-.23,h-.13,m['trim']);box('cornice_cap',-w/2+.005,w/2-.005,-.4,.23,h-.10,h,m['trim'])
  # Thin side quoins finish exposed module edges without exceeding width.
  for x in [-3,2.88]:
   for z in [.3,.95,1.6,2.25]:box('quoin',x,x+.12,-.27,front,z,z+.22,m['trim'])
  if key=='shop_ground':
   aw=s.d('awning_width')/2
   box('awning',-aw,aw,-.4,-.20,2.64,2.72,m['awning']);box('valance',-aw,aw,-.4,-.36,2.50,2.65,m['awning'])
   box('door_handle',.39,.415,-.215,-.17,.95,1.22,m['trim'])
 bpy.context.view_layer.update();return parts
if __name__=='__main__':
 parts=build(pl.Spec(HERE/'spec.json'));report=verify.geometry(parts);(HERE/'out/geometry_checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'shopfront_kit.blend'))
 if '--export' in sys.argv:
  # Spatial separation is essential: variants must not occlude one another in AO.
  pivots={k:(i*8,0,0) for i,k in enumerate(parts)}
  for k,objs in parts.items():
   for o in objs:o.location.x+=pivots[k][0]
  bpy.context.view_layer.update()
  info=pl.bake_shared_and_export(parts,pivots,HERE/'out','AR_Shopfront',res=2048,samples=32)
  for p in info['parts']:p['pivot']=[0,0,0]
  (HERE/'out/AR_Shopfront_parts.json').write_text(json.dumps(info,indent=2))
