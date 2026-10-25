import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
A=Path(__file__).resolve().parent; ROOT=A.parents[3]
sys.path.insert(0,str(ROOT/'RunnerGame/Art/lib'))
from photo_lib import al,bake_shared_and_export

def tri(o):
 o.data.calc_loop_triangles();return len(o.data.loop_triangles)
def build():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 src=ROOT/'.model-research/city-car-candidates/innerscene-hatchback.glb'
 assert hashlib.sha256(src.read_bytes()).hexdigest()=='107410e01453abbce452fabbe6d51436fb98a0920672643a893263a8861873d7'
 bpy.ops.import_scene.gltf(filepath=str(src))
 # Source headlamps and hood are at -X; map (x,y,z)->(y,-x,z).
 mats={}
 for name,col in {'paint':(.015,.105,.24),'black':(.012,.017,.022),'rubber':(.018,.022,.027),'glass':(.055,.105,.15),'chrome':(.31,.34,.37),'steel':(.18,.20,.23),'redlens':(.38,.012,.018),'clearlens':(.60,.66,.71),'white':(.65,.67,.66)}.items():
  m=bpy.data.materials.new('opaque_'+name);m.diffuse_color=(*col,1);m.use_nodes=True
  p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=.45
  mats[name]=m
 parts={'body':[]};pivots={'body':(0,0,0)};log=[]
 for o in list(bpy.data.objects):
  if o.type!='MESH': bpy.data.objects.remove(o,do_unlink=True);continue
  n=o.name;before=tri(o);origm=[m.name if m else '' for m in o.data.materials]
  drop=any(s in n.lower() for s in ['lug_','valve_stem','tread blocks','brake','rotor','steering','headrest','seat ','carpet','console','instrument','grille inner mesh','parking sensor','projector reflector','headlamp reflector','exhaust','shark fin']) or n=='Cube'
  if drop:
   log.append({'name':n,'before':before,'after':0,'action':'drop hidden interior / tiny fitting / redundant optical insert'});bpy.data.objects.remove(o,do_unlink=True);continue
  # Make mesh unique before reducing reused wheel instances.
  o.data=o.data.copy()
  mw=o.matrix_world.copy();o.matrix_world.identity()
  for v in o.data.vertices:
   q=mw@v.co;v.co=(q.y,-q.x,q.z-.0041)
  for i,mn in enumerate(origm):
   key=mn.split('.')[0];key=key if key in mats else 'black'
   o.data.materials[i]=mats[key]
  # Per-family budgets preserve coarse contour parts and concentrate reduction on dense round fittings.
  target=before
  if 'body shell' in n: target=3400
  elif 'Sculpted_tyre' in n:target=420
  elif 'Alloy_five_spoke' in n:target=260
  elif 'Crowned roof' in n:target=380
  elif 'glass' in n.lower() or 'windshield' in n.lower():target=min(before,120)
  elif 'shut line' in n.lower() or 'seam' in n.lower() or 'joint' in n.lower():target=min(before,72)
  elif 'fender lip' in n or 'Wheelhouse' in n:target=100
  elif 'tailgate rear pillar' in n:target=220
  elif before>150:target=min(before,96)
  if 'Sculpted_tyre' in n:
   vs=[v.co.copy() for v in o.data.vertices];c=Vector([(min(v[i] for v in vs)+max(v[i] for v in vs))/2 for i in range(3)])
   verts=[];faces=[]
   for dx,r in [(-.1125,.225),(-.1125,.285),(-.09,.31205),(.09,.31205),(.1125,.285),(.1125,.225)]:
    for j in range(40):
     a=2*math.pi*j/40;verts.append((c.x+dx,c.y+r*math.cos(a),.31205+r*math.sin(a)))
   for i in range(6):
    for j in range(40):faces.append((i*40+j,i*40+(j+1)%40,((i+1)%6)*40+(j+1)%40,((i+1)%6)*40+j))
   me=bpy.data.meshes.new(n+'_smooth_profile');me.from_pydata(verts,[],faces);me.materials.append(mats['rubber']);o.data=me
   target=before
  if target<before:
   bpy.context.view_layer.objects.active=o;o.select_set(True)
   mod=o.modifiers.new('family silhouette reduction','DECIMATE');mod.ratio=target/before
   bpy.ops.object.modifier_apply(modifier=mod.name);o.select_set(False)
  if 'Sculpted_tyre' in n or 'Alloy_five_spoke' in n or 'Center_cap' in n:
   vs=[v.co for v in o.data.vertices];c=Vector([(min(v[i] for v in vs)+max(v[i] for v in vs))/2 for i in range(3)])
   key=('front' if c.y>0 else 'rear')+('_left' if c.x<0 else '_right')
   parts.setdefault(key,[]).append(o)
   # Authored axle positions from source tyre bounding boxes (not mesh mean).
   pivots[key]=( -.775 if c.x<0 else .775,1.2321 if c.y>0 else -1.3505,.31205)
  else:parts['body'].append(o)
  log.append({'name':n,'before':before,'after':tri(o),'action':'preserve' if target==before else 'targeted family reduction'})
 (A/'reduction-log.json').write_text(json.dumps(log,indent=2))
 return parts,pivots

def check(parts,pivots):
 total=sum(tri(o) for v in parts.values() for o in v);assert total<=18000,total
 stats={'triangles':total,'parts':{},'forward_evidence':'Source hood/headlamps at negative X mapped to positive Y'}
 for k,objs in parts.items():
  vs=[v.co for o in objs for v in o.data.vertices];bounds=[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)]
  assert all(math.isfinite(c) for v in vs for c in v)
  for o in objs:
   assert all(p.area>1e-12 for p in o.data.polygons),o.name
  if k!='body':
   assert abs(bounds[2][0])<.003,(k,bounds)
   assert abs((bounds[1][0]+bounds[1][1])/2-pivots[k][1])<.002
  stats['parts'][k]={'triangles':sum(tri(o) for o in objs),'bounds':bounds,'pivot':pivots[k]}
 assert len(parts)==5
 (A/'pre-bake-check.json').write_text(json.dumps(stats,indent=2));return stats

if __name__=='__main__':
 p,piv=build();print(check(p,piv))
 bpy.ops.wm.save_as_mainfile(filepath=str(A/'editable.blend'))
 scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=8
 if '--export' in sys.argv:
  bake_shared_and_export(p,piv,A/'out','VEH_CityCar',res=2048,samples=32)
  # Imported wheel nodes retain a 2.858 mm transform offset after join. Recenter
  # each exported wheel on the measured axle without changing baked UVs.
  from normalize_export import normalize
  normalize(A)
 else:
  scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.color_type='MATERIAL';scene.display.shading.light='STUDIO';scene.display.shading.show_shadows=True
  scene.world.color=(.22,.22,.22);scene.render.resolution_x=1000;scene.render.resolution_y=750;scene.render.resolution_percentage=100
  bpy.ops.object.camera_add(location=(5,6,3.4));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.7))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=5.7;scene.camera=cam
  scene.render.filepath=str(A/'previews/reduced-workbench.png');bpy.ops.render.render(write_still=True)
