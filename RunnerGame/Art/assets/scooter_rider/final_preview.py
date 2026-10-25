"""Render actual exported assets in assembled coordinates, endpoints exclusive."""
from pathlib import Path
import bpy,json
from mathutils import Vector
HERE=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def import_manifest(folder,file):
    m=json.loads((folder/file).read_text()); material=bpy.data.materials.new(file); material.use_nodes=True
    t=material.node_tree.nodes.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(str(folder/m['texture']),check_existing=True)
    material.node_tree.links.new(t.outputs['Color'],material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
    result=[]
    for part in m['parts']:
        before=set(bpy.data.objects); bpy.ops.wm.obj_import(filepath=str(folder/part['obj']),forward_axis='NEGATIVE_Z',up_axis='Y')
        for ob in set(bpy.data.objects)-before:
            ob.location=part['pivot']; ob.data.materials.clear(); ob.data.materials.append(material)
            for p in ob.data.polygons: p.use_smooth=True
            result.append(ob)
    return result
import_manifest(HERE.parent/'scooter_voi/out','VEH_ScooterVoi_parts.json')
poses={name:import_manifest(HERE/'out',f'CHR_ScooterRider_{name}_parts.json') for name in ('ride','duck')}
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=12; scene.cycles.use_denoising=True; scene.render.threads_mode='FIXED'; scene.render.threads=2
scene.render.resolution_x=650; scene.render.resolution_y=750; scene.render.resolution_percentage=100; scene.world.color=(.22,.22,.22)
for loc,power,size in [((2,3,5),450,4),((-3,1,3),350,3),((0,-3,4),450,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); ob=bpy.context.object; ob.data.energy=power; ob.data.shape='DISK'; ob.data.size=size; ob.rotation_euler=(Vector((0,0,1))-ob.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(); cam=bpy.context.object; scene.camera=cam; cam.data.type='ORTHO'
for name,view,loc,target,scale in [('ride','side',(4,0,2),(0,0,.95),2.1),('duck','side',(4,0,2),(0,0,.95),2.1),('ride','hands',(-1,3,2),(0,.26,1.01),.69),('ride','feet',(2,2,1),(0,-.07,.29),.65)]:
    for pose,objects in poses.items():
        for ob in objects: ob.hide_render=pose!=name
    cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=scale
    scene.render.filepath=str(HERE/f'previews/export_{name}_{view}.png'); bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'final_assembly.blend'))
