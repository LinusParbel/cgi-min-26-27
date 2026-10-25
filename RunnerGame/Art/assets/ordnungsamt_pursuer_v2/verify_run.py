"""Inspect the saved animation, actual boot soles, equipment parenting and seam."""
from pathlib import Path
import bpy, json, math
from mathutils import Matrix

here=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(here/'officer_v2_run_preview.blend'))
scene=bpy.context.scene; rig=bpy.data.objects['Human.rig']; boots=bpy.data.objects['Black duty boots']
motion=json.loads((here/'previews/run/motion.json').read_text())
floor=-.0265; checks=[]; first=None; attachment_reference={}; count=motion['frames']
sample=['Vest front shell','Vest back shell','Vest shoulder radio microphone','Duty trouser cargo pocket -1','Boot lace -1 A0','Moustache hair 1']
for frame in range(1,count+2):
    scene.frame_set(frame); bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get(); ev=boots.evaluated_get(dg); me=ev.to_mesh()
    sole=min((boots.matrix_world @ v.co).z for v in me.vertices); ev.to_mesh_clear()
    expected=motion['poses'][frame-1]['sole_clearance']
    assert abs(sole-floor-expected)<.001, (frame,sole,floor,expected)
    for p in rig.pose.bones:
        assert all(math.isfinite(x) for row in p.matrix for x in row)
        assert abs(p.length-rig.data.bones[p.name].length)<.0001,(frame,p.name,p.length)
    for suffix in ('l','r'):
        a=rig.pose.bones[f'thigh_{suffix}']; b=rig.pose.bones[f'calf_{suffix}']
        bend=math.degrees((a.tail-a.head).angle(b.tail-b.head))
        assert bend>12,('Knee nears straight IK singularity',frame,suffix,bend)
    for name in sample:
        ob=bpy.data.objects[name]; assert ob.parent_type=='BONE' and ob.parent==rig
        bone_world=rig.matrix_world @ rig.pose.bones[ob.parent_bone].matrix
        relative=bone_world.inverted() @ ob.matrix_world
        if frame==1: attachment_reference[name]=relative.copy()
        else: assert max(abs(relative[i][j]-attachment_reference[name][i][j]) for i in range(4) for j in range(4))<.00001,(frame,name)
    matrices={p.name:rig.matrix_world @ p.matrix for p in rig.pose.bones}
    if frame==1: first=matrices
    if frame==count+1:
        seam=max(abs(matrices[name][i][j]-first[name][i][j]) for name in matrices for i in range(4) for j in range(4))
        assert seam<.00001,seam
    checks.append({'frame':frame,'actual_sole_z':sole,'expected_clearance':expected})
report={'frames':count,'duration_s':.8,'sole_contact_tolerance_m':.001,'loop_seam_matrix_error':seam,'rigid_attachment_samples':sample,'bone_lengths_preserved':True,'foot_checks':checks}
(here/'previews/run/rig_validation.json').write_text(json.dumps(report,indent=2))
print('RUN_VERIFIED',json.dumps({k:v for k,v in report.items() if k!='foot_checks'}),flush=True)
