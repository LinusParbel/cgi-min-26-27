import bpy,sys,json,math,random
from pathlib import Path
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parents[1]/'lib'));sys.path.insert(0,str(H))
import photo_lib as pl
import verify
S=json.loads((H/'spec.json').read_text());r=random.Random(S['seed']);al=pl.al
al.clear_scene()
mats=[al.material('asphalt_edge',(.082,.079,.073),mottle=.35,dust=.08,grime=.15),al.material('broken_lip',(.060,.057,.052),mottle=.42,dust=.08,grime=.22),al.material('broken_wall',(.038,.036,.032),mottle=.3),al.material('dark_centre',(.022,.022,.020),mottle=.32),al.material('aggregate',(.14,.13,.11),mottle=.25)]
n=S['segments'];verts=[];faces=[];mi=[]
rad=[1+.065*math.sin(i*1.73)+.048*math.sin(i*.67)+r.uniform(-.035,.035) for i in range(n)]
for j,(scale,z) in enumerate(zip(S['ring_scales'],S['ring_heights'])):
 for i in range(n):
  a=i*math.tau/n;v=rad[i];zz=z+(r.uniform(-.002,.003) if j in [1,2] else r.uniform(0,.0005))
  verts.append((.55*scale*v*math.cos(a),.4*scale*v*math.sin(a),zz))
for j in range(4):
 for i in range(n):
  k=(i+1)%n;a=j*n+i;b=j*n+k;c=(j+1)*n+k;d=(j+1)*n+i
  faces.extend([(a,b,c),(a,c,d)]);mi.extend([min(j,3)]*2)
verts.append((.025,-.015,.003));c=len(verts)-1
for i in range(n):faces.append((4*n+i,4*n+(i+1)%n,c));mi.append(3)
mesh=bpy.data.meshes.new('continuous_non_coplanar_damage');mesh.from_pydata(verts,[],faces);mesh.update()
o=bpy.data.objects.new('pothole_surface',mesh);bpy.context.collection.objects.link(o)
for m in mats:mesh.materials.append(m)
for p,idx in zip(mesh.polygons,mi):p.material_index=idx
parts=[o]
# Embedded small angular chips occupy the depression, with visible peaks and no floating rocks.
for k in range(24):
 a=r.random()*math.tau;t=math.sqrt(r.random())*.52;x=.55*t*math.cos(a);y=.4*t*math.sin(a);s=r.uniform(.005,.014);z=.0044
 v=[(x-s,y-s*.5,z),(x+s*.8,y-s*.7,z),(x+s,y+s*.5,z),(x-s*.6,y+s,z),(x,y,z+r.uniform(.003,.007))]
 f=[(0,1,4),(1,2,4),(2,3,4),(3,0,4)]
 m=bpy.data.meshes.new('chip');m.from_pydata(v,[],f);m.materials.append(mats[4]);ob=bpy.data.objects.new('embedded_aggregate',m);bpy.context.collection.objects.link(ob);parts.append(ob)
# Centre the authored silhouette at ground origin without lowering it through opaque road.
allv=[v.co for ob in parts for v in ob.data.vertices]
cx=(min(v.x for v in allv)+max(v.x for v in allv))/2;cy=(min(v.y for v in allv)+max(v.y for v in allv))/2
for ob in parts:
 for v in ob.data.vertices:v.co.x-=cx;v.co.y-=cy
bpy.context.view_layer.update();checks=verify.geometry(parts);(H/'out/geometry_checks.json').write_text(json.dumps(checks,indent=2));print(checks)
bpy.ops.wm.save_as_mainfile(filepath=str(H/'editable.blend'))
if '--export' in sys.argv:
 pl.bake_shared_and_export({'patch':parts},{'patch':(0,0,0)},H/'out','PROP_Pothole',res=S['atlas'],samples=32)
