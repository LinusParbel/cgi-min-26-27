"""Derive static running poses from the approved character prototype."""
import importlib.util
import math
import json
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('officer',ROOT/'build.py')
officer=importlib.util.module_from_spec(spec)
spec.loader.exec_module(officer)


def rotate(p,pivot,angle):
    pivot=Vector(pivot)
    return pivot+Matrix.Rotation(math.radians(angle),3,'X')@(p-pivot)


def direction(angle):
    a=math.radians(angle)
    return Vector((0,-math.sin(a),-math.cos(a)))


def limb(name,joints,radii,mat):
    """Dense rings with interpolated joint tangents prevent pinched rigid hinges."""
    centers=[]
    widths=[]
    for segment in range(2):
        for i in range(10):
            t=i/10
            centers.append(joints[segment].lerp(joints[segment+1],t))
            widths.append(radii[segment]*(1-t)+radii[segment+1]*t)
    centers.append(joints[-1]); widths.append(radii[-1])
    # Round the elbow/knee over several rings while leaving bone endpoints fixed.
    for _ in range(3):
        centers=[centers[0]]+[(centers[i-1]+centers[i]*2+centers[i+1])/4 for i in range(1,len(centers)-1)]+[centers[-1]]
    verts=[]
    sides=20
    for i,(c,r) in enumerate(zip(centers,widths)):
        tangent=(centers[min(i+1,len(centers)-1)]-centers[max(0,i-1)]).normalized()
        x=Vector((1,0,0))
        y=tangent.cross(x).normalized()
        for j in range(sides):
            a=j*math.tau/sides
            verts.append(c+x*(r*math.cos(a))+y*(r*.95*math.sin(a)))
    faces=[]
    for i in range(len(centers)-1):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            faces.append((a,b,b+sides,a+sides))
    faces += [tuple(reversed(range(sides))),tuple((len(centers)-1)*sides+j for j in range(sides))]
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces); mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    officer.finish(obj,name,mat)
    # Ring winding depends on the chain direction; ensure outward normals.
    import bmesh
    bm=bmesh.new(); bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(mesh); bm.free()
    return obj


# One leg's full cycle: landing, loading, toe-off, recovery, swing, extension.
# Degrees are art-directed, not motion-capture measurements.
KEYS=[(24,24,0),(4,29,0),(-19,25,-23),(-23,82,-28),
      (4,105,-15),(35,85,-7),(39,48,0),(31,29,0)]


def pose(objects,frame):
    source=list(objects)
    remove=('Trouser leg','Trouser knee','Jacket sleeve','Cuff')
    for o in source:
        if any(k in o.name for k in remove):
            objects.remove(o)
            bpy.data.objects.remove(o,do_unlink=True)
    skeleton={}
    for side in (-1,1):
        theta,bend,foot=KEYS[(frame+(4 if side==1 else 0))%8]
        hip=Vector((side*.125,0,.88))
        knee=hip+direction(theta)*.395
        ankle=knee+direction(theta-bend)*.385
        objects.append(limb('Posed trousers '+str(side),(hip,knee,ankle),(.116,.080,.063),bpy.data.materials['Service navy']))
        armtheta=-theta*.80
        shoulder=Vector((side*.275,0,1.375))
        elbow=shoulder+direction(armtheta)*.263
        elbow.x=side*.316
        wrist=elbow+direction(armtheta+82)*.235
        wrist.x=side*.324
        objects.append(limb('Posed sleeve '+str(side),(shoulder,elbow,wrist),(.096,.073,.061),bpy.data.materials['Service navy']))
        skeleton[str(side)]={'hip':list(hip),'knee':list(knee),'ankle':list(ankle),
            'thigh_length':(knee-hip).length,'shin_length':(ankle-knee).length,'foot_pitch':foot}
        for o in source:
            if o not in objects or o.type!='MESH':
                continue
            is_side=('-1' in o.name)==(side==-1)
            hand=any(k in o.name for k in ('Hand ','Thumb ')) and is_side
            if 'Finger crease' in o.name:
                hand=(o.location.x<0)==(side==-1)
            shoe=any(k in o.name for k in ('Boot sole','Boot upper')) and is_side
            if not(hand or shoe):
                continue
            origin=Vector((side*.35,-.016,.90)) if hand else Vector((side*.125,.012,.16))
            target=wrist if hand else ankle
            angle=armtheta+82 if hand else foot
            matrix=o.matrix_world.copy(); inverse=matrix.inverted()
            for v in o.data.vertices:
                # Foot orientation is independent from shin orientation.
                delta=matrix@v.co-origin
                if hand:
                    delta.z*=.82
                    delta=Matrix.Rotation(math.radians(-side*90),3,'Z')@delta
                v.co=inverse@(target+Matrix.Rotation(math.radians(-angle),3,'X')@delta)
    # Lean the torso, leaving the solved leg chains in world coordinates.
    excluded=('Posed trousers','Boot sole','Boot upper')
    lean=7
    for o in objects:
        if any(k in o.name for k in excluded):
            continue
        if o.type=='MESH':
            matrix=o.matrix_world.copy(); inverse=matrix.inverted()
            for v in o.data.vertices:
                v.co=inverse@rotate(matrix@v.co,(0,0,.88),lean)
        else:
            o.location=rotate(o.location,(0,0,.88),lean)
            o.rotation_euler=(Matrix.Rotation(math.radians(lean),3,'X')@o.rotation_euler.to_matrix()).to_euler()
    bpy.context.view_layer.update()
    # Ground the ACTUAL boot vertices, not a rotated bounding box.
    shoes=[o for o in objects if 'Boot ' in o.name]
    low=min((o.matrix_world@v.co).z for o in shoes for v in o.data.vertices)
    flight=.035 if frame%4==2 else 0
    for o in objects:
        o.location.z+=flight-low
    for chain in skeleton.values():
        assert abs(chain['thigh_length']-.395)<1e-5
        assert abs(chain['shin_length']-.385)<1e-5
    assert all(math.isfinite(v) for o in objects if o.type=='MESH' for p in o.data.vertices for v in p.co)
    (ROOT/'previews'/f'run_{frame+1}_joints.json').write_text(json.dumps(skeleton,indent=2))


def preview(index,phase):
    objects=officer.build()
    pose(objects,phase)
    scene=bpy.context.scene
    scene.render.engine='BLENDER_WORKBENCH'
    shade=scene.display.shading
    shade.light='STUDIO'
    shade.color_type='MATERIAL'
    shade.show_shadows=True
    shade.show_cavity=True
    shade.show_specular_highlight=False
    scene.world.color=(.11,.13,.16)
    scene.view_settings.view_transform='Standard'
    scene.render.resolution_x=600
    scene.render.resolution_y=720
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    camera=bpy.data.cameras.new('Running preview')
    camera.type='ORTHO'
    camera.ortho_scale=2.12
    cam=bpy.data.objects.new('Running preview',camera)
    scene.collection.objects.link(cam)
    scene.camera=cam
    for view,eye in [('side',(4,0,1.05)),('three_quarter',(3,-5,2.0))]:
        target=Vector((0,0,.89))
        cam.location=eye
        cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(ROOT/'previews'/f'run_{index}_{view}.png')
        bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/f'officer_run_{index}.blend'))
    print(f'POSE {index}: {len(objects)} components; grounded')


if __name__=='__main__':
    for i,phase in enumerate(range(8),1):
        preview(i,phase)
