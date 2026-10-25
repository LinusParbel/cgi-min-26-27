from pathlib import Path
import bpy, collections, json
here=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(here/'officer_v2_run_preview.blend'))
dg=bpy.context.evaluated_depsgraph_get(); totals=collections.Counter(); rows=[]
for ob in bpy.data.objects:
    if ob.type not in ('MESH','CURVE','FONT') or ob.hide_render or ob.name=='Studio ground': continue
    ev=ob.evaluated_get(dg); mesh=ev.to_mesh()
    n=sum(len(p.vertices)-2 for p in mesh.polygons); ev.to_mesh_clear()
    totals['Moustache' if ob.name.startswith('Moustache') else ob.type]+=n
    rows.append({'name':ob.name,'triangles':n,'modifiers':[(m.type,getattr(m,'levels',None)) for m in ob.modifiers]})
(here/'previews/export_inventory.json').write_text(json.dumps(rows,indent=2))
print('COUNTS',dict(totals),'TOP',sorted(rows,key=lambda r:r['triangles'],reverse=True)[:15])
