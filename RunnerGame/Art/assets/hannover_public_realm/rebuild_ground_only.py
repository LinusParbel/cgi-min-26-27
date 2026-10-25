"""Bounded rebuild: ground OBJ/atlas only; all map metadata, props, route and city are preserved."""
from pathlib import Path
import json,hashlib
A=Path(__file__).resolve().parent
s=(A/'build.py').read_text();ns={'__file__':str(A/'build.py')}
protected=['map.json','route.json','HannoverRoute.obj','KroepckeFacades.obj'];before={f:hashlib.sha256((A/'out'/f).read_bytes()).hexdigest() for f in protected}
exec(s[:s.index("route=json.loads")],ns)
exec("public=realm.difference(buildings).difference(holes)\nx0,y0,x1,y1=buildings.bounds\nextent=box(x0-25,y0-25,x1+25,y1+25)\ncontext=extent.difference(public).difference(holes)",ns)
exec(s[s.index('# Wide boulevard'):s.index('# Normalize each')],ns)
for f,h in before.items():assert hashlib.sha256((A/'out'/f).read_bytes()).hexdigest()==h
zones=ns['zones'];holes=ns['holes'];overlap=sum(a.intersection(b).area for i,a in enumerate(zones) for b in zones[i+1:]);assert overlap<1e-5
assert sum(z.intersection(holes).area for z in zones)<1e-6
assert ns['unary_union'](zones).union(holes).symmetric_difference(ns['extent']).area<.001
source=json.loads((A.parent/'hannover_street_references/refs.json').read_text())['photos'][0]
r={'materialReference':source,'sourceUse':'Architectural material feature only: gray center paving and red longitudinal tree-row strips. All runtime pixels original procedural, no photo or aerial pixels. Historical2019 reference, not current stone survey.','brickBandWidth_m':2,'brickArea_m2':ns['brick'].area,'grayGeorgPavingArea_m2':ns['field'].area,'atlasSwatches':len(ns['colors']),'zoneOverlap_m2':overlap,'topGroundOverOpenings_m2':0,'triangles':len(ns['faces']),'protectedSha256':before,'allProtectedFilesUnchanged':True,'scope':'Ground material zones and original atlas only; no route/tree/city/metadata changes'}
(A/'paving-material-report.json').write_text(json.dumps(r,indent=2));old=json.loads((A/'REPORT.json').read_text());old['triangles']=len(ns['faces']);old['pavingMaterialUpdate']='paving-material-report.json';(A/'REPORT.json').write_text(json.dumps(old,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ['materialReference','protectedSha256']},indent=2))
# Color-only schematic of exact disjoint zones for material review.
view=ns['Image'].new('RGB',(1400,700),'#777777');draw=ns['ImageDraw'].Draw(view);bounds=(549850,5802920,550270,5803130)
def pix(q):return ((q[0]-bounds[0])*3.2,700-(q[1]-bounds[1])*3.2)
for c,z in zip(ns['colors'],zones):
 for poly in (z.geoms if hasattr(z,'geoms') else [z]):
  if poly.geom_type=='Polygon':
   draw.polygon([pix(q) for q in poly.exterior.coords],fill=c)
   for ring in poly.interiors:draw.polygon([pix(q) for q in ring.coords],fill='#777777')
for prop in json.loads((A/'out/map.json').read_text())['sceneProps']:
 x,y=pix((prop['x']+550000,5803000-prop['z']));draw.ellipse((x-5,y-5,x+5,y+5),fill='#3e5c3b')
view.save(A/'paving-material-overview.png')
