"""Check anatomical wrist alignment and thumb-side roll over the complete run."""
from pathlib import Path
import bpy, math, json
from mathutils import Vector
here=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(here/'officer_v2_run_preview.blend'))
rig=bpy.data.objects['Human.rig']; scene=bpy.context.scene
max_wrist=0; min_thumb=1
for frame in range(1,scene.frame_end+2):
    scene.frame_set(frame); bpy.context.view_layer.update()
    for suffix in ('l','r'):
        hand=rig.pose.bones[f'hand_{suffix}']; lower=rig.pose.bones[f'lowerarm_{suffix}']
        forward=(rig.pose.bones[f'middle_01_{suffix}'].head-hand.head).normalized()
        forearm=(lower.tail-lower.head).normalized()
        angle=math.degrees(forward.angle(forearm)); max_wrist=max(max_wrist,angle)
        radial=rig.pose.bones[f'index_01_{suffix}'].head-rig.pose.bones[f'pinky_01_{suffix}'].head
        radial=(radial-forward*radial.dot(forward)).normalized()
        up=Vector((0,0,1)); up=(up-forward*up.dot(forward)).normalized()
        alignment=radial.dot(up); min_thumb=min(min_thumb,alignment)
        assert angle<5, ('Bent wrist',frame,suffix,angle)
        assert alignment>.94, ('Palm-down fist',frame,suffix,alignment)
report={'maximum_wrist_angle_degrees':max_wrist,'minimum_thumb_up_alignment':min_thumb,'frames_checked':scene.frame_end+1}
(here/'previews/run/hand_validation.json').write_text(json.dumps(report,indent=2))
print('HANDS_VERIFIED',json.dumps(report))
