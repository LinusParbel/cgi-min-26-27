import bpy, json, math, sys
from pathlib import Path
from mathutils import Vector
A=Path(__file__).resolve().parent;O=A/'out'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
# Parse directly rather than depend on importer operator versions.
v=[];uv=[];fs=[];name=None;groups={}
for l in (O/'KroepckeFacades.obj').read_text().splitlines():
 if l.startswith('v '):
  x,y,z=map(float,l.split()[1:]);v.append((x,-z,y))
 elif l.startswith('vt '):uv.append(tuple(map(float,l.split()[1:])))
 elif l.startswith('o '):name=l[2:]
 elif l.startswith('f '):groups.setdefault(name,[]).append([int(s.split('/')[0])-1 for s in l.split()[1:]])
mat=bpy.data.materials.new('opaque procedural limestone and glazing atlas');mat.use_nodes=True;nt=mat.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Roughness'].default_value=.75;tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(O/'KroepckeFacades.png'));nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
for n,faces in groups.items():
 mesh=bpy.data.meshes.new(n);mesh.from_pydata(v,[],faces);mesh.update();obj=bpy.data.objects.new(n,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat);layer=mesh.uv_layers.new()
 for poly in mesh.polygons:
  for li in poly.loop_indices:layer.data[li].uv=uv[mesh.loops[li].vertex_index]
# Neutral ground and shadow contact.
bpy.ops.mesh.primitive_plane_add(size=250,location=(265,-70,-1.08));g=bpy.context.object;gm=bpy.data.materials.new('paving');gm.diffuse_color=(.28,.29,.28,1);g.data.materials.append(gm)
world=bpy.context.scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.69,.75,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
bpy.ops.object.light_add(type='SUN',location=(200,-40,100));sun=bpy.context.object;sun.rotation_euler=(.5,.35,2.5);sun.data.energy=2.3
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.threads_mode='FIXED';scene.render.threads=8;scene.render.resolution_x=1500;scene.render.resolution_y=950;scene.render.resolution_percentage=100
scene.view_settings.view_transform='Standard';scene.render.image_settings.file_format='PNG'
for title,location,target,lens in [('magis',(290,-60,15),(247,-12,12),38),('center',(230,-20,16),(274,-112,12),33),('together',(330,20,70),(265,-80,8),37)]:
 if '--center-only' in sys.argv and title!='center':continue
 bpy.ops.object.camera_add(location=location);cam=bpy.context.object;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.data.clip_end=1000;scene.camera=cam;scene.render.filepath=str(A/'previews'/('model_'+title+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(A/'KroepckeFacades.blend'))
