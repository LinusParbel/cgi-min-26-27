import json,math
from pathlib import Path
def normalize(A):
 manifest=json.loads((A/'out/VEH_DeliveryVan_parts.json').read_text());report={}
 for part in manifest['parts']:
  path=A/'out'/part['obj'];lines=path.read_text().splitlines();verts=[];result=[];removed=0
  for line in lines:
   t=line.split()
   if not t:continue
   if t[0]=='v':verts.append(tuple(map(float,t[1:4])))
   if t[0]=='vn':
    n=list(map(float,t[1:4]));l=math.sqrt(sum(x*x for x in n));assert l>0
    line='vn '+' '.join(f'{x/l:.9f}' for x in n)
   if t[0]=='f':
    q=[verts[int(x.split('/')[0])-1] for x in t[1:]];a,b,c=q
    u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)];cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
    if sum(x*x for x in cross)<1e-24:removed+=1;continue
   result.append(line)
  path.write_text('\n'.join(result)+'\n');report[part['name']]={'serialized_zero_area_faces_removed':removed,'uv_preserved':True,'unit_normals_normalized':True}
 (A/'export-normalization.json').write_text(json.dumps(report,indent=2))
