"""Rigged 0.8-second in-place run preview; neutral source is never overwritten."""
from pathlib import Path
import math, json, sys, hashlib
import bpy
from mathutils import Vector,Quaternion,Matrix

HERE=Path(__file__).resolve().parent
FRAMES=40
FPS=50
SOURCE_HASH=hashlib.sha256((HERE/'officer_v2.blend').read_bytes()).hexdigest()
OUT=HERE/'previews/run'; OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(HERE/'officer_v2.blend'))
rig=bpy.data.objects['Human.rig']
scene=bpy.context.scene
rig.animation_data_clear()
for p in rig.pose.bones:
    p.rotation_mode='QUATERNION'; p.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()

def bone_parent(ob,bone):
    world=ob.matrix_world.copy()
    ob.parent=rig; ob.parent_type='BONE'; ob.parent_bone=bone; ob.matrix_world=world

# Clothing/body already have MPFB armature weights. Fit rigid equipment to the
# appropriate moving body section instead of leaving it behind in world space.
attachments={}
for ob in list(bpy.data.objects):
    if ob.type not in ('MESH','CURVE','FONT') or ob.name=='Studio ground' or ob.hide_render: continue
    if any(m.type=='ARMATURE' for m in ob.modifiers): continue
    name=ob.name
    bone='spine_03'
    if name.startswith(('Moustache hair','Forehead crease','Nasolabial crease')): bone='head'
    elif name.startswith(('Boot lace','Boot eyelet')): bone='foot_r' if ' -1 ' in name else 'foot_l'
    elif name.startswith(('Duty trouser cargo',)):
        bone='thigh_r' if name.endswith(' -1') else 'thigh_l'
    elif name.startswith(('Belt','Buckle','Duty belt','Utility pouch','Pouch snap')): bone='pelvis'
    elif name.startswith(('Sleeve','Hannover sleeve')): bone='upperarm_r' if ' -1' in name else 'upperarm_l'
    bone_parent(ob,bone); attachments[name]=bone

def radians(value): return math.radians(value)
def local_world_rotation(name,axis,angle):
    rest=rig.data.bones[name].matrix_local.to_quaternion()
    rig.pose.bones[name].rotation_quaternion=rest.inverted() @ Quaternion(axis,angle) @ rest
def orient(name,head,direction):
    rest=rig.data.bones[name]
    delta=(rest.tail_local-rest.head_local).normalized().rotation_difference(Vector(direction).normalized())
    q=delta @ rest.matrix_local.to_quaternion()
    rig.pose.bones[name].matrix=Matrix.Translation(head) @ q.to_matrix().to_4x4()
def two_bone(hip,ankle,l1,l2):
    delta=ankle-hip; distance=delta.length
    if distance>l1+l2-.002:
        ankle=hip+delta.normalized()*(l1+l2-.002); delta=ankle-hip; distance=delta.length
    direction=delta.normalized()
    pole=Vector((0,-1,0)); pole=(pole-direction*direction.dot(pole)).normalized()
    along=(l1*l1-l2*l2+distance*distance)/(2*distance)
    height=math.sqrt(max(0,l1*l1-along*along))
    return hip+direction*along+pole*height,ankle
def smooth_profile(t,keys):
    t=t%1
    for i,((a,va),(b,vb)) in enumerate(zip(keys,keys[1:])):
        if t<=b:
            previous=keys[i-1] if i else (keys[-2][0]-1,keys[-2][1])
            following=keys[i+2] if i+2<len(keys) else (keys[1][0]+1,keys[1][1])
            ma=(vb-previous[1])/(b-previous[0]); mb=(following[1]-va)/(following[0]-a)
            u=(t-a)/(b-a)
            return (2*u**3-3*u*u+1)*va+(u**3-2*u*u+u)*(b-a)*ma+(-2*u**3+3*u*u)*vb+(u**3-u*u)*(b-a)*mb
    return keys[-1][1]

foot_pitch=[(0,-5),(.22,0),(.34,25),(.55,40),(.70,12),(.84,-8),(1,-5)]
def foot_forward(t):
    # Constant backward travel while planted, C1 return path during swing.
    speed=1.70
    if t<=.30: return -.25+speed*t
    keys=[(.30,.26,speed),(.43,.31,0),(.78,-.22,-1.5),(.90,-.295,0),(1,-.25,speed)]
    for (a,va,ma),(b,vb,mb) in zip(keys,keys[1:]):
        if t<=b:
            u=(t-a)/(b-a)
            return (2*u**3-3*u*u+1)*va+(u**3-2*u*u+u)*(b-a)*ma+(-2*u**3+3*u*u)*vb+(u**3-u*u)*(b-a)*mb
    return -.25
records=[]
boots=bpy.data.objects['Black duty boots']
floor=-.0265
bpy.context.view_layer.update()
ev=boots.evaluated_get(bpy.context.evaluated_depsgraph_get()); mesh=ev.to_mesh()
boot_local={}
for side,suffix in ((1,'l'),(-1,'r')):
    inverse=rig.data.bones[f'foot_{suffix}'].matrix_local.inverted()
    boot_local[suffix]=[inverse @ (boots.matrix_world @ v.co) for v in mesh.vertices if v.co.x*side>0]
ev.to_mesh_clear()
for frame in range(1,FRAMES+2):
    scene.frame_set(frame)
    phase=(frame-1)/FRAMES; rig.location=(0,0,0)
    for p in rig.pose.bones: p.matrix_basis=Matrix.Identity(4)
    hip_height=.915-.024*math.cos(4*math.pi*(phase-.10))
    pelvis=rig.data.bones['pelvis']
    rotation=Quaternion((0,0,1),radians(3)*math.sin(2*math.pi*phase)) @ Quaternion((1,0,0),radians(3))
    head=pelvis.head_local+Vector((.006*math.cos(2*math.pi*phase),0,hip_height-.962))
    rig.pose.bones['pelvis'].matrix=Matrix.Translation(head) @ (rotation @ pelvis.matrix_local.to_quaternion()).to_matrix().to_4x4()
    for name,angle in [('spine_01',2),('spine_02',2),('spine_03',2),('neck_01',-2),('head',-2)]:
        local_world_rotation(name,(1,0,0),radians(angle))
    rest=rig.data.bones['spine_03'].matrix_local.to_quaternion()
    rig.pose.bones['spine_03'].rotation_quaternion=rest.inverted() @ (Quaternion((0,0,1),-radians(6)*math.sin(2*math.pi*phase)) @ Quaternion((1,0,0),radians(2))) @ rest
    bpy.context.view_layer.update()
    planned_lifts=[]; leg_targets={}
    for side,suffix in ((1,'l'),(-1,'r')):
        t=(phase+(0 if side==1 else .5))%1
        thigh=rig.data.bones[f'thigh_{suffix}']; calf=rig.data.bones[f'calf_{suffix}']
        hip=rig.pose.bones[thigh.name].head.copy()
        foot=rig.data.bones[f'foot_{suffix}']
        q=Quaternion((1,0,0),radians(smooth_profile(t,foot_pitch))) @ foot.matrix_local.to_quaternion()
        ground_ankle=floor-min((q @ v).z for v in boot_local[suffix])
        lift=.40*math.sin(math.pi*(t-.30)/.70)**2 if t>.30 else 0
        planned_lifts.append(lift)
        ankle=Vector((side*.105,foot_forward(t),ground_ankle+lift))
        knee,ankle=two_bone(hip,ankle,thigh.length,calf.length)
        orient(thigh.name,hip,knee-hip); bpy.context.view_layer.update()
        orient(calf.name,knee,ankle-knee); bpy.context.view_layer.update()
        rig.pose.bones[foot.name].matrix=Matrix.Translation(ankle) @ q.to_matrix().to_4x4()
        leg_targets[suffix]=(hip.copy(),ankle.copy(),q.copy(),lift)
        bpy.context.view_layer.update()
        upper=rig.data.bones[f'upperarm_{suffix}']; lower=rig.data.bones[f'lowerarm_{suffix}']
        shoulder=rig.pose.bones[upper.name].head.copy()
        angle=.65*math.cos(2*math.pi*t)
        upper_dir=Vector((side*.08,math.sin(angle),-math.cos(angle))).normalized()
        elbow=shoulder+upper_dir*upper.length
        elbow_flex=radians(85-12*math.cos(2*math.pi*t)+5*math.sin(2*math.pi*t))
        lower_angle=angle-elbow_flex
        lower_dir=Vector((side*.08,math.sin(lower_angle),-math.cos(lower_angle))).normalized()
        wrist=elbow+lower_dir*lower.length
        orient(upper.name,shoulder,elbow-shoulder); bpy.context.view_layer.update()
        orient(lower.name,elbow,wrist-elbow); bpy.context.view_layer.update()
        hand=rig.data.bones[f'hand_{suffix}']
        # Anatomical hand frame: wrist-to-middle knuckle follows the forearm;
        # pinky-to-index points toward the thumb. Shortest-arc bone aiming alone
        # leaves this roll unconstrained and produces palm-down, dangling fists.
        forward=(rig.data.bones[f'middle_01_{suffix}'].head_local-hand.head_local).normalized()
        radial=rig.data.bones[f'index_01_{suffix}'].head_local-rig.data.bones[f'pinky_01_{suffix}'].head_local
        radial=(radial-forward*radial.dot(forward)).normalized()
        rest_frame=Matrix((radial,forward,radial.cross(forward))).transposed()
        hand_forward=Quaternion((1,0,0),radians(2)*math.sin(2*math.pi*t-.35)) @ lower_dir
        thumb_up=Vector((-side*.12,0,1))
        thumb_up=(thumb_up-hand_forward*thumb_up.dot(hand_forward)).normalized()
        target_frame=Matrix((thumb_up,hand_forward,thumb_up.cross(hand_forward))).transposed()
        delta=(target_frame @ rest_frame.transposed()).to_quaternion()
        rig.pose.bones[hand.name].matrix=Matrix.Translation(wrist) @ (delta @ hand.matrix_local.to_quaternion()).to_matrix().to_4x4()
        for digit in ('index','middle','ring','pinky'):
            for joint,angle in ((1,35),(2,55),(3,25)):
                rig.pose.bones[f'{digit}_{joint:02d}_{suffix}'].rotation_quaternion=Quaternion((1,0,0),radians(angle))
        for joint,angle in ((1,12),(2,20),(3,15)):
            rig.pose.bones[f'thumb_{joint:02d}_{suffix}'].rotation_quaternion=Quaternion((1,0,0),radians(angle))
    bpy.context.view_layer.update()
    # Correct the small skinned-sole offset by re-solving each leg, never by
    # translating the pelvis/head/hands. The correction converges continuously.
    for _ in range(3):
        ev=boots.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=ev.to_mesh()
        world=[boots.matrix_world @ v.co for v in me.vertices]
        actual={s:min(v.z for v in world if v.x*side>0) for side,s in ((1,'l'),(-1,'r'))}; ev.to_mesh_clear()
        for suffix in ('l','r'):
            hip,ankle,q,lift=leg_targets[suffix]
            ankle.z+=floor+lift-actual[suffix]
            thigh=rig.data.bones[f'thigh_{suffix}']; calf=rig.data.bones[f'calf_{suffix}']
            knee,ankle=two_bone(hip,ankle,thigh.length,calf.length)
            orient(thigh.name,hip,knee-hip); bpy.context.view_layer.update()
            orient(calf.name,knee,ankle-knee); bpy.context.view_layer.update()
            rig.pose.bones[f'foot_{suffix}'].matrix=Matrix.Translation(ankle) @ q.to_matrix().to_4x4()
            leg_targets[suffix]=(hip,ankle,q,lift)
        bpy.context.view_layer.update()
    clearance=min(planned_lifts)
    for p in rig.pose.bones:
        p.keyframe_insert('location',frame=frame); p.keyframe_insert('rotation_quaternion',frame=frame); p.keyframe_insert('scale',frame=frame)
    rig.keyframe_insert('location',frame=frame)
    bpy.context.view_layer.update()
    records.append({'frame':frame,'phase':phase,'root_z':rig.location.z,'sole_clearance':max(0,clearance),'ankles':{s:list(rig.pose.bones[f'foot_{s}'].head+rig.location) for s in ('l','r')}})

scene.frame_start=1; scene.frame_end=FRAMES; scene.render.fps=FPS
scene.render.engine='CYCLES'; scene.cycles.samples=8; scene.cycles.use_denoising=True
scene.render.resolution_x=480; scene.render.resolution_y=600; scene.render.resolution_percentage=100
scene.frame_set(1)
bpy.ops.file.pack_all(); bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'officer_v2_run_preview.blend'))
(OUT/'motion.json').write_text(json.dumps({'fps':FPS,'frames':FRAMES,'duration_s':.8,'neutral_source_sha256':SOURCE_HASH,'attachments':attachments,'poses':records},indent=2))
if '--bake-only' in sys.argv:
    print('RUN_BAKED_WITHOUT_RENDER',flush=True)
    raise SystemExit(0)
cam=scene.camera
check='--check' in sys.argv
frames=[1,11,21,31] if check else list(range(1,FRAMES+1))
views=[('three_quarter',(3,-6,2.5),(0,0,.94),2.15)] if check else [('side',(6,0,1.8),(0,0,.94),2.15),('three_quarter',(3,-6,2.5),(0,0,.94),2.15)]
for view,loc,target,scale in views:
    cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=scale
    for frame in frames:
        scene.frame_set(frame); scene.render.filepath=str(OUT/f'{view}_{frame:02d}.png'); bpy.ops.render.render(write_still=True)
print('RUN_PREVIEW_RENDERED',flush=True)
