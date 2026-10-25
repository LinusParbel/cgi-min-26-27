"""Fresh CC0 MPFB civilian; reproducible two-pose scooter fit, Blender 5.2."""
from pathlib import Path
import sys, math, json
import bpy
from mathutils import Vector, Matrix, Quaternion
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[3]; RESEARCH=ROOT/'.model-research'
for d in ('previews','out','source'): (HERE/d).mkdir(exist_ok=True)
bootstrap=(RESEARCH/'inspect_human.py').read_text().split('bpy.ops.object.select_all')[0]
bootstrap=bootstrap.replace("ROOT/'mpfb-user'",repr(str(HERE/'source/mpfb-user')) and "Path("+repr(str(HERE/'source/mpfb-user'))+")")
exec(compile(bootstrap,str(RESEARCH/'inspect_human.py'),'exec'),{'__file__':str(RESEARCH/'inspect_human.py')})
from mpfb.services.humanservice import HumanService
from mpfb.services.targetservice import TargetService
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
macro=TargetService.get_default_macro_info_dict(); macro.update(gender=1.,age=.38,muscle=.40,weight=.48,height=.40)
body=HumanService.create_human(macro_detail_dict=macro)
assets=RESEARCH/'system-assets'
HumanService.set_character_skin(str(assets/'skins/middleage_caucasian_male/middleage_caucasian_male.mhmat'),body,skin_type='GAMEENGINE')
HumanService.add_builtin_rig(body,'game_engine'); rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
def fit(rel,kind):
    before=set(bpy.data.objects); HumanService.add_mhclo_asset(str(assets/rel),body,asset_type=kind,material_type='GAMEENGINE',subdiv_levels=0)
    return next(o for o in set(bpy.data.objects)-before if o.type=='MESH')
cloth=fit('clothes/male_casualsuit02/male_casualsuit02.mhclo','Clothes'); cloth.name='Plain teal top and denim jeans'
shoes=fit('clothes/shoes01/shoes01.mhclo','Clothes'); shoes.name='Civilian sneakers'
eyes=fit('eyes/low-poly/low-poly.mhclo','Eyes')
hair=fit('hair/short01/short01.mhclo','Hair')
brows=fit('eyebrows/eyebrow001/eyebrow001.mhclo','Eyebrows')
def mat(name,color):
    m=bpy.data.materials.new(name); m.use_nodes=True; m.diffuse_color=(*color,1)
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=.82
    return m
teal=mat('Unbranded teal cotton',(.018,.12,.15)); denim=mat('Denim blue',(.025,.055,.10)); sneaker=mat('Charcoal sneakers',(.024,.028,.034))
cloth.data.materials.clear(); cloth.data.materials.append(teal); cloth.data.materials.append(denim)
# Connected garment islands distinguish sleeves/shirt hem from jeans regardless
# of overlapping heights; a height threshold creates blue sleeve cuffs.
adj={i:set() for i in range(len(cloth.data.vertices))}
for e in cloth.data.edges: a,b=e.vertices; adj[a].add(b); adj[b].add(a)
unseen=set(adj); topverts=set()
while unseen:
    seed=unseen.pop(); group={seed}; todo=[seed]
    while todo:
        for j in adj[todo.pop()]&unseen: unseen.remove(j); group.add(j); todo.append(j)
    if max(cloth.data.vertices[i].co.z for i in group)>1.2: topverts.update(group)
for p in cloth.data.polygons: p.material_index=0 if p.vertices[0] in topverts else 1
shoes.data.materials.clear(); shoes.data.materials.append(sneaker)
# The adopted shoes01 upper is ankle-high. Keep its sole/toe anatomy but remove
# the high collar that would protrude through a deeply bent trouser leg.
import bmesh
bm=bmesh.new(); bm.from_mesh(shoes.data); cutoff=min(v.co.z for v in bm.verts)+.105
bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_center_median().z>cutoff],context='FACES')
bm.to_mesh(shoes.data); bm.free(); shoes.data.update()
# Shoes are rigid footwear. Source ankle/calf blend weights deform their soles
# during deep crouch; bind each complete sneaker to its foot, without scaling.
shoes.vertex_groups.clear()
for side,s in ((1,'l'),(-1,'r')):
    group=shoes.vertex_groups.new(name='foot_'+s)
    group.add([v.index for v in shoes.data.vertices if v.co.x*side>0],1,'REPLACE')
for o in (body,cloth,shoes,hair,eyes,brows):
    for m in o.modifiers:
        if m.type=='SUBSURF': m.levels=0; m.render_levels=0
    for p in o.data.polygons: p.use_smooth=True
# Hair cards are trimmed ONCE in rest state; use opaque geometry thereafter.
import numpy as np, bmesh
def cutout(ob):
    material=ob.data.materials[0]; node=material.node_tree.nodes.get('AlphaMapTexture')
    if node:
        im=node.image; pixels=np.array(im.pixels[:]).reshape(im.size[1],im.size[0],4)
        bm=bmesh.new(); bm.from_mesh(ob.data); uv=bm.loops.layers.uv.active
        remove=[]
        for f in bm.faces:
            coords=[l[uv].uv for l in f.loops]; c=sum(coords,Vector((0,0)))/len(coords)
            if pixels[min(im.size[1]-1,max(0,int(c.y*im.size[1]))),min(im.size[0]-1,max(0,int(c.x*im.size[0]))),3]<.45: remove.append(f)
        bmesh.ops.delete(bm,geom=remove,context='FACES'); bm.to_mesh(ob.data); bm.free()
    p=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    for l in list(p.inputs['Alpha'].links): material.node_tree.links.remove(l)
    p.inputs['Alpha'].default_value=1
cutout(hair); cutout(brows)
sources=sorted([body,cloth,shoes,eyes,hair,brows],key=lambda o:o.name)
for p in rig.pose.bones: p.rotation_mode='QUATERNION'
def orient(name,head,direction):
    rest=rig.data.bones[name]; delta=(rest.tail_local-rest.head_local).normalized().rotation_difference(Vector(direction).normalized())
    rig.pose.bones[name].matrix=Matrix.Translation(head) @ (delta @ rest.matrix_local.to_quaternion()).to_matrix().to_4x4()
def solve(a,b,l1,l2,pole):
    delta=b-a; dist=delta.length
    assert abs(l1-l2)<dist<l1+l2, ('unreachable',dist,l1+l2)
    d=delta/dist; v=Vector(pole); v=(v-d*v.dot(d)).normalized(); along=(l1*l1-l2*l2+dist*dist)/(2*dist)
    return a+d*along+v*math.sqrt(max(0,l1*l1-along*along))
def update(): bpy.context.view_layer.update()
def evaluated(ob):
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=ev.to_mesh(); pts=[ob.matrix_world@v.co for v in me.vertices]; ev.to_mesh_clear(); return pts
# Work in MPFB's native -Y frame then rotate everything through pi at capture.
# Target coordinates below are therefore x/y-negated scooter coordinates.
restfoot={}
shoe_rest=evaluated(shoes)
shoe_indices={s:[i for i,v in enumerate(shoe_rest) if v.x*side>0] for side,s in ((1,'l'),(-1,'r'))}
sole_indices={s:[i for i in ids if shoe_rest[i].z<min(shoe_rest[j].z for j in ids)+.008] for s,ids in shoe_indices.items()}
for side,s in ((1,'l'),(-1,'r')):
    inv=rig.data.bones['foot_'+s].matrix_local.inverted()
    restfoot[s]=[inv@v for v in evaluated(shoes) if v.x*side>0]
records={}
def pose(name):
    for p in rig.pose.bones: p.matrix_basis=Matrix.Identity(4)
    duck=name=='duck'; pelvis=rig.data.bones['pelvis']
    # Slight forward lean in ride; knee flex and torso lean for duck.
    hipheight=.76 if not duck else .51
    root=pelvis.head_local+Vector((0,.40 if duck else .045,hipheight-pelvis.head_local.z+.184))
    rot=Quaternion((1,0,0),math.radians(10 if not duck else 34))
    rig.pose.bones['pelvis'].matrix=Matrix.Translation(root) @ (rot@pelvis.matrix_local.to_quaternion()).to_matrix().to_4x4(); update()
    feet={}; hands={}
    for side,s in ((1,'l'),(-1,'r')):
        foot=rig.data.bones['foot_'+s]; q=foot.matrix_local.to_quaternion()
        # Narrow tandem stance, one foot forward, one behind.
        y=-.025 if side==1 else .225
        ankle=Vector((side*.027,y,.184-min((q@v).z for v in restfoot[s])))
        thigh=rig.data.bones['thigh_'+s]; calf=rig.data.bones['calf_'+s]; hip=rig.pose.bones[thigh.name].head.copy()
        for correction in range(3):
            knee=solve(hip,ankle,thigh.length,calf.length,(0,-1,0))
            orient(thigh.name,hip,knee-hip); update(); orient(calf.name,knee,ankle-knee); update()
            rig.pose.bones[foot.name].matrix=Matrix.Translation(ankle)@q.to_matrix().to_4x4(); update()
            allpts=evaluated(shoes); assert len(allpts)==len(shoe_rest)
            pts=[allpts[i] for i in shoe_indices[s]]
            ankle.z+=.184-min(v.z for v in pts)
        sole=[allpts[i] for i in sole_indices[s]]
        supported=[v for v in sole if -.09<=-v.x<=.09 and -.291<=-v.y<=.214]
        feet[s]={'whole_bounds_native':[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)],'sole_bounds_scooter':[[min((-v.x,-v.y,v.z)[i] for v in sole),max((-v.x,-v.y,v.z)[i] for v in sole)] for i in range(3)],'sole_supported_fraction':len(supported)/len(sole),'lowest_sole_z':min(v.z for v in sole)}
        # Palm travels forward and down; bar is underneath palm, not at wrist.
        hand=rig.data.bones['hand_'+s]
        forward=(rig.data.bones['middle_01_'+s].head_local-hand.head_local).normalized()
        radial=rig.data.bones['index_01_'+s].head_local-rig.data.bones['pinky_01_'+s].head_local
        radial=(radial-forward*radial.dot(forward)).normalized()
        restframe=Matrix((radial,forward,radial.cross(forward))).transposed()
        targetforward=Vector((0,-.96,-.28)).normalized(); thumb=Vector((-side,0,0))
        targetframe=Matrix((thumb,targetforward,thumb.cross(targetforward))).transposed()
        delta=(targetframe@restframe.transposed()).to_quaternion()
        grip=Vector((side*.235,-.2681990457,.982))
        wrist=grip-Vector((0,-.075,-.038))
        upper=rig.data.bones['upperarm_'+s]; lower=rig.data.bones['lowerarm_'+s]; shoulder=rig.pose.bones[upper.name].head.copy()
        elbow=solve(shoulder,wrist,upper.length,lower.length,(side*.5,.4,-.4))
        orient(upper.name,shoulder,elbow-shoulder); update(); orient(lower.name,elbow,wrist-elbow); update()
        rig.pose.bones[hand.name].matrix=Matrix.Translation(wrist)@(delta@hand.matrix_local.to_quaternion()).to_matrix().to_4x4()
        for digit in ('index','middle','ring','pinky'):
            for joint,ang in ((1,45),(2,65),(3,40)): rig.pose.bones[f'{digit}_{joint:02d}_{s}'].rotation_quaternion=Quaternion((1,0,0),math.radians(ang))
        for j,ang in ((1,20),(2,35),(3,25)): rig.pose.bones[f'thumb_{j:02d}_{s}'].rotation_quaternion=Quaternion((1,0,0),math.radians(ang))
        update(); hands[s]={'grip':list(grip),'wrist':list(wrist),'middle_knuckle':list(rig.pose.bones['middle_01_'+s].head)}
    update()
    records[name]={'feet_native_bounds':feet,'hands_native':hands,'head_top':max(v.z for v in evaluated(body))}
    for p in rig.pose.bones:
        p.keyframe_insert('location',frame=1 if not duck else 2); p.keyframe_insert('rotation_quaternion',frame=1 if not duck else 2); p.keyframe_insert('scale',frame=1 if not duck else 2)
pose('ride'); pose('duck')
scene=bpy.context.scene; scene.frame_start=1; scene.frame_end=2; scene.frame_set(1)
bpy.context.preferences.filepaths.save_version=0
scene.render.threads_mode='FIXED'; scene.render.threads=8
update()
(HERE/'previews/contact_measurements.json').write_text(json.dumps(records,indent=2))
print('CONTACT',records,flush=True)
bpy.ops.file.pack_all(); bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'rider_rig.blend'))
if '--export' in sys.argv: exec(compile((HERE/'export.py').read_text(),str(HERE/'export.py'),'exec'))
