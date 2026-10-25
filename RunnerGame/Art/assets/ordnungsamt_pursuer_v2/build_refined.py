"""Reference-led Hannover uniform preview. Blender 5.2; -- --draft for iterations."""
from pathlib import Path
import sys, math, random
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]; RESEARCH=ROOT/'.model-research'
DRAFT='--draft' in sys.argv
OUT=HERE/'previews'; OUT.mkdir(exist_ok=True)
bootstrap=(RESEARCH/'inspect_human.py').read_text().split('bpy.ops.object.select_all')[0]
exec(compile(bootstrap,str(RESEARCH/'inspect_human.py'),'exec'),{'__file__':str(RESEARCH/'inspect_human.py')})
from mpfb.services.humanservice import HumanService
from mpfb.services.targetservice import TargetService
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
macro=TargetService.get_default_macro_info_dict()
macro.update(gender=1.,age=.63,muscle=.5,weight=.62,height=.57)
body=HumanService.create_human(macro_detail_dict=macro)
targets=RESEARCH/'mpfb2-2.0.18/src/mpfb/data/targets'
for path,weight in [('head/head-age-incr',.33),('chin/chin-width-incr',.17),('chin/chin-bones-incr',.15),('cheek/l-cheek-volume-incr',.10),('cheek/r-cheek-volume-incr',.10),('eyebrows/eyebrows-angle-down',.10)]:
    TargetService.load_target(body,str(targets/(path+'.target.gz')),weight=weight)
assets=RESEARCH/'system-assets'
HumanService.set_character_skin(str(assets/'skins/middleage_caucasian_male/middleage_caucasian_male.mhmat'),body,skin_type='GAMEENGINE')
HumanService.add_builtin_rig(body,'game_engine')
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
def fit(rel,kind):
    before=set(bpy.data.objects)
    HumanService.add_mhclo_asset(str(assets/rel),body,asset_type=kind,material_type='GAMEENGINE',subdiv_levels=1)
    return next(o for o in set(bpy.data.objects)-before if o.type=='MESH')
uniform=fit('clothes/male_casualsuit01/male_casualsuit01.mhclo','Clothes'); uniform.name='Service jacket and trousers'
shoes=fit('clothes/shoes03/shoes03.mhclo','Clothes'); shoes.name='Black duty boots'
eyes=fit('eyes/low-poly/low-poly.mhclo','Eyes')
hair=fit('hair/short01/short01.mhclo','Hair')
fit('eyebrows/eyebrow001/eyebrow001.mhclo','Eyebrows')
fit('teeth/teeth_base/teeth_base.mhclo','Teeth')
def material(name,color,rough=.65):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough
    return m
navy=material('Navy service fabric',(.009,.016,.032),.83)
trousers=material('Navy trouser twill',(.009,.015,.027),.88)
panel=material('Navy reinforcement panels',(.008,.013,.024),.78)
blue=material('Pale blue shirt collar',(.19,.31,.43),.85)
black=material('Black leather',(.009,.011,.014),.58)
rubber=material('Rubber sole',(.006,.007,.009),.94)
nylon=material('Black woven webbing',(.007,.009,.012),.86)
lace=material('Black braided boot laces',(.018,.021,.026),.86)
metal=material('Dark hardware',(.055,.065,.075),.35)
white=material('White embroidered thread',(.72,.76,.79),.9)
gold=material('Sleeve shield border',(.50,.36,.12),.7)
red=material('Sleeve shield red',(.38,.018,.022),.8)
grayhair=material('Brown grey facial hair',(.045,.035,.027),.85)
crease=material('Subtle skin creases',(.36,.245,.20),.8)
for mat in body.data.materials:
    if not mat.use_nodes: continue
    nodes=mat.node_tree.nodes; links=mat.node_tree.links
    p=next((n for n in nodes if n.type=='BSDF_PRINCIPLED'),None)
    if p:
        p.inputs['Roughness'].default_value=.62
        noise=nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=240; noise.inputs['Detail'].default_value=3
        bump=nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.18; bump.inputs['Distance'].default_value=.00018
        links.new(noise.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],p.inputs['Normal'])
for mat in (navy,trousers,panel,nylon):
    nodes=mat.node_tree.nodes; links=mat.node_tree.links; p=nodes.get('Principled BSDF')
    p.inputs['Specular IOR Level'].default_value=.18
    tex=nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=420
    bump=nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.13; bump.inputs['Distance'].default_value=.0002
    links.new(tex.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],p.inputs['Normal'])
uniform.data.materials.clear()
for m in (navy,trousers,blue): uniform.data.materials.append(m)
for p in uniform.data.polygons:
    z=sum(uniform.data.vertices[i].co.z for i in p.vertices)/len(p.vertices)
    p.material_index=0 if z>1.055 else 1
shoes.data.materials.clear(); shoes.data.materials.append(black); shoes.data.materials.append(rubber)
for v in shoes.data.vertices:
    if v.co.z>.115:
        center=.20 if v.co.x>0 else -.20
        blend=min(1,(v.co.z-.115)/.035)
        factor=1-.22*blend
        v.co.x=center+(v.co.x-center)*factor
        v.co.y=-.005+(v.co.y+.005)*factor
for p in shoes.data.polygons:
    z=sum(shoes.data.vertices[i].co.z for i in p.vertices)/len(p.vertices)
    p.material_index=0
# A continuous height mask gives the rubber sole a clean edge across mesh faces.
nodes=black.node_tree.nodes; links=black.node_tree.links; bs=nodes.get('Principled BSDF')
geo=nodes.new('ShaderNodeNewGeometry'); sep=nodes.new('ShaderNodeSeparateXYZ')
links.new(geo.outputs['Position'],sep.inputs[0])
mask=nodes.new('ShaderNodeMath'); mask.operation='LESS_THAN'; mask.inputs[1].default_value=.014
links.new(sep.outputs['Z'],mask.inputs[0])
mix=nodes.new('ShaderNodeMixRGB'); mix.inputs[1].default_value=(.009,.011,.014,1); mix.inputs[2].default_value=(.004,.005,.006,1)
links.new(mask.outputs[0],mix.inputs[0]); links.new(mix.outputs[0],bs.inputs['Base Color'])
rough=nodes.new('ShaderNodeMapRange'); rough.inputs['To Min'].default_value=.58; rough.inputs['To Max'].default_value=.94
links.new(mask.outputs[0],rough.inputs['Value']); links.new(rough.outputs['Result'],bs.inputs['Roughness'])
for o in (body,uniform,shoes):
    for p in o.data.polygons: p.use_smooth=True
for mat in hair.data.materials:
    p=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); p.inputs['Roughness'].default_value=.88; p.inputs['Specular IOR Level'].default_value=.18
offset=hair.modifiers.new('Scalp clearance','DISPLACE'); offset.strength=.0025; offset.mid_level=0
def mesh_object(name,verts,faces,mat):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update()
    ob=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(ob); me.materials.append(mat); return ob
def cube(name,loc,scale,mat,bevel=.004):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(mat)
    b=o.modifiers.new('Soft edges','BEVEL'); b.width=bevel; b.segments=3
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return o
def tube(name,points,radius,mat):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.resolution_u=1; c.bevel_depth=radius; c.bevel_resolution=2
    s=c.splines.new('POLY'); s.points.add(len(points)-1)
    for p,co in zip(s.points,points): p.co=(*co,1)
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); c.materials.append(mat); return o
def uvball(name,loc,scale,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=1,location=loc); o=bpy.context.object; o.name=name; o.scale=scale; o.data.materials.append(mat)
    for p in o.data.polygons: p.use_smooth=True
    return o
def bvh(ob):
    bpy.context.view_layer.update(); return BVHTree.FromObject(ob,bpy.context.evaluated_depsgraph_get())
cloth=bvh(uniform); skin=bvh(body); boot=bvh(shoes)
clothing_masks=[m for m in body.modifiers if m.type=='MASK' and m.name.startswith('Delete.')]
for m in clothing_masks: m.show_viewport=False
unmasked_skin=bvh(body)
for m in clothing_masks: m.show_viewport=True
bpy.context.view_layer.update()
if '--inspect-fit' in sys.argv:
    for ob in (body,uniform,shoes):
        ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=ev.to_mesh()
        print('FIT_BOUNDS',ob.name,[[min(v.co[i] for v in me.vertices),max(v.co[i] for v in me.vertices)] for i in range(3)],flush=True)
        if ob==shoes:
            for z in (.05,.08,.10,.12,.15,.18,.21):
                vs=[v.co for v in me.vertices if abs(v.co.z-z)<.012 and v.co.x<0]
                print('BOOT_ROW',z,[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)] if vs else None,flush=True)
        ev.to_mesh_clear()
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'checkpoints/fitted_parts.blend'))
    raise SystemExit(0)
def hit(tree,x,z,back=False,offset=.002):
    pos,n,_,_=tree.ray_cast(Vector((x,1 if back else -1,z)),Vector((0,-1 if back else 1,0)))
    if pos is None: raise ValueError(f'No fitting surface at {x,z,back}')
    return pos+Vector((0,offset if back else -offset,0))
# Close the supplied shirt's deep opening into a service-jacket front.
# Fit behind existing cloth where it overlaps, and ahead of the skin in the opening.
vs=[]; fs=[]; nx=20; nz=18
for j in range(nz+1):
    for i in range(nx+1):
        x=-.10+i*.20/nx
        top=1.495
        z=1.39+(top-1.39)*j/nz
        p=hit(unmasked_skin,x,z,offset=.009)
        garment=hit(cloth,x,z,offset=0)
        if garment.y<p.y: p.y=max(p.y,garment.y+.003)
        vs.append(p)
for j in range(nz):
    for i in range(nx):
        a=j*(nx+1)+i; fs.append((a,a+1,a+nx+2,a+nx+1))
closure=mesh_object('Jacket front closure and inner collar',vs,fs,navy)
for p in closure.data.polygons:
    p.use_smooth=True
vs=[]; fs=[]; nx=20; nz=6
for j in range(nz+1):
    for i in range(nx+1):
        x=-.065+i*.13/nx; top=1.510+.008*(abs(x)/.065)**1.4
        z=1.495+(top-1.495)*j/nz
        p=hit(unmasked_skin,x,z,offset=.009); garment=hit(cloth,x,z,offset=0)
        if garment.y<p.y: p.y=max(p.y,garment.y+.003)
        vs.append(p)
for j in range(nz):
    for i in range(nx):
        a=j*(nx+1)+i; fs.append((a,a+1,a+nx+2,a+nx+1))
inner=mesh_object('Pale blue shirt neckline',vs,fs,blue)
for p in inner.data.polygons: p.use_smooth=True
points=[]; polygons=[]
for ob in (uniform,closure,inner):
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=ev.to_mesh(); base=len(points)
    points.extend(ob.matrix_world @ v.co for v in me.vertices)
    polygons.extend(tuple(base+i for i in p.vertices) for p in me.polygons); ev.to_mesh_clear()
cloth=BVHTree.FromPolygons(points,polygons)
def patch(name,x0,x1,z0,z1,mat,back=False,offset=.003,nx=8,nz=6):
    verts=[hit(cloth,x0+(x1-x0)*i/nx,z0+(z1-z0)*j/nz,back,offset) for j in range(nz+1) for i in range(nx+1)]
    faces=[]
    for j in range(nz):
        for i in range(nx):
            a=j*(nx+1)+i; face=(a,a+1,a+nx+2,a+nx+1)
            faces.append(tuple(reversed(face)) if back else face)
    ob=mesh_object(name,verts,faces,mat); uv=ob.data.uv_layers.new()
    for face in ob.data.polygons:
        for li in face.loop_indices:
            vi=ob.data.loops[li].vertex_index; u=vi%(nx+1)/nx
            uv.data[li].uv=(1-u if back else u,vi//(nx+1)/nz)
    return ob
def text(name,word,loc,size,back=False):
    c=bpy.data.curves.new(name,'FONT'); c.body=word; c.align_x='CENTER'; c.align_y='CENTER'; c.size=size; c.extrude=.0002
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.location=loc
    o.rotation_euler=(math.pi/2,0,math.pi if back else 0); c.materials.append(white)
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o
    bpy.ops.object.convert(target='MESH'); o=bpy.context.object
    for v in o.data.vertices:
        w=o.matrix_world @ v.co; w.y=hit(cloth,w.x,w.z,back,.0045).y
        v.co=o.matrix_world.inverted() @ w
    return o
label=material('Woven identification patch',(.02,.03,.04),.9)
tex=label.node_tree.nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(str(HERE/'source/identification_patch.png'),check_existing=True)
label.node_tree.links.new(tex.outputs['Color'],label.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
patch('Back identification backing',-.166,.166,1.365,1.47,label,True,.004,nx=48,nz=20)
patch('Chest identification backing',.045,.17,1.37,1.410,label,False,.004,nx=28,nz=12)
for side in (-1,1):
    lo,hi=sorted((side*.055,side*.165))
    patch(f'Chest pocket {side}',lo,hi,1.263,1.353,panel)
    patch(f'Pocket flap {side}',lo-.003,hi+.003,1.334,1.357,navy,offset=.006)
    p=hit(cloth,side*.13,1.345,offset=.009); uvball(f'Pocket snap {side}',p,(.003,.0015,.003),metal)
    points=[]; tabfaces=[]
    for j in range(3):
        for i in range(9):
            x=side*(.135+i*.013); y=-.016+j*.016
            p,n,_,_=cloth.ray_cast(Vector((x,y,2)),Vector((0,0,-1)))
            if p is None: raise ValueError('Shoulder tab failed to fit')
            points.append(p+n*.0015)
    for j in range(2):
        for i in range(8):
            a=j*9+i; tabfaces.append((a,a+1,a+10,a+9))
    mesh_object(f'Shoulder tab {side}',points,tabfaces,panel)
    uvball(f'Shoulder button {side}',points[9]+Vector((0,0,.002)),(.0035,.0035,.001),metal)
    z=1.335
    def sleeve_hit(y,z,offset=.004):
        p,n,_,_=cloth.ray_cast(Vector((side*2,y,z)),Vector((-side,0,0)))
        if p is None: raise ValueError(f'No sleeve surface {side,y,z}')
        return p+Vector((side*offset,0,0))
    def sleeve_rect(name,y0,y1,z0,z1,mat):
        pts=[sleeve_hit(y,z,.007) for y,z in [(y0,z0),(y1,z0),(y1,z1),(y0,z1)]]
        return mesh_object(name,pts,[(0,1,2,3)],mat)
    shield=[(-.027,.038),(.027,.038),(.028,-.007),(.020,-.033),(0,-.044),(-.020,-.033),(-.028,-.007)]
    pts=[sleeve_hit(a-.015,z+b) for a,b in shield]
    center=sleeve_hit(-.015,z)
    mesh_object(f'Sleeve shield backing {side}',[center]+pts,[(0,i+1,(i+1)%len(pts)+1) for i in range(len(pts))],panel)
    tube(f'Sleeve shield gold edge {side}',pts+[pts[0]],.0015,gold)
    badge=material(f'Hannover arms {side}',(.05,.05,.05),.85)
    tex=badge.node_tree.nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(str(HERE/'source/hannover-arms.png'),check_existing=True)
    badge.node_tree.links.new(tex.outputs['Color'],badge.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
    # Inset the vector-derived arms into a curved rectangular textile panel.
    vs=[]; fs=[]; nx=8; nz=10
    for j in range(nz+1):
        for i in range(nx+1): vs.append(sleeve_hit(-.039+i*.048/nx,z-.030+j*.057/nz,.008))
    for j in range(nz):
        for i in range(nx):
            a=j*(nx+1)+i; fs.append((a,a+1,a+nx+2,a+nx+1))
    ob=mesh_object(f'Hannover sleeve arms {side}',vs,fs,badge); uv=ob.data.uv_layers.new()
    for f in ob.data.polygons:
        for li in f.loop_indices:
            vi=ob.data.loops[li].vertex_index; uv.data[li].uv=(vi%(nx+1)/nx,vi//(nx+1)/nz)
    tube(f'Lower pocket welt {side}',[hit(cloth,side*(.10+i*.004),1.12+i*.004,offset=.005) for i in range(15)],.0016,panel)
zippts=[hit(cloth,0,1.085+i*.008,offset=.004) for i in range(51)]
tube('Central zipper tape',zippts,.003,nylon)
for i in range(48): cube(f'Zipper tooth {i}',hit(cloth,0,1.1+i*.008,offset=.006),(.006,.002,.0015),metal,.0004)
cube('Zipper pull',hit(cloth,0,1.49,offset=.008),(.009,.004,.021),metal,.002)
verts=[]; faces=[]; rx=.205; ry=.149; cy=-.029
for i in range(97):
    a=2*math.pi*i/96
    for z in (1.028,1.071):
        radial=Vector((math.cos(a),math.sin(a),0))
        p,n,_,_=cloth.ray_cast(Vector((radial.x,cy+radial.y,z)),-radial)
        if p is None: raise ValueError('Belt contour did not fit')
        verts.append(p+radial*.009)
    if i: faces.append((2*i-2,2*i,2*i+1,2*i-1))
radii=[]
for i in range(96):
    radii.append(max(math.hypot(verts[i*2+j].x,verts[i*2+j].y-cy) for j in (0,1)))
envelope=[max(radii[(i+k)%96] for k in range(-3,4))+.001 for i in range(96)]
for i in range(97):
    a=2*math.pi*i/96; r=envelope[i%96]
    for j,z in enumerate((1.028,1.071)): verts[i*2+j]=Vector((r*math.cos(a),cy+r*math.sin(a),z))
belt=mesh_object('Duty belt',verts,faces,nylon)
for p in belt.data.polygons: p.use_smooth=True
sol=belt.modifiers.new('Webbing thickness','SOLIDIFY'); sol.thickness=.006
by=hit(cloth,0,1.05,offset=.013).y
cube('Belt buckle',(0,by,1.05),(.052,.012,.033),black)
cube('Buckle central plate',(0,by-.008,1.05),(.026,.003,.019),metal,.002)
for side in (-1,1):
    p=hit(cloth,side*.075,1.05,offset=.01)
    cube(f'Belt keeper {side}',p,(.015,.012,.051),black,.002)
    cube(f'Utility pouch {side}',(side*.222,-.035,1.00),(.058,.084,.117),nylon,.008)
    cube(f'Utility pouch flap {side}',(side*.222,-.080,1.027),(.055,.010,.051),black)
    uvball(f'Pouch snap {side}',(side*.222,-.087,1.015),(.004,.002,.004),metal)
p=hit(cloth,-.155,1.466,offset=.015)
cube('Shoulder radio microphone',p,(.047,.025,.064),black,.006)
for i in range(5): cube(f'Radio speaker slot {i}',p+Vector((0,-.015,-.016+i*.006)),(.030,.002,.0015),metal,.0003)
wire=[]
for i in range(121):
    t=i/120; z=1.43-.31*t; x=-.145-.010*math.sin(math.pi*t)
    base=hit(cloth,x,z,offset=.010); base.x+=.0025*math.cos(t*math.pi*40); base.y+=.0025*math.sin(t*math.pi*40); wire.append(base)
tube('Radio coiled lead',wire,.0015,black)
for side in (-1,1):
    cx=side*.200
    for i in range(6):
        z=.045+i*.012
        left=hit(boot,cx-.018,z,offset=.003); right=hit(boot,cx+.018,z+.012,offset=.003)
        tube(f'Boot lace {side} A{i}',[left,(left+right)*.5+Vector((0,-.003,0)),right],.0016,lace)
        left2=hit(boot,cx+.018,z,offset=.003); right2=hit(boot,cx-.018,z+.012,offset=.003)
        tube(f'Boot lace {side} B{i}',[left2,(left2+right2)*.5+Vector((0,-.004,0)),right2],.0016,lace)
        for p in (left,left2): uvball(f'Boot eyelet {side} {i}',p,(.003,.0015,.003),metal)
rng=random.Random(41)
for i in range(1450):
    x=rng.uniform(-.031,.031); edge=abs(x)/.031
    low=1.629+.005*edge**1.5; high=1.644-.008*edge**1.5
    z=rng.uniform(low,high)
    if abs(x)<.003 and rng.random()<.65: continue
    p=hit(skin,x,z,offset=.0007); q=hit(skin,x+rng.uniform(-.001,.001),z-rng.uniform(.002,.0045),offset=.001)
    tube(f'Moustache hair {i}',[p,(p+q)*.5+Vector((0,-.0005,0)),q],rng.uniform(.00011,.00019),grayhair)
for j in range(3):
    pts=[]
    for i in range(41):
        x=-.046+i*.092/40; z=1.742+j*.009+.003*(x/.046)**2
        pts.append(hit(skin,x,z,offset=.00012))
    tube(f'Forehead crease {j}',pts,.00010,crease)
for side in (-1,1):
    pts=[hit(skin,side*(.024+i*.0011),1.650-i*.0022,offset=.0001) for i in range(15)]
    tube(f'Nasolabial crease {side}',pts,.00010,crease)
for o in list(bpy.data.objects):
    if o.type in ('MESH','CURVE','FONT') and o.parent is None: o.parent=rig
sys.path.insert(0,str(HERE))
from fit_labels import refit_labels
refit_labels()
from vest import add_vest
add_vest()
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=12 if DRAFT else 40
scene.cycles.use_denoising=True
scene.render.resolution_x=700 if DRAFT else 1000; scene.render.resolution_y=900 if DRAFT else 1250; scene.render.resolution_percentage=100
scene.world.color=(.18,.18,.18)
floor=material('Studio floor',(.14,.16,.19),.9); cube('Studio ground',(0,0,-.0465),(200,200,.04),floor)
def aim(o,point): o.rotation_euler=(Vector(point)-o.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power,size in [('Key',(-3,-4,5),400,4),('Fill',(3,-2,3),230,3),('Rim',(1,3,4),450,3)]:
    d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.shape='DISK'; d.size=size
    o=bpy.data.objects.new(name,d); scene.collection.objects.link(o); o.location=loc; aim(o,(0,0,1))
d=bpy.data.cameras.new('Review camera'); cam=bpy.data.objects.new('Review camera',d); scene.collection.objects.link(cam); scene.camera=cam; d.type='ORTHO'
scene.view_settings.view_transform='AgX'
views=[('three_quarter',(3,-6,2.5),(0,0,.91),2.05),('back',(-2,6,2.4),(0,0,.91),2.05),('face',(.5,-5,1.9),(0,-.025,1.65),.49),('hand',(1.5,-4,1.6),(.48,-.02,1.0),.5),('shoes',(1.8,-4,1.1),(0,-.05,.13),.78),('front',(0,-6,1.7),(0,0,.91),2.05),('vest_front',(0,-5,1.6),(0,0,1.32),.78),('vest_side',(4,-2,1.8),(0,0,1.32),.86)]
for name,loc,target,scale in views:
    cam.location=loc; aim(cam,target); d.ortho_scale=scale; scene.render.filepath=str(OUT/f'{name}.png'); bpy.ops.render.render(write_still=True)
cam.location=views[0][1]; aim(cam,views[0][2]); d.ortho_scale=views[0][3]
bpy.ops.file.pack_all(); bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'officer_v2.blend'))
print('OFFICER_V2_SAVED',flush=True)
