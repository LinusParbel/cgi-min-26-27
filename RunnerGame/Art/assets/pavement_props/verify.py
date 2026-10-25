"""Independent actual-OBJ contract plus destructive negative fixtures on parsed copies."""
import json,math,copy
from pathlib import Path
from PIL import Image
H=Path(__file__).resolve().parent
RANGES={'rack':[(.14,.16),(.87,.89),(.79,.81)],'table':[(.69,.71),(.69,.71),(.739,.741)],'chair':[(.449,.451),(.43,.49),(.81,.83)]}
def load(path):
 d={'v':[],'vt':[],'vn':[],'f':[]}
 for ln in path.read_text().splitlines():
  a=ln.split()
  if a and a[0] in d:d[a[0]].append([list(map(int,x.split('/'))) for x in a[1:]] if a[0]=='f' else list(map(float,a[1:])))
 return d
def check(k,d):
 v=d['v'];assert v and d['f'];lo=[min(p[i] for p in v) for i in range(3)];hi=[max(p[i] for p in v) for i in range(3)]
 assert abs(lo[1])<1e-5,(k,'ground',lo)
 # Engine is Y up; map sizes to source X,Y,Z.
 dims=[hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]]
 for size,(a,b) in zip(dims,RANGES[k]):assert a<=size<=b,(k,dims)
 assert abs(hi[0]+lo[0])<.001 and abs(hi[2]+lo[2])<.08,(k,'off-centre pivot')
 assert len(d['f'])<({'rack':3000,'table':3000,'chair':2000}[k])
 for key in ['v','vt','vn']:assert all(math.isfinite(c) for p in d[key] for c in p)
 assert all(-1e-6<=c<=1.000001 for p in d['vt'] for c in p)
 assert all(abs(sum(c*c for c in n)-1)<.01 for n in d['vn'])
 for face in d['f']:
  assert len(face)==3
  assert all(len(i)==3 and all(0<a<=len(d[t]) for a,t in zip(i,['v','vt','vn'])) for i in face)
  a,b,c=[v[i[0]-1] for i in face];u=[b[i]-a[i] for i in range(3)];w=[c[i]-a[i] for i in range(3)]
  cross=[u[(i+1)%3]*w[(i+2)%3]-u[(i+2)%3]*w[(i+1)%3] for i in range(3)]
  assert sum(x*x for x in cross)>1e-16,'collapsed triangle'
 return {'triangles':len(d['f']),'engine_bounds':{'min':lo,'max':hi},'source_dimensions':dims}
def run():
 atlas=Image.open(H/'out/PROP_Pavement.png');assert atlas.size==(1024,1024) and atlas.convert('RGBA').getextrema()[3]==(255,255)
 all_data={k:load(H/'out'/('PROP_Pavement_'+k+'.obj')) for k in RANGES}
 report={k:check(k,d) for k,d in all_data.items()};assert report['table']['triangles']+2*report['chair']['triangles']<6000
 negative=[]
 for label,mutate in [('raised_ground',lambda d:d['v'].__setitem__(slice(None),[[x,y+.1,z] for x,y,z in d['v']])),('bad_uv',lambda d:d['vt'][0].__setitem__(0,1.5)),('bad_normal',lambda d:d['vn'][0].__setitem__(slice(None),[0,0,0])),('invalid_index',lambda d:d['f'][0][0].__setitem__(0,999999)),('collapsed_face',lambda d:d['f'].__setitem__(0,[d['f'][0][0]]*3))]:
  d=copy.deepcopy(all_data['table']);mutate(d)
  try:check('table',d)
  except AssertionError:negative.append(label)
  else:raise AssertionError('Negative accepted: '+label)
 result={'parts':report,'table_two_chairs_triangles':report['table']['triangles']+2*report['chair']['triangles'],'opaque_shared_1024':True,'valid_geometry_uv_normals_indices':True,'negative_fixtures_rejected':negative}
 (H/'out/export_checks.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':run()
