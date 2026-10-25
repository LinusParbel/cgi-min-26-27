"""Geometry contract for the measured commuter (run inside Blender)."""
import sys,json,math
from mathutils.bvhtree import BVHTree
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import build
if '--mutate-spokes' in sys.argv:
    source=(HERE/'build.py').read_text()
    old="count=int(d('spoke_count'))"
    assert old in source
    exec(compile(source.replace(old,old+'-1'),str(HERE/'build.py'),'exec'),build.__dict__)
pl=build.pl
pl.al.clear_scene()
spec=pl.Spec(HERE/'spec.json')
parts=build.build(spec)
objects=[o for group in parts.values() for o in group]
tri=sum(pl.al.tri_count(o) for o in objects)
assert tri<=json.loads((HERE/'spec.json').read_text())['tri_budget'],tri
pts=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
assert -.001<=min(p.z for p in pts)<=.003
f=pl.bpy.data.objects['LM_front_axle'].location
r=pl.bpy.data.objects['LM_rear_axle'].location
assert f.y<r.y and abs((f-r).length-spec.d('wheelbase'))<.001
for name,centre in [('wheel_front',f),('wheel_rear',r)]:
    spokes=[o for o in parts[name] if '_spoke_' in o.name]
    assert len(spokes)==spec.d('spoke_count')
    for o in spokes:
        assert min(o.dimensions)<.0025 and max(o.dimensions)>.15
    tyre=next(o for o in parts[name] if o.name.endswith('_tyre'))
    assert abs(tyre.dimensions.z-spec.d('wheel_d'))<.001
    rim=next(o for o in parts[name] if o.name.endswith('_rim'))
    assert rim.dimensions.z<tyre.dimensions.z-.025
for photo in json.loads((HERE/'refs.json').read_text())['photos']:
    for lm in photo.get('landmarks',{}):
        assert pl.bpy.data.objects.get('LM_'+lm),lm
for rack in ['front','rear']:
    assert len([o for o in objects if o.name.startswith(rack+'_rack_support')])>=2
feet=[o for o in objects if o.name.startswith('stand_foot')]
assert len(feet)==2 and all(min((o.matrix_world@v.co).z for v in o.data.vertices)<.005 for o in feet)
# Surface intervals prove the saddle has a continuous structural support chain.
# A ray passes through each pair's shared material volume, rather than testing names/counts.
deps=pl.bpy.context.evaluated_depsgraph_get()
def interval(name,origin,direction):
    ob=pl.bpy.data.objects[name];tree=BVHTree.FromObject(ob,deps)
    inv=ob.matrix_world.inverted();p=inv@Vector(origin);v=inv.to_3x3()@Vector(direction)
    hits=[];travel=0
    for _ in range(8):
        loc,normal,index,distance=tree.ray_cast(p,v,2)
        if loc is None:break
        travel+=distance;hits.append(travel);p=loc+v*.000001;travel+=.000001
    assert len(hits)>=2,(name,hits)
    return hits[0],hits[-1]
def overlaps(a,b,origin,direction):
    aa=interval(a,origin,direction);bb=interval(b,origin,direction)
    assert min(aa[1],bb[1])-max(aa[0],bb[0])>-.0001,(a,b,aa,bb)
post=pl.bpy.data.objects['LM_seatpost_top'].location
clampz=post.z+spec.d('saddle_thick')*.5
overlaps('seatpost','saddle_post_clamp_riser',(0,post.y,post.z-.15),(0,0,1))
overlaps('saddle_post_clamp_riser','saddle_rail_clamp',(0,post.y,post.z-.15),(0,0,1))
for side in [-1,1]:
    x=side*spec.d('saddle_w')*.10
    overlaps('saddle_rail_clamp','saddle_rail_'+str(side),(x,post.y-.1,clampz),(0,1,0))
    for t in [-.25,.28]:
        overlaps('saddle_rail_'+str(side),'padded_saddle',(x,post.y+spec.d('saddle_len')*t,.8),(0,0,1))
# Surface rays: the double-triangle frame and spoke wheel must contain real holes.
deps=pl.bpy.context.evaluated_depsgraph_get()
assert not pl.bpy.context.scene.ray_cast(deps,Vector((2,0,.60)),Vector((-1,0,0)),distance=4)[0], 'filled frame triangle'
assert any(not pl.bpy.context.scene.ray_cast(deps,Vector((2,f.y+.16,f.z+.11+i*.007)),Vector((-1,0,0)),distance=4)[0] for i in range(8)), 'filled wheel'
result={'triangles':tri,'parts':{k:sum(pl.al.tri_count(o) for o in g) for k,g in parts.items()},'floor':min(p.z for p in pts),'wheelbase':(f-r).length,'spokes_per_wheel':len(spokes)}
(HERE/'previews').mkdir(exist_ok=True)
(HERE/'previews/geometry_validation.json').write_text(json.dumps(result,indent=2))
print('BIKE_GEOMETRY_PASSED',result)
