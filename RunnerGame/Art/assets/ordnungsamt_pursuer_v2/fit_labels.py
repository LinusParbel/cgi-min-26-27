"""Fit woven labels against the final evaluated garment, after parenting updates."""
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def refit_labels():
    bpy.context.view_layer.update()
    tree=BVHTree.FromObject(bpy.data.objects['Service jacket and trousers'],bpy.context.evaluated_depsgraph_get())
    for name,back,clearance in [('Back identification backing',True,.006),('Chest identification backing',False,.006)]:
        ob=bpy.data.objects[name]
        for vertex in ob.data.vertices:
            w=ob.matrix_world @ vertex.co
            p,_,_,_=tree.ray_cast(Vector((w.x,1 if back else -1,w.z)),Vector((0,-1 if back else 1,0)))
            assert p is not None
            w.y=p.y+(clearance if back else -clearance)
            vertex.co=ob.matrix_world.inverted() @ w
        ob.data.update()
    bpy.context.view_layer.update()

if __name__=='__main__':
    here=Path(__file__).resolve().parent
    bpy.ops.wm.open_mainfile(filepath=str(here/'officer_v2.blend'))
    refit_labels()
    bpy.ops.wm.save_as_mainfile(filepath=str(here/'officer_v2.blend'))
    scene=bpy.context.scene; cam=scene.camera
    for name,loc,target in [('three_quarter',(3,-6,2.5),(0,0,.91)),('back',(-2,6,2.4),(0,0,.91)),('front',(0,-6,1.7),(0,0,.91))]:
        cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=2.05
        scene.render.filepath=str(here/'previews'/f'{name}.png'); bpy.ops.render.render(write_still=True)
    cam.location=(3,-6,2.5); cam.rotation_euler=(Vector((0,0,.91))-cam.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.wm.save_as_mainfile(filepath=str(here/'officer_v2.blend'))
