"""Validate actual engine OBJ parts, shared opaque atlas and wheel pivots."""
from pathlib import Path
import json,math,hashlib
from PIL import Image
HERE=Path(__file__).resolve().parent; OUT=HERE/'out'; PREFIX='VEH_BikeCommuter'
manifest=json.loads((OUT/(PREFIX+'_parts.json')).read_text())
spec=json.loads((HERE/'spec.json').read_text()); dimensions=spec['dims']
assert {p['name'] for p in manifest['parts']}=={'body','wheel_front','wheel_rear'}
report=[]; world=[]; files=[OUT/(PREFIX+'_parts.json'),OUT/manifest['texture']]
for part in manifest['parts']:
    path=OUT/part['obj']; files.append(path)
    vs=[];uv=[];normals=[];faces=[]
    for line in path.read_text().splitlines():
        fields=line.split()
        if not fields: continue
        if fields[0]=='v': vs.append(tuple(map(float,fields[1:4])))
        elif fields[0]=='vt': uv.append(tuple(map(float,fields[1:3])))
        elif fields[0]=='vn': normals.append(tuple(map(float,fields[1:4])))
        elif fields[0]=='f': faces.append([tuple(map(int,v.split('/'))) for v in fields[1:]])
    assert all(math.isfinite(c) for v in vs+uv+normals for c in v)
    assert all(len(f)==3 for f in faces)
    assert all(1<=i<=len(vs) and 1<=t<=len(uv) and 1<=n<=len(normals) for f in faces for i,t,n in f)
    assert all(-.00001<=c<=1.00001 for v in uv for c in v)
    assert all(abs(sum(c*c for c in n)-1)<.001 for n in normals)
    degenerate=0
    for face in faces:
        a,b,c=[vs[v[0]-1] for v in face]
        u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
        cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        if sum(x*x for x in cross)<1e-20: degenerate+=1
    assert degenerate==0,(part['name'],degenerate)
    px,py,pz=part['pivot']
    world.extend((x+px,y+pz,z-py) for x,y,z in vs)
    if part['name'].startswith('wheel'):
        for axis in (1,2):
            assert abs(min(v[axis] for v in vs)+dimensions['wheel_d']['value']/2)<.001
            assert abs(max(v[axis] for v in vs)-dimensions['wheel_d']['value']/2)<.001
        assert abs(pz-dimensions['wheel_d']['value']/2)<.00001
    report.append({'name':part['name'],'triangles':len(faces),'vertices':len(vs),'pivot_blender':part['pivot'],'degenerate_triangles':degenerate})
triangles=sum(p['triangles'] for p in report)
assert triangles<=spec['tri_budget']
assert -.001<=min(v[1] for v in world)<=.003
front=next(p for p in manifest['parts'] if p['name']=='wheel_front')['pivot']
rear=next(p for p in manifest['parts'] if p['name']=='wheel_rear')['pivot']
assert front[1]<rear[1] and abs(rear[1]-front[1]-dimensions['wheelbase']['value'])<.00001
with Image.open(OUT/manifest['texture']) as im:
    assert im.size==(spec['tex_res'],spec['tex_res'])
    assert im.convert('RGBA').getchannel('A').getextrema()==(255,255)
result={'triangles':triangles,'budget':spec['tri_budget'],'parts':report,'opaque_texture_size':spec['tex_res'],'floor_engine_y':min(v[1] for v in world),'forward':'Blender -Y / engine +Z','hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(OUT/'validation.json').write_text(json.dumps(result,indent=2))
print('BIKE_EXPORT_VERIFIED',json.dumps({k:v for k,v in result.items() if k!='hashes'}))
