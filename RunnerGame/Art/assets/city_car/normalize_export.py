from pathlib import Path
import json
def normalize(A):
 m=json.loads((A/'out/VEH_CityCar_parts.json').read_text()); corrections={}
 for p in m['parts']:
  if p['name']=='body':continue
  f=A/'out'/p['obj'];lines=f.read_text().splitlines();zs=[float(l.split()[2]) for l in lines if l.startswith('v ')];offset=min(zs)+p['pivot'][2]
  corrected=[]
  for l in lines:
   if l.startswith('v '):
    t=l.split();t[2]=f'{float(t[2])-offset:.6f}';l=' '.join(t)
   corrected.append(l)
  f.write_text('\n'.join(corrected)+'\n');corrections[p['name']]=offset
 (A/'export-normalization.json').write_text(json.dumps(corrections,indent=2))
if __name__=='__main__':normalize(Path(__file__).resolve().parent)
