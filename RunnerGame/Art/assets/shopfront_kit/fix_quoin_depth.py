"""Remove redundant quoin side depth from existing exports without rebaking/UV changes.
Only distinct quoin solid components are shortened; source generator uses same extent.
"""
from pathlib import Path
HERE=Path(__file__).resolve().parent
for path in (HERE/'out').glob('AR_Shopfront_*.obj'):
 lines=path.read_text().splitlines();vs=[];vlines=[];faces=[]
 for i,line in enumerate(lines):
  t=line.split()
  if not t:continue
  if t[0]=='v':vs.append(list(map(float,t[1:4])));vlines.append(i)
  if t[0]=='f':faces.append([int(a.split('/')[0])-1 for a in t[1:]])
 parent=list(range(len(vs)))
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for f in faces:
  for i in f[1:]:parent[root(i)]=root(f[0])
 groups={}
 for i in range(len(vs)):groups.setdefault(root(i),[]).append(i)
 count=0;trimcount=0
 for ids in groups.values():
  lo=[min(vs[i][j] for i in ids) for j in range(3)];hi=[max(vs[i][j] for i in ids) for j in range(3)]
  # OBJ Y is source Z; OBJ Z is minus source Y.
  if abs((hi[0]-lo[0])-.12)<1e-5 and abs((hi[1]-lo[1])-.22)<1e-5 and abs(lo[2]+.4)<1e-5 and abs(hi[2]-.27)<1e-5:
   count+=1
   for i in ids:
    if abs(vs[i][2]+.4)<1e-5:
     vs[i][2]=.22;lines[vlines[i]]='v '+' '.join(f'{c:.6f}' for c in vs[i])
  if abs(hi[0]-lo[0]-6)<1e-5 and abs(lo[2]+.4)<1e-5 and (abs(hi[1]-lo[1]-.16)<1e-5 or abs(hi[1]-lo[1]-.1)<1e-5):
   trimcount+=1
   for i in ids:
    vs[i][0]=max(-2.995,min(2.995,vs[i][0]))
    if abs(vs[i][2]+.4)<1e-5:vs[i][2]=-.23
    lines[vlines[i]]='v '+' '.join(f'{c:.6f}' for c in vs[i])
 assert trimcount in [0,3],(path,trimcount)
 assert count in [0,8],(path,count)
 if count or trimcount:path.write_text('\n'.join(lines)+'\n')
 print(path.name,'shortened quoins:',count,'inset trim caps:',trimcount)
