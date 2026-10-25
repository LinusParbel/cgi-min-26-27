from pathlib import Path
import bpy, math, json, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(HERE/'rider_rig.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE'); rig.rotation_euler.z=math.pi
scooter=HERE.parent/'scooter_voi/out'; manifest=json.loads((scooter/'VEH_ScooterVoi_parts.json').read_text())
for part in manifest['parts']:
    bpy.ops.wm.obj_import(filepath=str(scooter/part['obj']),forward_axis='NEGATIVE_Z',up_axis='Y')
    ob=bpy.context.object; ob.location=part['pivot']
    m=bpy.data.materials.get('Scooter atlas')
    if not m:
        m=bpy.data.materials.new('Scooter atlas'); m.use_nodes=True; t=m.node_tree.nodes.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(str(scooter/manifest['texture']))
        m.node_tree.links.new(t.outputs['Color'],m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
    ob.data.materials.clear(); ob.data.materials.append(m)
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=16; scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED'; scene.render.threads=8; scene.render.resolution_x=650; scene.render.resolution_y=750; scene.render.resolution_percentage=100
scene.world.color=(.22,.22,.22)
for loc,power,size in [((2,3,5),450,4),((-3,1,3),350,3),((0,-3,4),450,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); ob=bpy.context.object; ob.data.energy=power; ob.data.shape='DISK'; ob.data.size=size; ob.rotation_euler=(Vector((0,0,1))-ob.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(); cam=bpy.context.object; scene.camera=cam; cam.data.type='ORTHO'
for frame,pose in ((1,'ride'),(2,'duck')):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    dashboard=[]; dashfaces=[]
    for ob in bpy.data.objects:
        if ob.type!='MESH' or 'ScooterVoi_body' not in ob.name: continue
        vv=[ob.matrix_world@v.co for v in ob.data.vertices]
        for face in ob.data.polygons:
            if min(vv[i].z for i in face.vertices)>1.08:
                offset=len(dashboard); dashboard.extend(vv[i] for i in face.vertices); dashfaces.append(tuple(range(offset,len(dashboard))))
    if dashboard:
        dash=BVHTree.FromPolygons(dashboard,dashfaces); intersections={}; nearest=[]
        for ob in bpy.data.objects:
            if ob.type!='MESH' or ob.name not in ('Human','Plain teal top and denim jeans'): continue
            ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=ev.to_mesh(); vv=[ob.matrix_world@v.co for v in me.vertices]
            tree=BVHTree.FromPolygons(vv,[tuple(p.vertices) for p in me.polygons]); intersections[ob.name]=len(tree.overlap(dash))
            nearest.extend(tree.find_nearest(p)[3] for p in dashboard); ev.to_mesh_clear()
            if ob.name=='Human':
                wraps={}
                for side in (-1,1):
                    distances=[]
                    for xoff in (-.025,0,.025):
                        for j in range(24):
                            a=j*2*math.pi/24; p=Vector((side*.235+xoff,.2681990457+.018*math.cos(a),.982+.018*math.sin(a)))
                            distances.append(tree.find_nearest(p)[3])
                    wraps[str(side)]={'min_surface_gap_m':min(distances),'samples_within_8mm':sum(d<.008 for d in distances),'samples':len(distances),'note':'Three cross-sections of actual cylindrical grip; measures skin proximity, not just wrist bone'}
                (HERE/f'previews/{pose}_grip_surfaces.json').write_text(json.dumps(wraps,indent=2))
        result={'dashboard_bounds':[[min(v[i] for v in dashboard),max(v[i] for v in dashboard)] for i in range(3)],'intersecting_triangle_pairs':intersections,'minimum_dashboard_vertex_to_skin_or_cloth_m':min(nearest)}
        (HERE/f'previews/{pose}_clearance.json').write_text(json.dumps(result,indent=2)); print('DASHBOARD_CLEARANCE',pose,result,flush=True)
        assert sum(intersections.values())==0,result
    if '--checkonly' in sys.argv: continue
    for view,loc,target,scale in [('side',(4,0,2),(0,0,.95),2.1),('front',(-2,4,2.4),(0,0,.95),2.1),('hands',(-1,3,2), (0,.26,1.01),.69),('feet',(2,2,1),(0,-.07,.29),.65)]:
        if '--finalcheck' in sys.argv and not ((pose=='duck' and view=='side') or (pose=='ride' and view=='feet')): continue
        cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=scale
        scene.render.filepath=str(HERE/f'previews/{pose}_{view}.png'); bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'assembly_preview.blend'))
