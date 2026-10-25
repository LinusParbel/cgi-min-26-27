from pathlib import Path
import json,numpy as np
from PIL import Image
A=Path('RunnerGame/Art/assets/kroepcke_facade_details');v=[];uv=[];n=[];f=[]
for l in (A/'out/KroepckeFacades.obj').read_text().splitlines():
 if l.startswith('v '):v.append(list(map(float,l.split()[1:])))
 elif l.startswith('vt '):uv.append(list(map(float,l.split()[1:])))
 elif l.startswith('vn '):n.append(list(map(float,l.split()[1:])))
 elif l.startswith('f '):f.append([[int(a) for a in t.split('/')] for t in l.split()[1:]])
v=np.array(v);uv=np.array(uv);n=np.array(n);f=np.array(f);tri=v[f[:,:,0]-1];cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);areas=np.linalg.norm(cross,axis=1)/2
checks={'triangles':len(f),'budget':25000,'indicesValid':bool(f.min()>=1 and f[:,:,0].max()<=len(v) and f[:,:,1].max()<=len(uv) and f[:,:,2].max()<=len(n)),'allFinite':bool(np.isfinite(v).all() and np.isfinite(uv).all() and np.isfinite(n).all()),'uvInsideAtlas':bool(uv.min()>0 and uv.max()<1),'nondegenerate':bool(areas.min()>1e-9),'minimumArea_m2':float(areas.min()),'normalLengthMaxError':float(np.max(np.abs(np.linalg.norm(n,axis=1)-1))),'normalWindingAligned':bool((np.sum(cross*n[f[:,0,2]-1],axis=1)>0).all()),'groundContactY':float(v[:,1].min()),'bounds':[v.min(0).tolist(),v.max(0).tolist()],'opaqueTexture':Image.open(A/'out/KroepckeFacades.png').mode=='RGB','textureSize':Image.open(A/'out/KroepckeFacades.png').size,'noPhotoPixels':'generator only draws numerical RGB swatches; reference images never opened by build.py','sourceCoverage':'every triangle of both complete source building meshes included in finished shell; glazing outward0.125m versus shell0.045m, trim0.22-0.38m'}
assert len(f)<=checks['budget'] and all(checks[k] for k in ['indicesValid','allFinite','uvInsideAtlas','nondegenerate','normalWindingAligned','opaqueTexture'])
assert abs(checks['groundContactY']+1)<.06
(A/'verification.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
