"""Remove collapsed bevel triangles after OBJ six-decimal serialization; create per-prop review manifests."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def trim_rim(path):
 lines=path.read_text().splitlines();vs=[];line_ids=[];parent=[]
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for ln,line in enumerate(lines):
  t=line.split()
  if t and t[0]=='v':vs.append(list(map(float,t[1:4])));line_ids.append(ln);parent.append(len(parent))
  if t and t[0]=='f':
   ids=[int(v.split('/')[0])-1 for v in t[1:]]
   for i in ids[1:]:parent[root(i)]=root(ids[0])
 groups={}
 for i in range(len(vs)):groups.setdefault(root(i),[]).append(i)
 trimmed=0
 for ids in groups.values():
  lo=[min(vs[i][j] for i in ids) for j in range(3)];hi=[max(vs[i][j] for i in ids) for j in range(3)]
  if abs(hi[0]-lo[0]-.75)<1e-4 and abs(lo[1]-.74)<1e-4 and abs(hi[1]-.8)<1e-4:
   for i in ids:vs[i][0]*=.725/.75;lines[line_ids[i]]='v '+' '.join(f'{v:.6f}' for v in vs[i])
   trimmed+=1
 path.write_text('\n'.join(lines)+'\n');return trimmed
def finish():
 info=json.loads((HERE/'out/PROP_StreetFurniture_parts.json').read_text());removed={}
 trimmed=trim_rim(HERE/'out/PROP_StreetFurniture_planter.obj')
 for p in info['parts']:
  path=HERE/'out'/p['obj'];vs=[];lines=[];n=0
  for line in path.read_text().splitlines():
   t=line.split()
   if t and t[0]=='v':vs.append(list(map(float,t[1:4])))
   if t and t[0]=='f':
    a,b,c=[vs[int(x.split('/')[0])-1] for x in t[1:]];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
    if sum((u[(j+1)%3]*v[(j+2)%3]-u[(j+2)%3]*v[(j+1)%3])**2 for j in range(3))<=1e-16:n+=1;continue
   lines.append(line)
  path.write_text('\n'.join(lines)+'\n');removed[p['name']]=n
  (HERE/'out'/('review_'+p['name']+'.json')).write_text(json.dumps({'texture':info['texture'],'parts':[p]},indent=2))
 (HERE/'out/export_cleanup.json').write_text(json.dumps(removed,indent=2));print('Collapsed serialized bevel triangles removed:',removed)
 print('UV-preserving rim endbar trims:',trimmed)
if __name__=='__main__':finish()
