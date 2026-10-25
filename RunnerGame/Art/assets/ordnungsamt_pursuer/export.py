"""Export matching-topology run poses with one baked atlas, never touching runtime assets."""
import importlib.util
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]
sys.path.insert(0,str(REPO/'tools'/'asset-spike'))
import asset_lib as al
spec=importlib.util.spec_from_file_location('running',ROOT/'running_preview.py')
running=importlib.util.module_from_spec(spec)
spec.loader.exec_module(running)
OUT=ROOT/'out'
OUT.mkdir(exist_ok=True)
PREFIX='CHR_Ordnungsamt'


def prepare_template():
    objects=running.officer.build()
    # Convert lettering before posing: font tessellation can depend on its transform.
    for o in objects:
        if o.type=='FONT':
            bpy.ops.object.select_all(action='DESELECT')
            o.select_set(True)
            bpy.context.view_layer.objects.active=o
            bpy.ops.object.convert(target='MESH')
    for o in objects:
        if o.type!='MESH':
            continue
        bpy.context.view_layer.objects.active=o
        for modifier in list(o.modifiers):
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        if len(o.data.polygons)>60 and 'ORDNUNGSAMT' not in o.name:
            modifier=o.modifiers.new('Game reduction','DECIMATE')
            modifier.ratio=.30
            bpy.ops.object.modifier_apply(modifier=modifier.name)
    return [(o.name,o.data.copy(),o.matrix_world.copy()) for o in objects]


TEMPLATE=prepare_template()


def make_pose(frame):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    objects=[]
    for name,data,matrix in TEMPLATE:
        o=bpy.data.objects.new(name,data.copy())
        bpy.context.collection.objects.link(o)
        o.matrix_world=matrix
        objects.append(o)
    running.pose(objects,frame)
    bpy.ops.object.select_all(action='DESELECT')
    for o in sorted(objects,key=lambda o:o.name):
        o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.join()
    obj=bpy.context.object
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    obj.name=f'{PREFIX}_run_{frame+1:02d}'
    # One persistent world origin prevents per-frame centring jitter.
    bpy.context.scene.cursor.location=(0,0,0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    return obj


frames=[]
uv=None
topology=None
source_topology=None
smooth_flags=None
atlas=None
report=[]
for frame in range(8):
    obj=make_pose(frame)
    mesh=obj.data
    current=[tuple(p.vertices) for p in mesh.polygons]
    if frame==0:
        source_topology=current
        modifier=obj.modifiers.new('Explicit triangles','TRIANGULATE')
        modifier.quad_method='FIXED'
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        mesh=obj.data
        topology=[tuple(p.vertices) for p in mesh.polygons]
        smooth_flags=[p.use_smooth for p in mesh.polygons]
        assert len(topology)<=12000, len(topology)
        al.bake_and_export(obj,str(OUT),PREFIX,res=1024,samples=32,ao_strength=.30,keep_origin=True)
        uv=[tuple(loop.uv) for loop in mesh.uv_layers.active.data]
        atlas=OUT/(PREFIX+'.png')
    else:
        if current!=source_topology:
            first=next((i for i,(a,b) in enumerate(zip(current,source_topology)) if a!=b),-1)
            raise AssertionError(f'Pose {frame+1}: faces {len(current)}/{len(source_topology)}, first mismatch {first}: {current[first]} vs {source_topology[first]}')
        vertices=[tuple(v.co) for v in mesh.vertices]
        mesh.clear_geometry()
        mesh.from_pydata(vertices,[],topology)
        mesh.update()
        for polygon,smooth in zip(mesh.polygons,smooth_flags):
            polygon.use_smooth=smooth
        assert [p.use_smooth for p in mesh.polygons]==smooth_flags
        assert len(mesh.loops)==len(uv)
        layer=mesh.uv_layers.new(name='bake')
        for loop,coord in zip(layer.data,uv):
            loop.uv=coord
        mat=bpy.data.materials.new('Shared atlas')
        mat.use_nodes=True
        image=bpy.data.images.load(str(atlas),check_existing=True)
        nodes=mat.node_tree.nodes
        texture=nodes.new('ShaderNodeTexImage'); texture.image=image
        shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
        mat.node_tree.links.new(texture.outputs['Color'],shader.inputs['Base Color'])
        nodes.active=texture
        mesh.materials.clear(); mesh.materials.append(mat)
    name=f'{PREFIX}_run_{frame+1:02d}'
    bpy.ops.wm.obj_export(filepath=str(OUT/(name+'.obj')),export_selected_objects=True,
        forward_axis='NEGATIVE_Z',up_axis='Y',export_triangulated_mesh=True,
        export_normals=True,export_uv=True,export_materials=False)
    info={'texture':PREFIX+'.png','parts':[{'name':name,'obj':name+'.obj','pivot':[0,0,0]}]}
    (OUT/(name+'_parts.json')).write_text(json.dumps(info,indent=2))
    frames.append({'obj':name+'.obj','duration_ms':100})
    z=[(obj.matrix_world@v.co).z for v in mesh.vertices]
    assert abs(min(z)-(.035 if frame%4==2 else 0))<.005
    report.append({'pose':frame+1,'triangles':len(mesh.polygons),'vertices':len(mesh.vertices),
        'min_z':min(z),'max_z':max(z),'shared_uv':True})
    print('EXPORT_CHECK',json.dumps(report[-1]),flush=True)
(OUT/(PREFIX+'_animation.json')).write_text(json.dumps({'texture':PREFIX+'.png',
    'loop':True,'forward':'Blender -Y / engine +Z','frames':frames},indent=2))
(OUT/'validation.json').write_text(json.dumps(report,indent=2))
print('EXPORTED 8 poses sharing one 1024 atlas',flush=True)
