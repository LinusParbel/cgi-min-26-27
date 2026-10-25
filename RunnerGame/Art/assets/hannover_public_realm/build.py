"""Georeferenced public realm v2; all runtime pixels authored, aerial reference only."""
from pathlib import Path
import sys,json,math,hashlib,shutil,heapq
A=Path(__file__).resolve().parent; ROOT=A.parents[3]
sys.path.insert(0,str(ROOT/'.model-research/hannover_route/python_deps'))
import numpy as np
import shapely as S
from shapely.geometry import Polygon,LineString,Point,shape,box
from shapely.ops import unary_union
from PIL import Image,ImageDraw
OUT=A/'out';OUT.mkdir(exist_ok=True)
previousMap=json.loads((OUT/'map.json').read_text()) if (OUT/'map.json').is_file() else {}
SRC=A.parent/'hannover_route';REF=A.parent/'hannover_route_reference';OLD=A.parent/'hannover_pedestrian_blockout'
feats=json.loads((SRC/'footprints.geojson').read_text())['features'];buildings=unary_union([shape(f['geometry']) for f in feats])
proposal=json.loads((REF/'waypoint-proposal.json').read_text())
def geo(p):return (549750+p[0]*.5,5803400-p[1]*.5)
# Official north-up 0.5m overview image pixels, hand interpreted. No Google geometry.
realm_pixels=[(1220,390),(1410,495),(1470,584),(1280,675),(1238,734),(1160,830),(1116,900),(1030,912),(986,870),(715,798),(578,751),(484,703),(361,650),(288,677),(204,683),(163,620),(184,530),(229,460),(294,489),(318,571),(405,604),(490,644),(565,669),(620,690),(727,730),(857,771),(977,817),(1000,803),(1035,760),(1138,605),(1215,483)]
realm=Polygon([geo(p) for p in realm_pixels]).buffer(0)
main_pixels=[(1236,628),(1059,872),(1074,881),(1250,639)]
main=Polygon([geo(p) for p in main_pixels]);forecourt=Polygon(proposal['opening_polygons'][1]['coordinates'])
holes=unary_union([main,forecourt]); clock=Point(550270,5802950)
def local(p):return [round(p[0]-550000,4),round(-(p[1]-5803000),4)]
route=json.loads((OLD/'out/route.json').read_text());shutil.copyfile(OLD/'out/route.json',OUT/'route.json')
# Preserve the exact provisional controls, reconstruct runtime's 20-percent quadratic corners.
nodes=[(p['x']+550000,5803000-p['z']) for p in route['points']]
def rounded(nodes):
 result=[nodes[0]]
 for i in range(1,len(nodes)-1):
  a,b,c=map(np.array,nodes[i-1:i+2]);trim=.2*min(np.linalg.norm(a-b),np.linalg.norm(c-b));en=b+(a-b)/np.linalg.norm(a-b)*trim;ex=b+(c-b)/np.linalg.norm(c-b)*trim
  result.extend([tuple(en)])
  count=max(2,math.ceil((np.linalg.norm(en-b)+np.linalg.norm(ex-b))/.15))
  for t in np.linspace(0,1,count+1)[1:]:result.append(tuple((1-t)**2*en+2*(1-t)*t*b+t*t*ex))
 result.append(nodes[-1]);return LineString(result)

# Preserve old blocked route for a strong regression fixture.
oldcurve=rounded(nodes);oldtube=oldcurve.buffer(1.8,resolution=16)
public=realm.difference(buildings).difference(holes)
x0,y0,x1,y1=buildings.bounds
extent=box(x0-25,y0-25,x1+25,y1+25)
context=extent.difference(public).difference(holes)
# Search every upper corridor in full public polygon; never reshape source obstacles.
def solve_route(margin):
 obstacles=unary_union([buildings.buffer(margin),holes.buffer(margin+.3),clock.buffer(margin+1.5)])
 allowed=public.buffer(-margin).difference(obstacles)
 bx,by,ex,ey=public.bounds;step=.5
 xs=np.arange(math.floor(bx),ex+step,step);ys=np.arange(math.floor(by),ey+step,step)
 xx,yy=np.meshgrid(xs,ys);free=S.contains(allowed,S.points(xx.ravel(),yy.ravel())).reshape(xx.shape)
 def nearest(p):
  dd=(xx-p[0])**2+(yy-p[1])**2;dd[~free]=np.inf
  return tuple(np.unravel_index(np.argmin(dd),dd.shape))
 def astar(a,b):
  a=nearest(a);b=nearest(b);queue=[(0,a)];cost={a:0};prev={}
  while queue:
   _,u=heapq.heappop(queue)
   if u==b:break
   for dy,dx in ((0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)):
    v=(u[0]+dy,u[1]+dx)
    if not(0<=v[0]<len(ys) and 0<=v[1]<len(xs)) or not free[v]:continue
    if dx and dy and (not free[u[0],v[1]] or not free[v[0],u[1]]):continue
    c=cost[u]+math.hypot(dx,dy)
    if c<cost.get(v,1e30):cost[v]=c;prev[v]=u;heapq.heappush(queue,(c+math.hypot(v[0]-b[0],v[1]-b[1]),v))
  else:raise RuntimeError('No connected upper public corridor at margin '+str(margin))
  r=[b]
  while r[-1]!=a:r.append(prev[r[-1]])
  return [(float(xs[x]),float(ys[y])) for y,x in r[::-1]]
 raw=[]
 for a,b in zip([(550420,5803165),(550270,5802949)],[(550270,5802949),(549850,5803115)]):
  seg=astar(a,b);raw.extend(seg if not raw else seg[1:])
 controls=[raw[0]];i=0
 while i<len(raw)-1:
  j=len(raw)-1
  while j>i+1:
   if allowed.covers(LineString([raw[i],raw[j]])):break
   j-=1
  controls.append(raw[j]);i=j
 return controls
candidates=[]
for search_margin in [5,4,3,2.4]:
 try:
  trial=solve_route(search_margin);trialcurve=rounded(trial);trialtube=trialcurve.buffer(1.8,resolution=16)
  coords=np.array(trialcurve.coords);radii=[]
  for a,b,c in zip(coords,coords[1:],coords[2:]):
   ab=np.linalg.norm(a-b);bc=np.linalg.norm(b-c);ac=np.linalg.norm(a-c);cross=abs(np.cross(b-a,c-a))
   if cross>1e-8:radii.append(ab*bc*ac/(2*cross))
  radius=min(radii) if radii else 1e9
  valid=bool(public.buffer(.0001).covers(trialtube) and trialtube.distance(buildings)>=.3 and trialtube.distance(holes)>=.5 and radius>=4)
  candidates.append({'margin':search_margin,'nodes':trial,'radius':float(radius),'valid':valid,'openingDistance':trialtube.distance(holes),'support':public.buffer(.0001).covers(trialtube)})
  if valid:break
 except RuntimeError as e:candidates.append({'margin':search_margin,'failure':str(e)})
# Raster stair-step visibility can leave short intermediate legs. Remove redundant
# controls only when the complete rounded physical tube remains legal.
from itertools import combinations
for base_candidate in list(candidates):
 if 'nodes' not in base_candidate:continue
 initial=base_candidate['nodes']
 for count in [1,2,3]:
  found=False
  for removed in combinations(range(1,len(initial)-1),count):
   trial=[p for i,p in enumerate(initial) if i not in removed];trialcurve=rounded(trial);trialtube=trialcurve.buffer(1.8,resolution=16)
   if not public.buffer(.0001).covers(trialtube) or trialtube.distance(buildings)<.3 or trialtube.distance(holes)<.5 or trialtube.distance(clock)<1.235:continue
   coords=np.array(trialcurve.coords);radii=[]
   for a,b,c in zip(coords,coords[1:],coords[2:]):
    cross=abs(np.cross(b-a,c-a))
    if cross>1e-8:radii.append(np.linalg.norm(a-b)*np.linalg.norm(b-c)*np.linalg.norm(a-c)/(2*cross))
   radius=float(min(radii)) if radii else 1e9
   if radius<4:continue
   candidates.append({'margin':base_candidate['margin'],'nodes':trial,'radius':radius,'valid':True,'removedRasterControls':removed,'openingDistance':trialtube.distance(holes),'support':True});found=True;break
  if found:break
# Broad Kr?pcke turns need space beyond the lip, rather than following shortest
# raster path tightly around its tip. Search nearby control positions in the plaza.
for base_candidate in list(candidates):
 if 'nodes' not in base_candidate or base_candidate.get('valid'):continue
 initial=base_candidate['nodes'];found=False
 for omitted in range(1,len(initial)-1):
  simplified=[p for i,p in enumerate(initial) if i!=omitted]
  for j,p in enumerate(simplified[1:-1],1):
   if Point(p).distance(clock)>40:continue
   for de,dn in [(0,-2),(0,-4),(0,-6),(2,-4),(-2,-4),(2,-6),(-2,-6)]:
    trial=[list(q) for q in simplified];trial[j]=[p[0]+de,p[1]+dn]
    trialcurve=rounded(trial);trialtube=trialcurve.buffer(1.8,resolution=16)
    if not public.buffer(.0001).covers(trialtube) or trialtube.distance(buildings)<.3 or trialtube.distance(holes)<.5 or trialtube.distance(clock)<1.235:continue
    coords=np.array(trialcurve.coords);radii=[]
    for a,b,c in zip(coords,coords[1:],coords[2:]):
     cross=abs(np.cross(b-a,c-a))
     if cross>1e-8:radii.append(np.linalg.norm(a-b)*np.linalg.norm(b-c)*np.linalg.norm(a-c)/(2*cross))
    radius=float(min(radii)) if radii else 1e9
    if radius<4:continue
    candidates.append({'margin':base_candidate['margin'],'nodes':trial,'radius':radius,'valid':True,'removedRasterControls':[omitted],'plazaControlOffset_m':[de,dn],'openingDistance':trialtube.distance(holes),'support':True});found=True;break
   if found:break
  if found:break
(A/'route-search.json').write_text(json.dumps(candidates,indent=2))
valids=[c for c in candidates if c.get('valid')]
assert valids, candidates
chosen=valids[0];nodes=chosen['nodes'];curve=rounded(nodes);tube=curve.buffer(1.8,resolution=16)
route['points']=[dict(zip(('x','z'),local(p))) for p in nodes]
route['metadata'].update({'adjustedSourceCoordinates':nodes,'method':'0.5m A* across full official-aerial public polygon; buffered source obstacles, visibility simplification, runtime 20% quadratic corners','minimumTurnRadius_m':chosen['radius'],'searchMargin_m':chosen['margin'],'laneSpacing':1.5,'playerHalfWidth':.3})
(OUT/'route.json').write_text(json.dumps(route,indent=2),encoding='utf-8')
# Wide boulevard central field and plaza fields, not the gameplay centerline.
georg=LineString([geo(p) for p in [(244,604),(350,635),(548,709),(746,775),(1016,868)]])
field=public.intersection(georg.buffer(9,cap_style=2))
plazas=public.intersection(unary_union([Polygon([geo(p) for p in [(1190,396),(1410,495),(1470,584),(1290,675),(1190,570)]]),Polygon([geo(p) for p in [(163,620),(184,530),(229,460),(294,489),(318,571),(361,650),(288,677),(204,683)]])]))
bands=public.boundary.buffer(.65).intersection(public).difference(plazas)
# Photo01 establishes gray central paving plus red longitudinal strips under
# both tree ranks. Geometry follows inferred aerial-fit tree rows, not photo pixels.
row_source=json.loads((A/'paired-avenue-placements.json').read_text())
row_records=sorted(row_source['rows'],key=lambda r:r['stationX'])
row_axes=[[],[]];centre=[]
for r in row_records:
 pair=r['pairLocalXZ'];north,south=(pair[0],pair[1]) if r['segment']=='west' else (pair[1],pair[0])
 for i,q in enumerate([north,south]):row_axes[i].append((q[0]+550000,5803000-q[1]))
 centre.append((550000+(pair[0][0]+pair[1][0])/2,5803000-(pair[0][1]+pair[1][1])/2))
row_lines=[LineString(axis) for axis in row_axes]
georg_material_area=public.intersection(LineString(centre).buffer(12,cap_style=2)).difference(plazas).difference(bands)
brick=unary_union([axis.buffer(1,cap_style=2,join_style=2) for axis in row_lines]).intersection(georg_material_area)
field=unary_union([field,georg_material_area]).difference(plazas).difference(bands).difference(brick)
base=public.difference(field).difference(plazas).difference(bands).difference(brick)
zones=[context,base,field,plazas,bands,brick]
# Original procedural atlas: context, warm granite, gray Georg pavers,
# light plaza slabs, charcoal boundary bands, terracotta running-bond brick.
colors=[(124,126,123),(181,177,166),(160,164,162),(193,190,180),(91,94,91),(155,87,68)]
im=Image.new('RGB',(256*len(colors),256));draw=ImageDraw.Draw(im)
for k,c in enumerate(colors):
 draw.rectangle((k*256,0,k*256+255,255),fill=c)
 rw,ch=(8,4) if k==5 else ((20,10) if k==2 else ((128,64) if k==3 else (64,32)))
 for row in range(0,256,ch):
  for col in range(-rw,256,rw):
   x=col+(rw//2 if (row//ch)%2 else 0)
   if x+rw-1<0 or x>255:continue
   draw.rectangle((k*256+max(0,x),row,k*256+min(255,x+rw-1),min(255,row+ch-1)),outline=tuple(max(0,v-19) for v in c))
im.save(OUT/'PedestrianGround.png')
verts=[];uv=[];norms=[];faces=[];swatch=0;tile=(0,0)
def tri(vs,rail=False):
 v=np.array(vs,float);n=np.cross(v[1]-v[0],v[2]-v[0]);length=np.linalg.norm(n)
 if length<1e-8:return
 n/=length;ids=[]
 for q in v:
  verts.append(q.tolist());u=(q[0]-tile[0])/8;w=(q[2]-tile[1])/8
  uv.append(((4.5/len(colors),.5) if rail else ((swatch+min(.999,max(.001,u)))/len(colors),min(.999,max(.001,w)))))
  ids.append(len(verts))
 norms.append(n.tolist());faces.append((ids,len(norms)))
def xyz(p,y):x,z=local(p);return [x,y,z]
def surface(poly,y):
 for t in S.constrained_delaunay_triangles(poly).geoms:
  vs=[xyz(p,y) for p in list(t.exterior.coords)[:3]]
  if np.cross(np.array(vs[1])-vs[0],np.array(vs[2])-vs[0])[1]<0:vs.reverse()
  tri(vs)
for swatch,zone in enumerate(zones):
 bx,by,ex,ey=zone.bounds
 for e in range(math.floor(bx/8)*8,math.ceil(ex/8)*8,8):
  for n in range(math.floor(by/8)*8,math.ceil(ey/8)*8,8):
   part=zone.intersection(box(e,n,e+8,n+8));tile=(e-550000,5803000-(n+8))
   for poly in (part.geoms if hasattr(part,'geoms') else [part]):
    if poly.geom_type=='Polygon' and poly.area>.0001:surface(poly,-1)
for poly in holes.geoms:
 # Lower promenade floor gets original warm paving and bounded UV cells.
 swatch=1
 bx,by,ex,ey=poly.bounds
 for e in range(math.floor(bx/8)*8,math.ceil(ex/8)*8,8):
  for n in range(math.floor(by/8)*8,math.ceil(ey/8)*8,8):
   part=poly.intersection(box(e,n,e+8,n+8));tile=(e-550000,5803000-(n+8))
   if part.geom_type=='Polygon' and part.area>.0001:surface(part,-4)
 swatch=0
 coords=list(poly.exterior.coords)
 for a,b in zip(coords,coords[1:]):
  tri([xyz(a,-1),xyz(b,-4),xyz(b,-1)]);tri([xyz(a,-1),xyz(a,-4),xyz(b,-4)])
  # Guardrail posts + horizontal supported continuous beam, on upper lip.
  delta=np.array(b)-a;length=np.linalg.norm(delta);n=np.array([-delta[1],delta[0]])/length
  mid=(np.array(a)+b)/2
  if poly.contains(Point(mid+n*.1)):n=-n
  aa=np.array(a)+n*.16;bb=np.array(b)+n*.16
  def beam(p,q,lo,hi,w):
   dd=np.array(q)-p;nn=np.array([-dd[1],dd[0]])/np.linalg.norm(dd)*w/2
   ring=[np.array(p)+nn,np.array(q)+nn,np.array(q)-nn,np.array(p)-nn]
   for j in range(4):
    k=(j+1)%4;tri([xyz(ring[j],lo),xyz(ring[k],hi),xyz(ring[k],lo)],True);tri([xyz(ring[j],lo),xyz(ring[j],hi),xyz(ring[k],hi)],True)
   tri([xyz(ring[0],hi),xyz(ring[2],hi),xyz(ring[1],hi)],True);tri([xyz(ring[0],hi),xyz(ring[3],hi),xyz(ring[2],hi)],True)
  # Source opening/building conflicts remain recorded; omit unsupported rail spans.
  supported=LineString([aa,bb]).difference(buildings.buffer(.12))
  for span in (supported.geoms if hasattr(supported,'geoms') else [supported]):
   if span.is_empty or span.length<.2:continue
   sa=np.array(span.coords[0]);sb=np.array(span.coords[-1]);beam(sa,sb,.02,.12,.09)
   for t in np.linspace(0,1,max(2,math.ceil(span.length/2)+1)):
    p=sa+(sb-sa)*t;beam(p,p+delta/length*.08,-1,.12,.08)
with (OUT/'PedestrianGround.obj').open('w') as f:
 for v in verts:f.write('v '+' '.join(map(str,v))+'\n')
 for v in uv:f.write('vt '+' '.join(map(str,v))+'\n')
 for v in norms:f.write('vn '+' '.join(map(str,v))+'\n')
 f.write('o pedestrian_ground\n')
 for ids,n in faces:f.write('f '+' '.join(f'{i}/{i}/{n}' for i in ids)+'\n')
(OUT/'PedestrianGround_parts.json').write_text(json.dumps({'texture':'PedestrianGround.png','parts':[{'name':'pedestrian_ground','obj':'PedestrianGround.obj','pivot':[0,0,0]}]},indent=2))
# Normalize each copied building to the same flat datum using measured GroundSurface minimum.
mapping=json.loads((SRC/'buildings.json').read_text()); shifts={f['properties']['obj_name']:54-f['properties']['ground_height_min'] for f in feats}
lines=(SRC/'out/HannoverRoute.obj').read_text().splitlines();vv=[list(map(float,l.split()[1:])) for l in lines if l.startswith('v ')];owner={};name=None
for l in lines:
 if l.startswith('o '):name=l[2:]
 if l.startswith('f '):
  for v in l.split()[1:]:owner[int(v.split('/')[0])-1]=name
k=0;new=[]
for l in lines:
 if l.startswith(('mtllib ','usemtl ')):continue
 if l.startswith('v '):
  v=vv[k];v[1]+=shifts[owner[k]];l='v '+' '.join(f'{x:.6f}' for x in v);k+=1
 new.append(l)
(OUT/'HannoverRoute.obj').write_text('\n'.join(new)+'\n')
for name in ['HannoverRoute.png','HannoverRoute_parts.json']:shutil.copyfile(SRC/'out'/name,OUT/name)
(OUT/'map.json').write_text(json.dumps({'cityManifest':'HannoverRoute_parts.json','groundManifest':'PedestrianGround_parts.json','route':'route.json','groundY':-1,'clock':dict(zip(('x','z'),local(clock.coords[0]))),'title':route['title']},indent=2),encoding='utf-8')
# Tree canopy centres interpreted from leafless March 2025 aerial, 1.5-3m uncertainty.
tree_pixels=[(350,655),(375,664),(402,674),(430,684),(458,693),(486,703),(513,712),(541,722),(569,731),(597,740),(625,750),(653,759),(681,768),(709,778),(737,787),(765,797),(793,806),(821,815),(849,825),(877,834),(905,843),(933,853),(961,862),(365,675),(393,684),(421,694),(449,703),(477,713),(505,722),(533,731),(561,741),(589,750),(617,759),(645,769),(673,778),(701,788),(729,797),(757,806),(785,816),(813,825),(841,834),(869,844),(897,853),(925,863),(276,573),(263,543),(248,514),(222,594),(258,636),(303,641),(1283,523),(1304,541),(1330,561),(1363,578),(1304,608)]
tree_pixels += [(350,615),(381,627),(412,639),(443,651),(475,663),(507,675),(537,686),(568,697),(598,709),(628,719),(658,730),(688,740),(719,751),(747,760),(775,772),(804,781),(834,793),(861,802),(889,813),(917,822),(947,834),(974,842)]
props=[];rejected=[]
for p in tree_pixels:
 q=Point(geo(p))
 if not public.covers(q) or q.distance(buildings)<2 or q.distance(tube)<2 or q.distance(holes)<2:rejected.append(p);continue
 x,z=local(q.coords[0]);props.append({'kind':'tree','x':x,'z':z,'yaw':0,'scale':1})
mp=json.loads((OUT/'map.json').read_text());mp['sceneProps']=props;mp.update({k:v for k,v in previousMap.items() if k not in ['cityManifest','groundManifest','route','groundY','clock','sceneProps']});mp.setdefault('title','Hannover public realm v2 (facades pending)');(OUT/'map.json').write_text(json.dumps(mp,indent=2),encoding='utf-8')
measure={'crs':'EPSG:25832','localTransform':'X=E-550000; Z=5803000-N','source':'../hannover_route_reference/overview-clean.png','pixelTransform':[.5,0,549750,0,-.5,5803400],'realmPixels':realm_pixels,'mainOpeningPixels':main_pixels,'treePixels':tree_pixels,'rejectedTreePixels':rejected,'acceptedSceneProps':props,'uncertainty_m':{'facadePavingEdge':3,'openingLip':2,'treeCenter':3},'method':'Manual interpretation of licensed aerial. User Google markings used for scope only. March leafless trees and shadows limit precision.'}
(A/'placements-source.json').write_text(json.dumps(measure,indent=2))
checks={'publicArea_m2':public.area,'backgroundArea_m2':context.area,'routeLength_m':curve.length,'minimumTurnRadius_m':chosen['radius'],'oldRouteBlockedByRevisedOpening':oldtube.intersects(holes),'oldRouteOpeningOverlap_m2':oldtube.intersection(holes).area,'negativeBuildingRouteFixtureDetected':not buildings.is_empty and LineString([buildings.representative_point(),clock]).buffer(1.8).intersects(buildings),'routeBuildingClearance_m':tube.distance(buildings),'routeOpeningClearance_m':tube.distance(holes),'routeSupported':public.buffer(.01).covers(tube),'openingTopGroundOverlap_m2':sum(z.intersection(holes).area for z in zones),'zonePairOverlap_m2':sum(z.intersection(w).area for i,z in enumerate(zones) for w in zones[i+1:]),'entireCityExtentSupportedExceptOpenings':unary_union(zones).union(holes).symmetric_difference(extent).area<.001,'negativeOpeningFixtureDetected':not unary_union(zones).covers(main.representative_point()),'negativeOutsideRealmFixtureDetected':not public.covers(Point(x0-20,y0-20)),'acceptedTrees':len(props),'rejectedTrees':len(rejected),'triangles':len(faces),'limitations':['2010 generalized building footprints vs March 2025 aerial conflict; no fabricated survey certainty','Opening lip manually revised from legal aerial, approximately +/-2m; lower depth remains assumed 3m','Route recomputed across full public polygon with complete swept-tube clearance and broad runtime-rounded corners','Existing city meshes remain grey LoD2, facades pending','Paving patterns authored representative zones, not exact stone-by-stone reconstruction','No surveyed terrain; flat upper datum H54, engine Y=-1']}
assert checks['oldRouteBlockedByRevisedOpening']
assert checks['negativeBuildingRouteFixtureDetected']
assert checks['routeSupported']
assert checks['routeOpeningClearance_m']>=.5
assert checks['routeBuildingClearance_m']>=.3
assert checks['minimumTurnRadius_m']>=4
assert checks['openingTopGroundOverlap_m2']<.001
assert checks['zonePairOverlap_m2']<.001
assert checks['entireCityExtentSupportedExceptOpenings']
assert checks['negativeOpeningFixtureDetected'] and checks['negativeOutsideRealmFixtureDetected']
(A/'REPORT.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
shutil.copyfile(SRC/'CREDITS.txt',A/'SOURCE_CREDITS.txt')
with (A/'SOURCE_CREDITS.txt').open('a',encoding='utf-8') as f:f.write('\nDigitale Orthophotos 2025, Landeshauptstadt Hannover, FB Planen und Stadtentwicklung, Bereich Geoinformation. CC BY 4.0. https://creativecommons.org/licenses/by/4.0/\nSource https://opengeodata.hannover-stadt.de/DOP20_Teil_Mitte.zip ; survey 2025-03-06. Manual interpretation of paving edges, opening lip, tree centres; no aerial or Google pixels in runtime.\nOriginal procedural texture atlas by project authors.\n')
shutil.copyfile(SRC/'provenance.json',A/'city-source-provenance.json');shutil.copyfile(OLD/'provenance.json',A/'city-normalization-provenance.json');shutil.copyfile(REF/'overview-georef.json',A/'aerial-reference-provenance.json')
(A/'spec.json').write_text(json.dumps({'version':2,'groundY':-1,'lowerY':-4,'pavingZones':['context','facade-edge granite','boulevard field','plaza slabs','edge bands'],'routeStatus':'replanned v2, 1.5m lane spacing and verified swept tube','build':'python RunnerGame/Art/assets/hannover_public_realm/build.py','sourceGeometry':'../hannover_route/footprints.geojson'},indent=2))
# Schematic QA preview uses metric aspect and exported geometry. Aerial is not composited.
bounds=(549800,5802890,550500,5803210);view=Image.new('RGB',(1750,800),'#777b77');d=ImageDraw.Draw(view)
def pix(p):return ((p[0]-bounds[0])*2.5,800-(p[1]-bounds[1])*2.5)
def polygons(g):return g.geoms if hasattr(g,'geoms') else [g]
for k,zone in enumerate(zones):
 for poly in polygons(zone):
  if poly.geom_type!='Polygon':continue
  d.polygon([pix(q) for q in poly.exterior.coords],fill=colors[k])
  for ring in poly.interiors:d.polygon([pix(q) for q in ring.coords],fill='#777b77')
for f in feats:
 poly=shape(f['geometry']);d.polygon([pix(q) for q in poly.exterior.coords],fill='#777f88',outline='#535960')
for poly in polygons(holes):d.polygon([pix(q) for q in poly.exterior.coords],fill='#292f31',outline='#ddddcf')
for p in props:
 u,v=pix((p['x']+550000,5803000-p['z']));d.ellipse((u-8,v-8,u+8,v+8),fill='#527047',outline='#32492c')
d.line([pix(q) for q in curve.coords],fill='#b85c40',width=3)
d.text((20,20),'PUBLIC REALM V2 | grey buildings still await facades | rust line: verified v2 route',fill='white')
view.save(A/'overview.png')

shutil.copyfile(SRC/'out/HannoverRoute.obj',A/'HannoverRoute.raw-source.obj')
(A/'provenance.json').write_text(json.dumps({'version':2,'runtimePixels':'entirely original procedural atlas','googleUse':'user scope only, no traced geometry or pixels','geometrySource':'official city LoD2 footprints plus manual interpretation of official CC BY 4.0 DOP20','sourceCitySha256':hashlib.sha256((SRC/'out/HannoverRoute.obj').read_bytes()).hexdigest(),'derivativeCitySha256':hashlib.sha256((OUT/'HannoverRoute.obj').read_bytes()).hexdigest(),'aerialGeoref':'aerial-reference-provenance.json','placements':'placements-source.json','sourceCredits':'SOURCE_CREDITS.txt','groundMethod':'disjoint authored public paving polygons and full map context, constrained triangulation per UV cell; all upper holes removed','route':'recomputed v2; old blocked route is negative fixture; full tube and >=4m turn radius checked'},indent=2))
