import bpy,json
from pathlib import Path
from mathutils import Vector
bpy.ops.import_scene.gltf(filepath=str(Path('.model-research/city-car-candidates/innerscene-hatchback.glb').resolve()))
r=[]
for o in bpy.data.objects:
 if o.type=='MESH':
  vs=[o.matrix_world@v.co for v in o.data.vertices];o.data.calc_loop_triangles()
  r.append(dict(name=o.name,tris=len(o.data.loop_triangles),bounds=[[round(min(v[i] for v in vs),4),round(max(v[i] for v in vs),4)] for i in range(3)],mats=[m.name if m else '' for m in o.data.materials]))
Path('RunnerGame/Art/assets/city_car/inspection.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r))
