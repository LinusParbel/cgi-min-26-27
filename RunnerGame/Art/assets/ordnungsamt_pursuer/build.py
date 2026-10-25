"""Original character prototype; run with Blender --background --python this_file."""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent


def material(name, rgb, roughness=0.65):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    node = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    node.inputs['Base Color'].default_value = (*rgb, 1)
    node.inputs['Roughness'].default_value = roughness
    return m


def finish(obj, name, mat, smooth=True):
    obj.name = name
    obj.data.materials.append(mat)
    if smooth and obj.type == 'MESH':
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj


def ellipsoid(name, loc, scale, mat, segments=24, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=loc)
    o = bpy.context.object
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, name, mat)


def box(name, loc, size, mat, bevel=0.008):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    finish(o, name, mat, False)
    if bevel:
        mod = o.modifiers.new('Soft edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o


def profile(name, sections, mat, sides=24):
    """Closed elliptical section surface: (cx,cy,z,halfwidth,halfdepth)."""
    verts = []
    for x, y, z, w, d in sections:
        verts.extend((x+w*math.cos(a*2*math.pi/sides), y+d*math.sin(a*2*math.pi/sides), z) for a in range(sides))
    faces = []
    for k in range(len(sections)-1):
        for j in range(sides):
            a=k*sides+j; b=k*sides+(j+1)%sides
            faces.append((a,b,b+sides,a+sides))
    faces.extend([tuple(reversed(range(sides))),tuple((len(sections)-1)*sides+j for j in range(sides))])
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    o=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(o)
    return finish(o,name,mat)


def patch(name, points, mat):
    mesh=bpy.data.meshes.new(name)
    order=tuple(range(len(points)))
    normal=(Vector(points[1])-Vector(points[0])).cross(Vector(points[2])-Vector(points[0]))
    if normal.y>0:
        order=tuple(reversed(order))
    mesh.from_pydata(points,[],[order])
    mesh.update()
    o=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(o)
    return finish(o,name,mat,False)


def text(name, body, loc, width, mat, rear=False):
    curve=bpy.data.curves.new(name,'FONT')
    curve.body=body
    curve.align_x='CENTER'
    curve.align_y='CENTER'
    curve.size=0.08
    curve.extrude=0.00015
    curve.resolution_u=3
    o=bpy.data.objects.new(name,curve)
    bpy.context.collection.objects.link(o)
    o.location=loc
    o.rotation_euler=(math.pi/2,0,math.pi if rear else 0)
    bpy.context.view_layer.update()
    o.scale *= width/o.dimensions.x
    curve.materials.append(mat)
    return o


def build():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    navy=material('Service navy',(0.018,0.030,0.060))
    trim=material('Navy raised seams',(0.030,0.046,0.078))
    shirt=material('Pale blue shirt',(0.34,0.52,0.68))
    black=material('Black leather',(0.012,0.014,0.018),0.42)
    sole=material('Rubber soles',(0.022,0.025,0.030))
    skin=material('Warm skin',(0.53,0.31,0.21),0.7)
    skinshade=material('Skin creases',(0.30,0.13,0.085))
    hair=material('Brown hair',(0.055,0.029,0.019))
    gray=material('Salt and pepper',(0.15,0.12,0.10))
    white=material('Lettering',(0.82,0.86,0.87))
    eyes=material('Eye whites',(0.65,0.68,0.65))
    iris=material('Iris',(0.065,0.09,0.085))
    metal=material('Equipment metal',(0.24,0.27,0.30),0.3)

    # Garment silhouette: broad shoulders, soft belly, tailored jacket hem.
    profile('Jacket',[(0,0,0.88,.235,.145),(0,0,0.94,.255,.17),(0,-.014,1.06,.267,.193),
        (0,-.008,1.18,.265,.187),(0,0,1.30,.267,.16),(0,0,1.39,.265,.14),
        (0,0,1.44,.22,.112),(0,0,1.465,.10,.085)],navy)
    profile('Trouser pelvis',[(0,0,.77,.205,.12),(0,0,.89,.235,.145),(0,0,.95,.23,.15)],navy)
    for side in (-1,1):
        x=side*.125
        profile('Trouser leg '+str(side),[(x,0,.13,.073,.074),(x,.004,.24,.075,.077),
            (x,.01,.42,.081,.089),(x,-.012,.51,.09,.10),(x,0,.68,.108,.113),(x,0,.84,.118,.12)],navy)
        box('Boot sole '+str(side),(x,-.042,.033),(.157,.293,.058),sole,.02)
        profile('Boot upper '+str(side),[(x,-.046,.05,.075,.14),(x,-.052,.085,.076,.142),
            (x,-.035,.12,.068,.115),(x,.008,.16,.061,.068),(x,.012,.21,.06,.063)],black)
        box('Trouser knee seam '+str(side),(x,-.104,.49),(.128,.006,.008),trim,.002)
        # Relaxed bent arms; later pose versions use articulated segment transforms.
        profile('Jacket sleeve '+str(side),[(side*.35,-.015,.91,.065,.07),(side*.355,.0,1.03,.074,.076),
            (side*.34,.01,1.15,.079,.082),(side*.315,0,1.30,.09,.095),(side*.255,0,1.40,.09,.095)],navy)
        profile('Cuff '+str(side),[(side*.351,-.016,.89,.065,.068),(side*.35,-.016,.94,.068,.072)],trim)
        ellipsoid('Hand '+str(side),(side*.352,-.018,.835),(.058,.043,.083),skin)
        ellipsoid('Thumb '+str(side),(side*.31,-.049,.86),(.026,.028,.047),skin,16,10)
        for i in range(3):
            box('Finger crease',(side*.354+(i-1)*.018,-.057,.81),(.002,.003,.026),skinshade,.001)
        box('Lower pocket '+str(side),(side*.15,-.174,1.01),(.135,.025,.105),trim,.008)
        box('Pocket flap '+str(side),(side*.15,-.19,1.05),(.14,.012,.027),navy,.004)
        box('Shoulder tab '+str(side),(side*.213,-.015,1.435),(.09,.105,.012),trim,.004)

    profile('Neck',[(0,0,1.42,.077,.074),(0,0,1.56,.079,.075)],skin)
    patch('Visible shirt',[(-.075,-.165,1.447),(.075,-.165,1.447),(.025,-.199,1.29),(-.025,-.199,1.29)],shirt)
    for side in (-1,1):
        patch('Shirt collar '+str(side),[(0,-.175,1.435),(side*.070,-.167,1.45),(side*.081,-.187,1.405),(side*.035,-.193,1.38)],shirt)
        patch('Jacket lapel '+str(side),[(side*.09,-.17,1.44),(side*.145,-.168,1.39),(side*.035,-.205,1.27),(side*.048,-.198,1.36)],trim)
    box('Jacket zipper',(0,-.204,1.13),(.008,.006,.24),metal,.001)
    box('Chest identification panel',(.124,-.169,1.292),(.18,.013,.045),black,.003)
    text('Chest ORDNUNGSAMT','ORDNUNGSAMT',(.124,-.178,1.294),.16,white)
    box('Back identification panel',(0,.166,1.316),(.385,.016,.078),black,.005)
    text('Back ORDNUNGSAMT','ORDNUNGSAMT',(0,.177,1.319),.35,white,True)
    box('Shoulder radio',(-.16,-.174,1.32),(.074,.043,.116),black,.008)
    for i in range(4):
        box('Radio grille',(-.16,-.198,1.33+i*.009),(.046,.004,.003),metal,.0005)
    box('Radio antenna',(-.181,-.176,1.425),(.009,.01,.10),black,.003)
    box('Duty belt',(0,0,.925),(.47,.303,.047),black,.009)
    box('Belt buckle',(0,-.158,.926),(.064,.014,.037),metal,.003)
    box('Equipment pouch',(.244,.008,.875),(.068,.10,.12),black,.012)

    # Shaped skull with jaw, cheeks and brow, instead of a spherical head.
    profile('Head',[(0,-.008,1.49,.052,.052),(0,-.017,1.515,.077,.075),
        (0,-.01,1.55,.098,.087),(0,0,1.60,.113,.102),(0,.006,1.66,.11,.104),
        (0,.012,1.72,.103,.098),(0,.016,1.765,.078,.075),(0,.016,1.785,.025,.027)],skin,32)
    for side in (-1,1):
        ellipsoid('Ear '+str(side),(side*.114,.008,1.63),(.023,.023,.041),skin,16,12)
        ellipsoid('Ear inner '+str(side),(side*.128,-.006,1.63),(.009,.013,.022),skinshade,12,8)
        ellipsoid('Cheek '+str(side),(side*.059,-.069,1.589),(.043,.021,.032),skin,20,12)
        ellipsoid('Eye '+str(side),(side*.046,-.092,1.652),(.023,.007,.009),eyes,20,12)
        ellipsoid('Iris '+str(side),(side*.045,-.099,1.652),(.006,.002,.007),iris,16,10)
        brow=ellipsoid('Determined eyebrow '+str(side),(side*.049,-.103,1.68),(.038,.010,.010),hair,16,10)
        brow.rotation_euler.y=-side*.20
        ellipsoid('Temple hair '+str(side),(side*.099,.024,1.69),(.012,.064,.058),hair,16,12)
        ellipsoid('Gray sideburn '+str(side),(side*.106,-.015,1.652),(.008,.022,.028),gray,12,8)
        m=ellipsoid('Moustache '+str(side),(side*.026,-.112,1.586),(.034,.014,.012),hair,20,12)
        m.rotation_euler.y=side*.14
    ellipsoid('Nose bridge',(0,-.104,1.632),(.019,.026,.035),skin,20,14)
    ellipsoid('Nose tip',(0,-.127,1.612),(.027,.024,.019),skin,20,12)
    ellipsoid('Lower lip',(0,-.100,1.561),(.032,.009,.006),skinshade,16,8)
    ellipsoid('Chin',(0,-.073,1.534),(.052,.027,.021),skin,20,12)
    profile('Short hair cap',[(0,.018,1.702,.107,.098),(0,.018,1.73,.104,.098),(0,.018,1.755,.092,.087),
        (0,.018,1.78,.067,.063),(0,.018,1.795,.015,.016)],hair,32)
    # A swept fringe gives a readable hairline without a cap.
    fringe=ellipsoid('Swept fringe',(-.019,-.057,1.748),(.083,.037,.026),hair,24,12)
    fringe.rotation_euler.y=-.12
    return [o for o in bpy.context.scene.objects if o.type in {'MESH','FONT'}]


def render_preview(objects):
    scene=bpy.context.scene
    # Workbench provides fast, repeatable garment and silhouette previews.
    scene.render.engine='BLENDER_WORKBENCH'
    shade=scene.display.shading
    shade.light='STUDIO'
    shade.color_type='MATERIAL'
    shade.show_shadows=True
    shade.show_specular_highlight=False
    shade.show_cavity=True
    shade.cavity_type='BOTH'
    shade.curvature_ridge_factor=1.1
    shade.curvature_valley_factor=1.0
    shade.background_type='WORLD'
    scene.world.color=(.11,.13,.16)
    scene.view_settings.view_transform='Standard'
    scene.render.resolution_x=600
    scene.render.resolution_y=720
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    data=bpy.data.cameras.new('Preview camera')
    cam=bpy.data.objects.new('Preview camera',data)
    scene.collection.objects.link(cam)
    scene.camera=cam
    data.type='ORTHO'
    out=ROOT/'previews'
    out.mkdir(exist_ok=True)
    views=[('front',(0,-4,1.5),(0,0,.91),2.05),
           ('three_quarter',(3,-5,2.6),(0,0,.91),2.05),
           ('back',(0,4,1.6),(0,0,.91),2.05),
           ('face',(1,-4,1.95),(0,-.015,1.63),.43)]
    for name,eye,target,scale in views:
        cam.location=eye
        cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
        data.ortho_scale=scale
        scene.render.filepath=str(out/(name+'.png'))
        bpy.ops.render.render(write_still=True)
    cam.location=(3,-5,2.6)
    cam.rotation_euler=(Vector((0,0,.91))-cam.location).to_track_quat('-Z','Y').to_euler()
    data.ortho_scale=2.05


def validate(objects):
    bpy.context.view_layer.update()
    pts=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
    lo=[min(p[i] for p in pts) for i in range(3)]
    hi=[max(p[i] for p in pts) for i in range(3)]
    assert all(math.isfinite(v) for p in pts for v in p)
    assert abs(lo[2])<.01, f'Feet not grounded: {lo}'
    assert 1.75<hi[2]<1.85, f'Unexpected height: {hi}'
    tris=0
    deps=bpy.context.evaluated_depsgraph_get()
    for o in objects:
        evaluated=o.evaluated_get(deps)
        mesh=evaluated.to_mesh()
        mesh.calc_loop_triangles()
        tris+=len(mesh.loop_triangles)
        evaluated.to_mesh_clear()
    result={'stage':'neutral-pose visual prototype','triangles':tris,'bounds_min':lo,'bounds_max':hi,
            'height_m':hi[2]-lo[2],'uniform':'Hannover-inspired artistic approximation',
            'runtime_ready':False,'notes':'Preview geometry is not yet reduced to final game triangle budget.'}
    (ROOT/'previews'/'validation.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result))


if __name__=='__main__':
    objects=build()
    (ROOT/'previews').mkdir(exist_ok=True)
    validate(objects)
    render_preview(objects)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'officer_preview.blend'))
