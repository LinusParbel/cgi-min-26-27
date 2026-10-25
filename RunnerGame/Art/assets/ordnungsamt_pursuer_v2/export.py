"""Export the approved run to matching OBJ poses and one opaque baked atlas.

Works on an in-memory copy. Neutral/animated sources and runtime stay untouched.
"""
from pathlib import Path
import sys, json, math, hashlib
import bpy, bmesh, numpy as np
from mathutils import Matrix, Vector

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
sys.path.insert(0,str(REPO/'tools/asset-spike'))
import asset_lib as al
OUT=HERE/'out'; OUT.mkdir(exist_ok=True)
PREFIX='CHR_OrdnungsamtV2'
SOURCE=HERE/'officer_v2_run_preview.blend'
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (SOURCE,HERE/'officer_v2.blend')}
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene; scene.frame_set(1)

def active(ob):
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True)
    bpy.context.view_layer.objects.active=ob

def apply(ob,mod):
    active(ob); bpy.ops.object.modifier_apply(modifier=mod.name)

def opaque_cutout(ob,subdivisions):
    """Trim low-alpha hair/brow faces once, before deformation, preserving weights."""
    mat=ob.data.materials[0]
    image=mat.node_tree.nodes['AlphaMapTexture'].image
    pixels=np.array(image.pixels[:],dtype=np.float32).reshape(image.size[1],image.size[0],4)
    mod=ob.modifiers.new('Cutout tessellation','SUBSURF')
    mod.subdivision_type='SIMPLE'; mod.levels=subdivisions
    while list(ob.modifiers).index(mod)>0:
        active(ob); bpy.ops.object.modifier_move_up(modifier=mod.name)
    apply(ob,mod)
    bm=bmesh.new(); bm.from_mesh(ob.data); uv=bm.loops.layers.uv.active
    remove=[]
    for face in bm.faces:
        coords=[loop[uv].uv.copy() for loop in face.loops]
        coords.append(sum(coords,coords[0]*0)/len(coords))
        alpha=[pixels[min(image.size[1]-1,max(0,int(v.y*image.size[1]))),min(image.size[0]-1,max(0,int(v.x*image.size[0]))),3] for v in coords]
        if sum(alpha)/len(alpha)<.48: remove.append(face)
    bmesh.ops.delete(bm,geom=remove,context='FACES')
    bm.to_mesh(ob.data); bm.free(); ob.data.update()
    shader=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    for link in list(shader.inputs['Alpha'].links): mat.node_tree.links.remove(link)
    shader.inputs['Alpha'].default_value=1

sources=[]; reductions=[]
for ob in sorted(list(bpy.data.objects),key=lambda o:o.name):
    if ob.hide_render or ob.name=='Studio ground' or ob.type not in ('MESH','CURVE','FONT'): continue
    if ob.name.startswith('Moustache hair') and int(ob.name.split()[-1])%4:
        ob.hide_render=True; continue
    if ob.type=='CURVE':
        ob.data.bevel_resolution=0; ob.data.resolution_u=1
    if ob.type=='MESH':
        for mod in ob.modifiers:
            if mod.type=='SUBSURF': mod.levels=0; mod.render_levels=0
        skinned=any(m.type=='ARMATURE' for m in ob.modifiers)
        if ob.name in ('Human.short01','Human.eyebrow001'):
            opaque_cutout(ob,1 if ob.name=='Human.short01' else 2)
        if ob.name in ('Human.teeth_base','Human.short01','Service jacket and trousers'):
            mod=ob.modifiers.new('Fixed source reduction','DECIMATE')
            mod.ratio={'Human.teeth_base':.15,'Human.short01':.45,'Service jacket and trousers':.85}[ob.name]
            while list(ob.modifiers).index(mod)>0:
                active(ob); bpy.ops.object.modifier_move_up(modifier=mod.name)
            apply(ob,mod)
        if not skinned:
            for mod in list(ob.modifiers): apply(ob,mod)
            tris=sum(len(p.vertices)-2 for p in ob.data.polygons)
            if tris>50:
                mod=ob.modifiers.new('Fixed fitting reduction','DECIMATE')
                mod.ratio=.30 if tris>4000 or tris<350 else .45
                apply(ob,mod)
                reductions.append({'object':ob.name,'before':tris,'after':sum(len(p.vertices)-2 for p in ob.data.polygons)})
    sources.append(ob)

# Make implicit source-image UVs explicit before the bake adds another UV layer.
for ob in sources:
    if ob.type!='MESH' or not ob.data.uv_layers: continue
    ob.data.uv_layers.active.name='source'
    for mat in ob.data.materials:
        if not mat or not mat.use_nodes: continue
        nodes=mat.node_tree.nodes
        uvnode=nodes.get('__source_uv') or nodes.new('ShaderNodeUVMap')
        uvnode.name='__source_uv'; uvnode.uv_map='source'
        for node in list(nodes):
            if node.type=='TEX_IMAGE' and not node.inputs['Vector'].is_linked:
                mat.node_tree.links.new(uvnode.outputs['UV'],node.inputs['Vector'])

materials=[]
for ob in sources:
    for mat in ob.data.materials:
        if mat and mat not in materials: materials.append(mat)

def capture(frame):
    scene.frame_set(frame); bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get()
    verts=[]; faces=[]; uvs=[]; slots=[]; smooth=[]
    for ob in sources:
        ev=ob.evaluated_get(dg); me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
        offset=len(verts)
        # Source studio floor is -0.0265 m; move it to game ground once.
        verts.extend(tuple(ob.matrix_world @ v.co+Vector((0,0,.0265))) for v in me.vertices)
        layer=me.uv_layers.get('source') or me.uv_layers.active
        for p in me.polygons:
            faces.append(tuple(offset+i for i in p.vertices)); smooth.append(p.use_smooth)
            mat=me.materials[p.material_index].original if me.materials else None
            slots.append(materials.index(mat) if mat else 0)
            uvs.extend(tuple(layer.data[i].uv) if layer else (0,0) for i in p.loop_indices)
        ev.to_mesh_clear()
    return verts,faces,uvs,slots,smooth

verts,faces,source_uv,slots,smooth=capture(1)
mesh=bpy.data.meshes.new('Export topology'); mesh.from_pydata(verts,[],faces); mesh.update()
for mat in materials: mesh.materials.append(mat)
for p,slot,sm in zip(mesh.polygons,slots,smooth): p.material_index=slot; p.use_smooth=sm
layer=mesh.uv_layers.new(name='source')
for loop,coord in zip(layer.data,source_uv): loop.uv=coord
obj=bpy.data.objects.new(PREFIX,mesh); scene.collection.objects.link(obj); active(obj)
tri=obj.modifiers.new('Fixed triangles','TRIANGULATE'); tri.quad_method='FIXED'; apply(obj,tri)
mesh=obj.data
topology=[tuple(p.vertices) for p in mesh.polygons]
print('EXPORT_TEMPLATE',len(verts),len(topology),len(sources),flush=True)
if len(topology)>=80000:
    dg=bpy.context.evaluated_depsgraph_get(); counts=[]
    for source in sources:
        ev=source.evaluated_get(dg); me=ev.to_mesh()
        counts.append((sum(len(p.vertices)-2 for p in me.polygons),source.name)); ev.to_mesh_clear()
    print('EXPORT_DENSE',sorted(counts,reverse=True)[:20],flush=True)
assert len(topology)<80000, len(topology)
if '--inspect-only' in sys.argv:
    (OUT/'preparation.json').write_text(json.dumps({'triangles':len(topology),'vertices':len(verts),'reductions':reductions},indent=2))
    raise SystemExit(0)

# Avoid self-occlusion from the rigged originals during the atlas AO bake.
for original in bpy.data.objects:
    if original!=obj and original.type in ('MESH','CURVE','FONT'): original.hide_render=True
al.bake_and_export(obj,str(OUT),PREFIX,res=2048,samples=16,ao_strength=.18,margin=8,uv_margin=.003,keep_origin=True)
atlas_uv=[tuple(x.uv) for x in mesh.uv_layers.active.data]
records=[]; frames=[]
for frame in range(1,41):
    if frame>1:
        vertices,current_faces,_,_,_=capture(frame)
        assert current_faces==faces, ('Topology changed',frame)
        assert len(vertices)==len(mesh.vertices)
        for v,co in zip(mesh.vertices,vertices): v.co=co
        mesh.update()
    name=f'{PREFIX}_run_{frame:02d}'
    obj.name=name; active(obj)
    bpy.ops.wm.obj_export(filepath=str(OUT/(name+'.obj')),export_selected_objects=True,
        forward_axis='NEGATIVE_Z',up_axis='Y',export_triangulated_mesh=True,
        export_normals=True,export_uv=True,export_materials=False)
    (OUT/(name+'_parts.json')).write_text(json.dumps({'texture':PREFIX+'.png','parts':[{'name':name,'obj':name+'.obj','pivot':[0,0,0]}]},indent=2))
    frames.append({'obj':name+'.obj','duration_ms':20})
    records.append({'frame':frame,'triangles':len(mesh.polygons),'vertices':len(mesh.vertices),'min_z':min(v.co.z for v in mesh.vertices)})
    print('EXPORTED_FRAME',frame,flush=True)
assert [tuple(x.uv) for x in mesh.uv_layers.active.data]==atlas_uv
for file,digest in hashes.items(): assert hashlib.sha256((HERE/file).read_bytes()).hexdigest()==digest
(OUT/(PREFIX+'_animation.json')).write_text(json.dumps({'texture':PREFIX+'.png','loop':True,'forward':'Blender -Y / engine +Z','fps':50,'duration_ms':800,'frames':frames},indent=2))
(OUT/'validation.json').write_text(json.dumps({'source_sha256':hashes,'texture_size':2048,'opaque':True,'reductions':reductions,'poses':records},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'officer_v2_export_preview.blend'))
print('EXPORT_COMPLETE',len(topology),'triangles / 40 poses / 2048 atlas',flush=True)
