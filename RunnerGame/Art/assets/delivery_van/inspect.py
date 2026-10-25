import bpy,json
from pathlib import Path
bpy.ops.import_scene.gltf(filepath=str(Path('.model-research/delivery-van/source.glb').resolve()))
r=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();v=[o.matrix_world@x.co for x in o.data.vertices]
 r.append(dict(name=o.name,tri=len(o.data.loop_triangles),mat=[m.name for m in o.data.materials],bounds=[[round(min(q[i] for q in v),4),round(max(q[i] for q in v),4)] for i in range(3)]))
Path('RunnerGame/Art/assets/delivery_van/source-inspection.json').write_text(json.dumps(r,indent=2))
for q in r:print(q)
