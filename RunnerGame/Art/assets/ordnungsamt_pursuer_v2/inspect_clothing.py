import bpy
from pathlib import Path
p=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(p/'officer_v2.blend'))
o=bpy.data.objects['Service jacket and trousers']
me=o.data; parent=list(range(len(me.vertices)))
def find(i):
    while parent[i]!=i:
        parent[i]=parent[parent[i]]; i=parent[i]
    return i
for edge in me.edges:
    a,b=map(find,edge.vertices); parent[a]=b
groups={}
for v in me.vertices: groups.setdefault(find(v.index),[]).append(v)
for vs in sorted(groups.values(),key=len,reverse=True)[:20]:
    print('GARMENT_COMPONENT',len(vs),[[round(min(v.co[i] for v in vs),4),round(max(v.co[i] for v in vs),4)] for i in range(3)],flush=True)
