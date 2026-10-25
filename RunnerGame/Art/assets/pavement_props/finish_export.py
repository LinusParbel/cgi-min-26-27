"""Deterministic serialized triangle cleanup; no texture mutation."""
from pathlib import Path
H=Path(__file__).resolve().parent
def clean():
 removed={}
 for path in (H/'out').glob('*.obj'):
  vs=[];out=[];n=0
  for line in path.read_text().splitlines():
   a=line.split()
   if a and a[0]=='v':vs.append(list(map(float,a[1:])))
   if a and a[0]=='f':
    x,y,z=[vs[int(t.split('/')[0])-1] for t in a[1:]];u=[y[i]-x[i] for i in range(3)];v=[z[i]-x[i] for i in range(3)]
    if sum((u[(i+1)%3]*v[(i+2)%3]-u[(i+2)%3]*v[(i+1)%3])**2 for i in range(3))<=1e-16:n+=1;continue
   out.append(line)
  path.write_text('\n'.join(out)+'\n');removed[path.name]=n
 print(removed)
if __name__=='__main__':clean()
