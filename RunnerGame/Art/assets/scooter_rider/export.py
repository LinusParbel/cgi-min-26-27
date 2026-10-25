"""One bake, fixed topology, coordinates-only second pose. Run after build.py."""
from pathlib import Path
import bpy, sys, json, math
from mathutils import Vector
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[3]; OUT=HERE/'out'; PREFIX='CHR_ScooterRider'
if 'sources' not in globals():
    bpy.ops.wm.open_mainfile(filepath=str(HERE/'rider_rig.blend'))
    sources=sorted([o for o in bpy.data.objects if o.type=='MESH'],key=lambda o:o.name)
    records=json.loads((HERE/'previews/contact_measurements.json').read_text())
sys.path.insert(0,str(ROOT/'tools/asset-spike')); import asset_lib as al
def active(ob):
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob
for ob in sources:
    if not ob.data.uv_layers: continue
    ob.data.uv_layers.active.name='source'
    for material in ob.data.materials:
        uv=material.node_tree.nodes.get('__source_uv') or material.node_tree.nodes.new('ShaderNodeUVMap'); uv.name='__source_uv'; uv.uv_map='source'
        for node in list(material.node_tree.nodes):
            if node.type=='TEX_IMAGE' and not node.inputs['Vector'].is_linked: material.node_tree.links.new(uv.outputs['UV'],node.inputs['Vector'])
materials=[]
for ob in sources:
    for m in ob.data.materials:
        if m not in materials: materials.append(m)
counts={}
def capture(frame):
    bpy.context.scene.frame_set(frame); bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
    verts=[]; faces=[]; uvs=[]; slots=[]; smooth=[]
    for ob in sources:
        ev=ob.evaluated_get(dg); me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=dg); offset=len(verts)
        for v in me.vertices:
            p=ob.matrix_world@v.co; verts.append((-p.x,-p.y,p.z))
        layer=me.uv_layers.get('source') or me.uv_layers.active
        for p in me.polygons:
            faces.append(tuple(offset+i for i in p.vertices)); slots.append(materials.index(me.materials[p.material_index].original)); smooth.append(p.use_smooth)
            uvs.extend(tuple(layer.data[i].uv) if layer else (0,0) for i in p.loop_indices)
        counts[ob.name]=sum(len(p.vertices)-2 for p in me.polygons); ev.to_mesh_clear()
    return verts,faces,uvs,slots,smooth
verts,faces,uvs,slots,smooth=capture(1)
mesh=bpy.data.meshes.new('Fixed two-pose mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
for m in materials: mesh.materials.append(m)
for p,slot,sm in zip(mesh.polygons,slots,smooth): p.material_index=slot; p.use_smooth=sm
layer=mesh.uv_layers.new(name='source')
for l,uv in zip(layer.data,uvs): l.uv=uv
ob=bpy.data.objects.new(PREFIX,mesh); bpy.context.collection.objects.link(ob); active(ob)
tri=ob.modifiers.new('Deterministic triangulation','TRIANGULATE'); tri.quad_method='FIXED'; bpy.ops.object.modifier_apply(modifier=tri.name)
mesh=ob.data; assert len(mesh.polygons)<=35000,(len(mesh.polygons),counts)
topology=[tuple(p.vertices) for p in mesh.polygons]
print('PREBAKE_COUNTS',counts,'TOTAL',len(topology),flush=True)
for name,record in records.items():
    for foot in record['feet_native_bounds'].values():
        assert foot['sole_supported_fraction']>=.99
        assert abs(foot['lowest_sole_z']-.184)<.001
    clearance=json.loads((HERE/f'previews/{name}_clearance.json').read_text())
    assert sum(clearance['intersecting_triangle_pairs'].values())==0
assert records['ride']['head_top']-records['duck']['head_top']>=.30
if '--prepare-only' in sys.argv: raise SystemExit(0)
for source in sources: source.hide_render=True
al.bake_and_export(ob,str(OUT),PREFIX,res=2048,samples=16,ao_strength=.12,margin=8,uv_margin=.003,keep_origin=True)
(OUT/(PREFIX+'.obj')).unlink() # helper emits unnamed template; endpoint OBJs are the only deliverables
atlas_uv=[tuple(l.uv) for l in mesh.uv_layers.active.data]
for frame,name in ((1,'ride'),(2,'duck')):
    if frame==2:
        vertices,current_faces,_,_,_=capture(2); assert current_faces==faces; assert len(vertices)==len(mesh.vertices)
        for v,co in zip(mesh.vertices,vertices): v.co=co
        mesh.update()
    assert [tuple(p.vertices) for p in mesh.polygons]==topology
    assert [tuple(l.uv) for l in mesh.uv_layers.active.data]==atlas_uv
    ob.name=PREFIX+'_'+name; active(ob)
    bpy.ops.wm.obj_export(filepath=str(OUT/(ob.name+'.obj')),export_selected_objects=True,forward_axis='NEGATIVE_Z',up_axis='Y',export_triangulated_mesh=True,export_normals=True,export_uv=True,export_materials=False)
    (OUT/(ob.name+'_parts.json')).write_text(json.dumps({'texture':PREFIX+'.png','parts':[{'name':name,'obj':ob.name+'.obj','pivot':[0,0,0]}]},indent=2))
(OUT/(PREFIX+'_poses.json')).write_text(json.dumps({'texture':PREFIX+'.png','display':'mutually_exclusive','default':'ride','forward':'Blender +Y / engine -Z','origin':'Common scooter axle-midpoint at ground; pivot [0,0,0]','poses':{n:PREFIX+'_'+n+'_parts.json' for n in ('ride','duck')},'triangles_per_pose':len(topology),'resident_triangles_both_poses':len(topology)*2,'atlas_baked_from':'ride'},indent=2))
(OUT/'build_validation.json').write_text(json.dumps({'source_triangles':counts,'triangles_per_pose':len(topology),'vertices':len(mesh.vertices),'head_reduction_m':records['ride']['head_top']-records['duck']['head_top'],'contacts':records},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'rider_export.blend'))
print('EXPORT_COMPLETE',len(topology),flush=True)
