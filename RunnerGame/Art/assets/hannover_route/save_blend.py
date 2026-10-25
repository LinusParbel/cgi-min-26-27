"""Run headless Blender after build.py; preserves editable individual buildings."""
import bpy,json
from pathlib import Path
A=Path(__file__).resolve().parent;O=A/'out'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mat=bpy.data.materials.new('Neutral authored massing grey');mat.diffuse_color=(.31,.33,.34,1)
vertices=[];groups={};current=None
for line in (O/'HannoverRoute.obj').read_text().splitlines():
 p=line.split()
 if not p:continue
 if p[0]=='v':x,y,z=map(float,p[1:]);vertices.append((x,-z,y))
 elif p[0]=='o':current=p[1];groups[current]=[]
 elif p[0]=='f':groups[current].append(tuple(int(x.split('/')[0])-1 for x in p[1:]))
records={x['name']:x for x in json.loads((A/'buildings.json').read_text())}
for name,faces in groups.items():
 ids=sorted({i for f in faces for i in f});lookup={n:i for i,n in enumerate(ids)}
 mesh=bpy.data.meshes.new(name);mesh.from_pydata([vertices[i] for i in ids],[],[tuple(lookup[i] for i in f) for f in faces]);mesh.update()
 obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat)
 r=records[name];obj['source_gml_id']=r['id'];obj['source_tile']=r['tile'];obj['source_bbox_ENH']=json.dumps([r['lo'],r['hi']]);obj['licence']='CC BY 4.0; Landeshauptstadt Hannover'
bpy.context.scene['origin_ENH']='550000,5803000,55';bpy.context.scene['source_crs']='EPSG:25832 / DE_DHHN92_NH';bpy.context.scene.unit_settings.system='METRIC'
bpy.ops.wm.save_as_mainfile(filepath=str(A/'HannoverRoute.blend'))
print('Saved editable city buildings',len(groups))
