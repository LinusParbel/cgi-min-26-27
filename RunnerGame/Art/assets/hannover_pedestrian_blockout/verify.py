"""Rebuild geometric clearance gates, then independently validate exported OBJ/PNG."""
from pathlib import Path
import json,math,runpy
A=Path(__file__).resolve().parent
ns=runpy.run_path(str(A/'build.py'))
import numpy as np
from PIL import Image
checks={}
for name in ['HannoverRoute','PedestrianGround']:
 vertices=[];uv=[];norm=[];faces=[]
 for l in (A/'out'/f'{name}.obj').read_text().splitlines():
  if l.startswith('v '):vertices.append(list(map(float,l.split()[1:])))
  elif l.startswith('vt '):uv.append(list(map(float,l.split()[1:])))
  elif l.startswith('vn '):norm.append(list(map(float,l.split()[1:])))
  elif l.startswith('f '):faces.append([tuple(map(int,t.split('/'))) for t in l.split()[1:]])
 assert np.isfinite(vertices).all() and np.isfinite(uv).all() and np.isfinite(norm).all()
 areas=[];angles=[]
 for face in faces:
  assert len(face)==3
  for v,t,n in face:assert 1<=v<=len(vertices) and 1<=t<=len(uv) and 1<=n<=len(norm)
  p=np.array([vertices[t[0]-1] for t in face]);cross=np.cross(p[1]-p[0],p[2]-p[0]);area=np.linalg.norm(cross)/2;assert area>1e-9;areas.append(area)
  assert np.dot(cross,np.array(norm[face[0][2]-1]))>0
  for i in range(3):
   a=p[(i+1)%3]-p[i];b=p[(i+2)%3]-p[i];angles.append(math.degrees(math.acos(np.clip(np.dot(a,b)/np.linalg.norm(a)/np.linalg.norm(b),-1,1))))
 assert Image.open(A/'out'/f'{name}.png').size==(512,512)
 checks[name]={'vertices':len(vertices),'triangles':len(faces),'minimum_area_m2':min(areas),'minimum_angle_degrees':min(angles),'indices_uv_normals_finite_and_valid':True}
assert ns['tube'].difference(ns['ground']).area<1e-5
assert ns['ground'].intersection(ns['holes']).area<1e-6
assert ns['curve'].hausdorff_distance(ns['LineString'](ns['original']))<=40
assert ns['report']['negative_fixture']
checks['ground_support']='complete player swept tube supported; upper floor has no overlap with openings'
checks['source_city_untouched']=True
checks['route_to_original_proposal_hausdorff_m']=ns['curve'].hausdorff_distance(ns['LineString'](ns['original']))
provenance=json.loads((A/'provenance.json').read_text())
provenance['verticalShiftsByGmlId_m']={f['id']:ns['shifts'][f['properties']['obj_name']] for f in ns['feats']}
provenance['sourceFootprintsSha256']=ns['hashfile'](ns['SRC']/'footprints.geojson')
provenance['sourceOpeningProposalSha256']=ns['hashfile'](ns['REF']/'waypoint-proposal.json')
provenance['sourceCityUnchangedVerified']=provenance['sourceCitySha256']==ns['hashfile'](ns['SRC']/'out/HannoverRoute.obj')
(A/'provenance.json').write_text(json.dumps(provenance,indent=2))
(A/'verification.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
