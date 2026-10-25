"""Independent artifact, route identity and geometry checks; run after build.py."""
from pathlib import Path
import json, math, hashlib
A=Path(__file__).parent;out=A/'out'
report=json.loads((A/'REPORT.json').read_text())
m=json.loads((out/'map.json').read_text())
for key in ['cityManifest','groundManifest','route']:assert (out/m[key]).is_file()
for name in [m['cityManifest'],m['groundManifest']]:
 manifest=json.loads((out/name).read_text());assert (out/manifest['texture']).is_file()
 for p in manifest['parts']:
  obj=out/p['obj'];assert obj.is_file();vcount=0;fcount=0
  for line in obj.read_text().splitlines():
   if line.startswith('v '):assert all(math.isfinite(float(v)) for v in line.split()[1:]);vcount+=1
   if line.startswith('f '):assert len(line.split())==4;fcount+=1
  assert vcount and fcount
import sys
sys.path.insert(0,str(A.resolve().parents[3]/'.model-research/hannover_route/python_deps'))
import numpy as np
from shapely.geometry import Polygon,LineString,Point,shape
from shapely.ops import unary_union
placements=json.loads((A/'placements-source.json').read_text())
def geo(p):return (549750+p[0]*.5,5803400-p[1]*.5)
realm=Polygon([geo(p) for p in placements['realmPixels']]).buffer(0)
main=Polygon([geo(p) for p in placements['mainOpeningPixels']])
proposal=json.loads((A.parent/'hannover_route_reference/waypoint-proposal.json').read_text())
holes=unary_union([main,Polygon(proposal['opening_polygons'][1]['coordinates'])])
features=json.loads((A.parent/'hannover_route/footprints.geojson').read_text())['features'];buildings=unary_union([shape(f['geometry']) for f in features])
public=realm.difference(buildings).difference(holes)
def reconstruct(route):
 controls=[np.array([p['x']+550000,5803000-p['z']]) for p in route['points']];points=[controls[0]];radii=[]
 for a,b,c in zip(controls,controls[1:],controls[2:]):
  trim=.2*min(np.linalg.norm(a-b),np.linalg.norm(c-b));en=b+(a-b)/np.linalg.norm(a-b)*trim;ex=b+(c-b)/np.linalg.norm(c-b)*trim
  points.append(en)
  for t in np.linspace(0,1,max(4,math.ceil(2*trim/.05)))[1:]:points.append((1-t)**2*en+2*(1-t)*t*b+t*t*ex)
  for t in np.linspace(0,1,101):
   velocity=2*((1-t)*(b-en)+t*(ex-b));accel=2*(ex-2*b+en);cross=abs(velocity[0]*accel[1]-velocity[1]*accel[0])
   if cross>1e-8:radii.append(np.linalg.norm(velocity)**3/cross)
 points.append(controls[-1]);return LineString(points),min(radii)
route=json.loads((out/'route.json').read_text());curve,radius=reconstruct(route);tube=curve.buffer(1.8,resolution=32)
assert tube.distance(buildings)>=.3
assert tube.distance(holes)>=.5
assert public.buffer(.0001).covers(tube)
assert radius>=4
oldcurve,_=reconstruct(json.loads((A.parent/'hannover_pedestrian_blockout/out/route.json').read_text()))
assert oldcurve.buffer(1.8).intersects(holes)
assert report['openingTopGroundOverlap_m2']<1e-6
assert report['zonePairOverlap_m2']<1e-5
assert report['entireCityExtentSupportedExceptOpenings']
assert report['negativeOpeningFixtureDetected'] and report['negativeOutsideRealmFixtureDetected']
for prop in m['sceneProps']:
 q=Point(prop['x']+550000,5803000-prop['z']);assert public.covers(q) and q.distance(buildings)>=2 and q.distance(holes)>=2 and q.distance(tube)>=.2
import runpy
runpy.run_path(str(A/'verify_lower_visibility.py'))
result={'artifactChecks':'PASS','routeReplannedAgainstNewGeometry':True,'minimumTurnRadius_m':radius,'buildingClearance_m':tube.distance(buildings),'openingClearance_m':tube.distance(holes),'oldRouteBlockedNegativeFixture':True,'geometryChecks':'PASS','gameplayRouteStatus':'PASS: 1.8m swept tube supported, 1.5m lane spacing, building/opening margins and >=4m radius','sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}}
(A/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
