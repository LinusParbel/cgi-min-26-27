"""Extract per-frame positions and joint changes from the actual saved rig."""
from pathlib import Path
import bpy,json,math
from mathutils import Vector
here=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(here/'officer_v2_run_preview.blend'))
rig=bpy.data.objects['Human.rig']; rows=[]
count=bpy.context.scene.frame_end; fps=bpy.context.scene.render.fps
names=['pelvis','head','upperarm_l','lowerarm_l','hand_l','thigh_l','calf_l','foot_l','upperarm_r','lowerarm_r','hand_r','thigh_r','calf_r','foot_r']
for f in range(1,count+1):
    bpy.context.scene.frame_set(f); bpy.context.view_layer.update()
    points={n:list(rig.matrix_world @ rig.pose.bones[n].head) for n in names}
    angles={}
    for s in ('l','r'):
        for kind,a,b in [('knee','thigh','calf'),('elbow','upperarm','lowerarm')]:
            p=rig.pose.bones[f'{a}_{s}']; q=rig.pose.bones[f'{b}_{s}']
            angles[f'{kind}_{s}']=math.degrees((p.tail-p.head).angle(q.tail-q.head))
    rows.append({'frame':f,'root_z':rig.location.z,'points':points,'angles':angles})
summary={}
for name in ('pelvis','hand_l','hand_r','foot_l','foot_r'):
    pts=[Vector(r['points'][name]) for r in rows]
    steps=[(pts[(i+1)%count]-pts[i]).length for i in range(count)]
    accel=[(pts[(i+1)%count]-pts[i]*2+pts[(i-1)%count]).length for i in range(count)]
    summary[name]={'step_m':steps,'second_difference_m':accel}
summary['knee_deg']=[round(r['angles']['knee_l'],1) for r in rows]
summary['root_z']=[round(r['root_z'],4) for r in rows]
summary['stance_foot_velocity_m_s']=[(rows[i+1]['points']['foot_l'][1]-rows[i]['points']['foot_l'][1])*fps for i in range(count) if (i+1)/count<=.30]
(here/'previews/run/motion_analysis.json').write_text(json.dumps({'rows':rows,'summary':summary},indent=2))
print(json.dumps({'frames':count,'fps':fps,'peak_acceleration_m_s2':{name:max(summary[name]['second_difference_m'])*fps*fps for name in ('pelvis','hand_l','hand_r','foot_l','foot_r')},'knee_range_degrees':[min(summary['knee_deg']),max(summary['knee_deg'])],'stance_speed_range_m_s':[min(summary['stance_foot_velocity_m_s']),max(summary['stance_foot_velocity_m_s'])]}),flush=True)
