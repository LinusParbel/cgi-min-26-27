"""Inspect the saved scene in a separate Blender process."""
from pathlib import Path
import bpy, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree

here=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(here/'officer_v2.blend'))
dg=bpy.context.evaluated_depsgraph_get()
report={'meshes':[], 'rigs':[], 'unpacked_images':[], 'checks':{}}
for o in bpy.data.objects:
    if o.type=='ARMATURE': report['rigs'].append({'name':o.name,'bones':len(o.data.bones)})
    if o.type not in ('MESH','CURVE','FONT') or o.name=='Studio ground' or o.hide_render: continue
    ev=o.evaluated_get(dg); mesh=ev.to_mesh(); mesh.calc_loop_triangles()
    points=[o.matrix_world @ v.co for v in mesh.vertices]
    report['meshes'].append({'name':o.name,'triangles':len(mesh.loop_triangles),'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]})
    ev.to_mesh_clear()
for im in bpy.data.images:
    if im.source=='FILE' and not im.packed_file: report['unpacked_images'].append(im.name)
assert report['rigs'] and report['rigs'][0]['bones']==53, report['rigs']
assert not report['unpacked_images'], report['unpacked_images']
assert all((here/'previews'/f'{name}.png').is_file() for name in ['three_quarter','back','face','hand','shoes','front'])
# The collar bug placed front zipper pieces on the back through an open neckline.
zipper=[o for o in bpy.data.objects if o.name.startswith('Zipper ') or o.name=='Central zipper tape']
assert zipper and all(o.matrix_world.translation.y<0 for o in zipper if o.type=='MESH')
report['checks']['zipper_meshes_on_front']=True
cloth=bpy.data.objects['Service jacket and trousers']; tree=BVHTree.FromObject(cloth,dg)
label=bpy.data.objects['Back identification backing']
offsets=[]
for vertex in label.data.vertices:
    w=label.matrix_world @ vertex.co
    p,_,_,_=tree.ray_cast(Vector((w.x,1,w.z)),Vector((0,-1,0)))
    assert p is not None
    offsets.append(w.y-p.y)
assert min(offsets)>.005 and max(offsets)<.007, (min(offsets),max(offsets))
assert label.data.uv_layers and label.data.materials
report['checks']['back_label_clearance_m']=[min(offsets),max(offsets)]
report['checks']['label_texture_packed']=any(im.name.startswith('identification_patch') and im.packed_file for im in bpy.data.images)
assert report['checks']['label_texture_packed']
if 'Vest front shell' in bpy.data.objects:
    points=[]; polygons=[]
    for name in ('Service jacket and trousers','Jacket front closure and inner collar','Pale blue shirt neckline'):
        ob=bpy.data.objects[name]; ev=ob.evaluated_get(dg); me=ev.to_mesh(); start=len(points)
        points.extend(ob.matrix_world @ v.co for v in me.vertices)
        polygons.extend(tuple(start+i for i in p.vertices) for p in me.polygons); ev.to_mesh_clear()
    garment_tree=BVHTree.FromPolygons(points,polygons)
    for back in (False,True):
        shell=bpy.data.objects['Vest back shell' if back else 'Vest front shell']
        vest_tree=BVHTree.FromObject(shell,dg)
        label=bpy.data.objects['Vest back ORDNUNGSAMT label' if back else 'Vest front ORDNUNGSAMT label']
        offsets=[]; gaps=[]; torso_gaps=[]
        for vertex in label.data.vertices:
            w=label.matrix_world @ vertex.co
            p,_,_,_=vest_tree.ray_cast(Vector((w.x,1 if back else -1,w.z)),Vector((0,-1 if back else 1,0)))
            assert p is not None
            offsets.append((w.y-p.y)*(1 if back else -1))
        assert min(offsets)>.004 and max(offsets)<.008, (back,min(offsets),max(offsets))
        for vertex in shell.data.vertices:
            w=shell.matrix_world @ vertex.co
            p,_,_,_=garment_tree.ray_cast(Vector((w.x,1 if back else -1,w.z)),Vector((0,-1 if back else 1,0)))
            if p is not None and (p.y>0 if back else p.y<0):
                gap=(w.y-p.y)*(1 if back else -1); gaps.append(gap)
                if 1.13<w.z<1.44 and abs(w.x)<.17: torso_gaps.append(gap)
        report['checks']['vest_back' if back else 'vest_front']={'label_clearance_m':[min(offsets),max(offsets)],'shell_to_garment_gap_m':[min(gaps),max(gaps)],'torso_gap_m':[min(torso_gaps),max(torso_gaps)]}
        assert min(gaps)>0, ('Vest cuts through garment',back,min(gaps))
        assert min(torso_gaps)>.011, ('Padded torso inner layer intersects garment',back,min(torso_gaps))
    assert all(f'Vest shoulder bridge {side}' in bpy.data.objects for side in (-1,1))
    assert all(f'Vest side fastening band {side} {level}' in bpy.data.objects for side in (-1,1) for level in (0,1))
    assert all(o.location.y<0 for o in bpy.data.objects if o.name.startswith('Vest zipper'))
    report['checks']['vest_separate_panels_shoulders_side_bands']=True
report['checks']['preview_only']='Accessories require deformation checks before animation; no engine export performed.'
report['visible_mesh_triangles']=sum(m['triangles'] for m in report['meshes'])
(here/'previews'/'validation.json').write_text(json.dumps(report,indent=2))
print('OFFICER_V2_VERIFIED',json.dumps({'triangles':report['visible_mesh_triangles'],'rigs':report['rigs'],'unpacked_images':report['unpacked_images'],'checks':report['checks']}),flush=True)
