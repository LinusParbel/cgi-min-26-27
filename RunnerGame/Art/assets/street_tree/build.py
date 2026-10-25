"""Blender 5.2: --python build.py -- [--bake]. First run checks/previews only."""
import bpy, sys, json, math, random, hashlib
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'RunnerGame/Art/lib'))
import photo_lib as pl
al=pl.al
S=json.loads((HERE/'spec.json').read_text()); rng=random.Random(S['seed'])
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene; scene.render.threads_mode='FIXED'; scene.render.threads=S['threads']
def mat(name,c):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True
    m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*c,1)
    m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.9
    return m
wood=al.material('weathered bark',(.16,.105,.065),roughness=.95,dust=.12,streaks=.7,grime=.12,mottle=.25)
greens=[mat('leaf green '+str(i),c) for i,c in enumerate([(.105,.19,.045),(.14,.235,.06),(.19,.27,.075),(.09,.155,.04),(.16,.215,.055)])]
verts=[]; faces=[]; mids=[]
def tube(points,radii,sides=8):
    start=len(verts)
    for k,(p,r) in enumerate(zip(points,radii)):
        p=Vector(p); axis=Vector(points[min(k+1,len(points)-1)])-Vector(points[max(0,k-1)])
        q=axis.to_track_quat('Z','Y')
        for j in range(sides):
            vertex=p+q@Vector((r*math.cos(j*math.tau/sides),r*math.sin(j*math.tau/sides),0))
            if p.z==0: vertex.z=0
            verts.append(tuple(vertex))
    for k in range(len(points)-1):
        for j in range(sides): faces.append((start+k*sides+j,start+k*sides+(j+1)%sides,start+(k+1)*sides+(j+1)%sides,start+(k+1)*sides+j)); mids.append(0)
    faces.extend([tuple(start+j for j in reversed(range(sides))),tuple(start+(len(points)-1)*sides+j for j in range(sides))]); mids.extend([0,0])
trunk=[(0,0,0),(.025,-.015,.55),(.09,.015,1.4),(.065,.04,2.3),(.14,.03,3.2),(.08,.12,4.1),(.16,.08,5.1),(.1,.12,6.25)]
tube(trunk,[.19,.16,.135,.115,.095,.07,.045,.012],10)
centres=[]
# Layered non-spherical crown; radii peak in middle, taper at top, unequal azimuths.
for i in range(40):
    t=i/39; z=2.92+3.04*t; angle=(i//2)*2.39996+(i%2)*.49+rng.uniform(-.24,.24)
    radius=(1.16+.38*math.sin(t*math.pi)-.79*t**3)*rng.uniform(.84,1.04)
    end=Vector((math.cos(angle)*radius+.08,math.sin(angle)*radius+.06,z))
    root=Vector((.1,.07,max(2.35,z-.95)))
    mid=root.lerp(end,.53)+Vector((0,0,-.13))
    if i%2==0:
        tube([root,mid,end],[.043*(1-.55*t),.022,.005],6)
        previous_mid=mid.copy()
    else:
        tube([previous_mid,mid,end],[.022,.014,.005],6)
    centres.append(end)
    for side in (-1,1):
        twig=end+Vector((math.cos(angle+side*.85)*.24,math.sin(angle+side*.85)*.24,.16))
        tube([mid,end.lerp(twig,.65),twig],[.016,.008,.0025],5)
leaf_start=len(faces)
for centre in centres:
    for j in range(50):
        # Leaf clouds remain locally attached to terminal branch clusters with porous gaps.
        p=centre+Vector((rng.uniform(-.42,.34),rng.uniform(-.39,.34),rng.uniform(-.30,.42)))
        n=Vector((rng.uniform(-1,1),rng.uniform(-1,1),rng.uniform(-.7,1))).normalized()
        u=n.cross(Vector((0,0,1)))
        if u.length<.01: u=Vector((1,0,0))
        u.normalize(); v=n.cross(u).normalized(); a=rng.random()*math.tau
        u,v=u*math.cos(a)+v*math.sin(a),-u*math.sin(a)+v*math.cos(a)
        length=S['leaf_length']*rng.uniform(.8,1.2); width=S['leaf_width']*rng.uniform(.8,1.2)
        k=len(verts); verts.extend([tuple(p+u*length/2),tuple(p+v*width/2),tuple(p-u*length/2),tuple(p-v*width/2)])
        # Distinct vertex IDs are essential: Blender edit-mode conversion removes duplicate faces
        # on the same vertex IDs during smart UV unwrap, even with reversed winding.
        verts.extend(verts[k:k+4])
        mi=1+rng.randrange(len(greens)); faces.extend([(k,k+1,k+2,k+3),(k+7,k+6,k+5,k+4)]); mids.extend([mi,mi])
me=bpy.data.meshes.new('authored branch and two sided leaf geometry'); me.from_pydata(verts,[],faces); me.update()
obj=bpy.data.objects.new('ENV_StreetTree',me); scene.collection.objects.link(obj)
for m in [wood]+greens: me.materials.append(m)
for p,mi in zip(me.polygons,mids): p.material_index=mi
# Rescale crown to authored bounds without shifting trunk's ground pivot.
lo=[min(v.co[i] for v in me.vertices) for i in range(3)]; hi=[max(v.co[i] for v in me.vertices) for i in range(3)]
for v in me.vertices:
    v.co.x*=3.5/(hi[0]-lo[0]); v.co.y*=3.5/(hi[1]-lo[1]); v.co.z*=6.5/hi[2]
deps=bpy.context.evaluated_depsgraph_get(); ev=obj.evaluated_get(deps).to_mesh(); ev.calc_loop_triangles()
tris=len(ev.loop_triangles); leaf_polys=[p for p in ev.polygons if p.material_index>0]
assert tris<=S['triangle_budget']; assert len(leaf_polys)==4000
assert min(v.co.z for v in ev.vertices)==0
assert min(ev.vertices[i].co.z for p in leaf_polys for i in p.vertices)>2.4
assert all(p.area>1e-8 for p in ev.polygons)
assert not obj.modifiers
for i in range(leaf_start,len(me.polygons),2): assert me.polygons[i].normal.dot(me.polygons[i+1].normal)<-.999
check={'evaluated_triangles':tris,'leaf_triangles':8000,'wood_triangles':tris-8000,'leaf_quads_per_side':2000,'bounds_source':[list(map(lambda i:min(v.co[i] for v in ev.vertices),range(3))),list(map(lambda i:max(v.co[i] for v in ev.vertices),range(3)))],'seed':S['seed'],'geometry_sha256':hashlib.sha256(repr((verts,faces)).encode()).hexdigest(),'modifiers':0,'two_sided_opposed_pairs':2000,'leaf_min_z':min(ev.vertices[i].co.z for p in leaf_polys for i in p.vertices)}
(HERE/'out/prebake_checks.json').write_text(json.dumps(check,indent=2)); obj.evaluated_get(deps).to_mesh_clear()
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'out/ENV_StreetTree_source.blend'))
if '--bake' not in sys.argv:
    al.render_previews(obj,str(HERE/'previews/shape.png'),views=('three_quarter','back'),size=384)
else:
    al.bake_and_export(obj,str(HERE/'out'),'ENV_StreetTree',S['atlas'],samples=S['samples'],margin=3,uv_margin=.001,keep_origin=True,ao_strength=.25)
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'out/ENV_StreetTree_baked.blend'))
print(json.dumps(check))
