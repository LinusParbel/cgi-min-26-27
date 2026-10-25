"""Reproducible MakeHuman officer anatomy and wardrobe preview (Blender 5.2)."""
from pathlib import Path
import sys, json, math
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RESEARCH = ROOT / '.model-research'
# Reuse the tested workspace-local MPFB bootstrap, without generating its test body.
bootstrap = (RESEARCH / 'inspect_human.py').read_text().split('bpy.ops.object.select_all')[0]
exec(compile(bootstrap, str(RESEARCH / 'inspect_human.py'), 'exec'), {'__file__': str(RESEARCH / 'inspect_human.py')})
from mpfb.services.humanservice import HumanService
from mpfb.services.targetservice import TargetService

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
macro = TargetService.get_default_macro_info_dict()
macro.update(gender=1., age=.58, muscle=.48, weight=.62, height=.57)
body = HumanService.create_human(macro_detail_dict=macro)
assets = RESEARCH / 'system-assets'
HumanService.set_character_skin(str(assets/'skins/middleage_caucasian_male/middleage_caucasian_male.mhmat'), body, skin_type='GAMEENGINE')
HumanService.add_builtin_rig(body, 'game_engine')

def fit(rel, kind):
    before = set(bpy.data.objects)
    HumanService.add_mhclo_asset(str(assets/rel), body, asset_type=kind, material_type='GAMEENGINE', subdiv_levels=1)
    return next(o for o in set(bpy.data.objects)-before if o.type=='MESH')

uniform = fit('clothes/male_casualsuit01/male_casualsuit01.mhclo', 'Clothes')
shoes = fit('clothes/shoes04/shoes04.mhclo', 'Clothes')
eyes = fit('eyes/low-poly/low-poly.mhclo', 'Eyes')
hair = fit('hair/short04/short04.mhclo', 'Hair')
fit('eyebrows/eyebrow001/eyebrow001.mhclo', 'Eyebrows')
fit('teeth/teeth_base/teeth_base.mhclo', 'Teeth')

def material(name, color, roughness=.65):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=roughness
    return m
navy=material('Service navy wool',(.018,.031,.060))
shirt=material('Pale blue uniform shirt',(.23,.40,.59))
black=material('Black duty leather',(.012,.015,.020),.37)
dark=material('Dark brown hair',(.025,.018,.014))
white=material('Silver white embroidery',(.72,.78,.83))
uniform.data.materials.clear(); uniform.data.materials.append(navy); uniform.data.materials.append(shirt)
for p in uniform.data.polygons:
    z=sum((uniform.matrix_world @ uniform.data.vertices[i].co).z for i in p.vertices)/len(p.vertices)
    p.material_index=1 if z>1.00 else 0
shoes.data.materials.clear(); shoes.data.materials.append(black)
# The supplied shoes include sock uppers: tuck them beneath the trouser cuffs.
for v in shoes.data.vertices:
    if v.co.z>.14:
        side=1 if v.co.x>0 else -1
        v.co.x=side*.16+(v.co.x-side*.16)*.82
        v.co.y*=.82
hair.data.materials.clear(); hair.data.materials.append(dark)
hair_offset=hair.modifiers.new('Scalp clearance','DISPLACE'); hair_offset.strength=.005; hair_offset.mid_level=0
dark.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.92
dark.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.15
for o in (uniform,shoes,body):
    for p in o.data.polygons: p.use_smooth=True

def cube(name,loc,scale,mat,bevel=.008):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(mat)
    b=o.modifiers.new('Soft manufactured edges','BEVEL'); b.width=bevel; b.segments=3
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return o

# Accessories are preview fittings, positioned after the actual wardrobe is evaluated.
bpy.context.view_layer.update()
print('WARDROBE_BOUNDS',[(o.name,tuple(o.dimensions),tuple(o.location)) for o in (body,uniform,shoes)],flush=True)
cube('Shoulder radio',(-.17,-.135,1.40),(.062,.038,.095),black)
cube('Radio antenna',(-.19,-.13,1.478),(.007,.007,.075),black,.002)
cube('Chest name backing',(.125,-.169,1.365),(.13,.009,.028),navy,.003)
def text(name,word,loc,size,rotation):
    c=bpy.data.curves.new(name,'FONT'); c.body=word; c.align_x='CENTER'; c.size=size; c.extrude=.0003
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=rotation; c.materials.append(white)
text('Chest embroidery','ORDNUNGSAMT',(.125,-.176,1.362),.012,(math.pi/2,0,0))
text('Back embroidery','ORDNUNGSAMT',(0,.145,1.40),.032,(math.pi/2,0,math.pi))

# Small moustache follows the actual upper lip surface, rather than floating cylinders.
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
surface=BVHTree.FromObject(body,dg)
verts=[]; faces=[]
for i in range(25):
    x=-.027+i*.054/24
    center=1.636-.006*(abs(x)/.027)**1.4
    thickness=.0035*max(.15,1-(abs(x)/.029)**2)
    for z in (center-thickness,center+thickness):
        hit,normal,_,_=surface.ray_cast(Vector((x,-1,z)),Vector((0,1,0)))
        verts.append(tuple(hit+normal*.0015) if hit is not None else (x,-.16,z))
    if i: faces.append((2*i-2,2*i-1,2*i+1,2*i))
mesh=bpy.data.meshes.new('Fitted moustache'); mesh.from_pydata(verts,[],faces); mesh.update()
obj=bpy.data.objects.new('Short moustache',mesh); bpy.context.collection.objects.link(obj); mesh.materials.append(dark)

scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.samples=24
scene.render.resolution_x=850; scene.render.resolution_y=1050; scene.render.resolution_percentage=100
scene.world.color=(.22,.22,.22)
floor=material('Studio floor',(.12,.145,.18))
cube('Studio ground',(0,0,-.045),(200,200,.04),floor)
def aim(o,point): o.rotation_euler=(Vector(point)-o.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power,size in [('Key',(-3,-4,5),500,4),('Fill',(3,-2,3),350,3),('Rim',(1,3,4),550,3)]:
    d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.shape='DISK'; d.size=size
    o=bpy.data.objects.new(name,d); scene.collection.objects.link(o); o.location=loc; aim(o,(0,0,1))
d=bpy.data.cameras.new('Review camera'); cam=bpy.data.objects.new('Review camera',d); scene.collection.objects.link(cam); scene.camera=cam; d.type='ORTHO'
scene.view_settings.view_transform='AgX'
views=[('three_quarter',(3,-6,2.7),(0,0,.90),2.15),('back',(-2,6,2.5),(0,0,.90),2.15),('face',(1,-5,2.0),(0,-.02,1.58),.60),('hand',(1.5,-4,1.6),(.48,-.02,1.0),.50),('shoes',(2,-4,1.0),(0,-.04,.12),.80)]
for name,loc,target,scale in views:
    cam.location=loc; aim(cam,target); d.ortho_scale=scale
    scene.render.filepath=str(HERE/'previews'/f'{name}.png'); bpy.ops.render.render(write_still=True)
cam.location=views[0][1]; aim(cam,views[0][2]); d.ortho_scale=views[0][3]
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'officer_v2.blend'))
print('OFFICER_V2_SAVED',flush=True)
