"""Reproducible flat pedestrian blockout; official source geometry remains untouched."""
from pathlib import Path
import sys,json,math,heapq,hashlib,shutil
A=Path(__file__).resolve().parent; ROOT=A.parents[3]
sys.path.insert(0,str(ROOT/'.model-research/hannover_route/python_deps'))
import numpy as np
import shapely as S
from shapely.geometry import Polygon,LineString,Point,shape
from shapely.ops import unary_union
from PIL import Image,ImageDraw
OUT=A/'out';OUT.mkdir(exist_ok=True)
SRC=A.parent/'hannover_route';REF=A.parent/'hannover_route_reference'
proposal=json.loads((REF/'waypoint-proposal.json').read_text()); feats=json.loads((SRC/'footprints.geojson').read_text())['features']
buildings=unary_union([shape(f['geometry']) for f in feats]);holes=unary_union([Polygon(h['coordinates']) for h in proposal['opening_polygons']])
original=[(p['easting'],p['northing']) for p in proposal['waypoints']]
# The clock coordinate is an aerial interpretation, not a surveyed point.
clock=Point(550270,5802950)
obstacles=unary_union([buildings.buffer(2.8),holes.buffer(3.0),clock.buffer(3.8)])
corridor=LineString(original).buffer(40)
step=.5; xmin,ymin,xmax,ymax=corridor.bounds
xs=np.arange(math.floor(xmin),xmax+step,step);ys=np.arange(math.floor(ymin),ymax+step,step)
xx,yy=np.meshgrid(xs,ys); pp=S.points(xx.ravel(),yy.ravel())
free=(S.contains(corridor,pp)&~S.intersects(obstacles,pp)).reshape(xx.shape)
def nearest(p):
 d=(xx-p[0])**2+(yy-p[1])**2;d[~free]=np.inf
 return tuple(np.unravel_index(np.argmin(d),d.shape))
def path(a,b):
 a=nearest(a);b=nearest(b);q=[(0,a)];cost={a:0};prev={}
 while q:
  _,u=heapq.heappop(q)
  if u==b:break
  for dy,dx in ((0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)):
   v=(u[0]+dy,u[1]+dx)
   if not(0<=v[0]<len(ys) and 0<=v[1]<len(xs)) or not free[v]:continue
   if dx and dy and (not free[u[0],v[1]] or not free[v[0],u[1]]):continue
   c=cost[u]+math.hypot(dx,dy)
   if c<cost.get(v,1e30):cost[v]=c;prev[v]=u;heapq.heappush(q,(c+math.hypot(v[0]-b[0],v[1]-b[1]),v))
 else:raise RuntimeError('No physically clear route within 40 m proposal corridor')
 r=[b]
 while r[-1]!=a:r.append(prev[r[-1]])
 return [(float(xs[x]),float(ys[y])) for y,x in r[::-1]]
# Preserve station -> upper promenade -> clock vicinity -> Georgstrasse -> Steintor order.
raw=[]
for a,b in zip([original[0],(550326,5803022),(550263,5802956),original[-1]],[(550326,5803022),(550263,5802956),original[-1]]):
 print('segment',a,b,flush=True);seg=path(a,b);raw.extend(seg if not raw else seg[1:])
# Visibility simplification retains obstacle margin for subsequent rounded corners.
nodes=[raw[0]];i=0
while i<len(raw)-1:
 j=len(raw)-1
 while j>i+1:
  line=LineString([raw[i],raw[j]])
  if not line.intersects(obstacles) and corridor.covers(line):break
  j-=1
 nodes.append(raw[j]);i=j
def rounded(nodes):
 result=[nodes[0]]
 for i in range(1,len(nodes)-1):
  a,b,c=map(np.array,nodes[i-1:i+2]);trim=.2*min(np.linalg.norm(a-b),np.linalg.norm(c-b));en=b+(a-b)/np.linalg.norm(a-b)*trim;ex=b+(c-b)/np.linalg.norm(c-b)*trim
  result.extend([tuple(en)])
  count=max(2,math.ceil((np.linalg.norm(en-b)+np.linalg.norm(ex-b))/.15))
  for t in np.linspace(0,1,count+1)[1:]:result.append(tuple((1-t)**2*en+2*(1-t)*t*b+t*t*ex))
 result.append(nodes[-1]);return LineString(result)
# Split visibility segments to bound 20%-trim control legs while allowing broad turns.
dense=[nodes[0]]
for a,b in zip(nodes,nodes[1:]):
 count=max(1,math.ceil(math.dist(a,b)/15))
 for t in np.linspace(0,1,count+1)[1:]:dense.append(tuple(np.array(a)*(1-t)+np.array(b)*t))
nodes=dense
curve=rounded(nodes)
# Check the complete swept three-lane tube; player half width .3 and spacing 1.5.
tube=curve.buffer(1.8,resolution=16)
assert tube.distance(buildings)>=.3,('building clearance',tube.distance(buildings))
assert tube.distance(holes)>=.5,('opening clearance',tube.distance(holes))
assert tube.distance(clock)>=1.235,('clock clearance',tube.distance(clock))
def local(p):return [round(p[0]-550000,4),round(-(p[1]-5803000),4)]
route={'title':'Hauptbahnhof â€“ KrÃ¶pcke â€“ Steintor','points':[dict(zip(('x','z'),local(p))) for p in nodes], 'metadata':{'crs':'EPSG:25832','sourceProposal':original,'adjustedSourceCoordinates':nodes,'method':'0.5 m A* within 40 m of aerial proposal; visibility simplification; 20 percent quadratic corner trim','laneSpacing':1.5,'playerHalfWidth':.3}}
route['title']='Hauptbahnhof \u2013 Kr\u00f6pcke \u2013 Steintor'
(OUT/'route.json').write_text(json.dumps(route,indent=2),encoding='utf-8')
# Authored paving, all pixels original. UV repeats intentionally every 4 m.
im=Image.new('RGB',(512,512),(188,179,157));d=ImageDraw.Draw(im)
for y in range(0,512,64):
 for x in range(-64,512,128):
  x+=32 if y%128 else 0;d.rectangle((x,y,x+126,y+62),fill=(190+(y//64)%3,181,160),outline=(160,151,132))
d.rectangle((0,0,7,511),fill=(57,61,58));im.save(OUT/'PedestrianGround.png')
plazas=unary_union([Point(original[0]).buffer(27),Point(550263,5802956).buffer(16),Point(original[-1]).buffer(23)])
ground=unary_union([curve.buffer(7,join_style=1),plazas,holes.buffer(4)]).difference(buildings).difference(holes)
verts=[];uv=[];norms=[];faces=[]
def tri(vs,rail=False):
 v=np.array(vs,float);n=np.cross(v[1]-v[0],v[2]-v[0]);l=np.linalg.norm(n)
 if l<1e-8:return
 n/=l;ids=[]
 for p in v:
  verts.append(p.tolist());uv.append((.007,.5) if rail else (p[0]/4,p[2]/4));ids.append(len(verts))
 norms.append(n.tolist());faces.append((ids,len(norms)))
def xyz(p,y):x,z=local(p);return [x,y,z]
def surface(poly,y):
 for t in S.constrained_delaunay_triangles(poly).geoms:
  vs=[xyz(p,y) for p in list(t.exterior.coords)[:3]]
  if np.cross(np.array(vs[1])-vs[0],np.array(vs[2])-vs[0])[1]<0:vs.reverse()
  tri(vs)
for poly in (ground.geoms if hasattr(ground,'geoms') else [ground]):surface(poly,-1)
for poly in holes.geoms:
 surface(poly,-4)
 coords=list(poly.exterior.coords)
 for a,b in zip(coords,coords[1:]):
  tri([xyz(a,-1),xyz(b,-1),xyz(b,-4)]);tri([xyz(a,-1),xyz(b,-4),xyz(a,-4)])
  # Guardrail posts + horizontal supported continuous beam, on upper lip.
  delta=np.array(b)-a;length=np.linalg.norm(delta);n=np.array([-delta[1],delta[0]])/length
  mid=(np.array(a)+b)/2
  if poly.contains(Point(mid+n*.1)):n=-n
  aa=np.array(a)+n*.16;bb=np.array(b)+n*.16
  def beam(p,q,lo,hi,w):
   dd=np.array(q)-p;nn=np.array([-dd[1],dd[0]])/np.linalg.norm(dd)*w/2
   ring=[np.array(p)+nn,np.array(q)+nn,np.array(q)-nn,np.array(p)-nn]
   for j in range(4):
    k=(j+1)%4;tri([xyz(ring[j],lo),xyz(ring[k],lo),xyz(ring[k],hi)],True);tri([xyz(ring[j],lo),xyz(ring[k],hi),xyz(ring[j],hi)],True)
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
report={'route_length_m':curve.length,'nodes':len(nodes),'building_clearance_from_player_tube_m':tube.distance(buildings),'opening_clearance_from_player_tube_m':tube.distance(holes),'clock_clearance_from_player_tube_m':tube.distance(clock),'ground_area_m2':ground.area,'ground_triangles':len(faces),'negative_fixture':LineString(original).buffer(1.8).intersects(holes.buffer(.5)),'curve':'20% trim, quadratic Bezier; sampled <=0.15 m along control polygon','assumptions':['Flat upper floor H54 / engine Y-1','Lower floor 3m below upper, not measured','Opening polygons retained exactly as manual aerial proposal','Route adjusted inside 40m corridor; no survey accuracy claimed']}
assert report['negative_fixture'];assert ground.intersection(holes).area<1e-6
(A/'REPORT.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(A/'provenance.json').write_text(json.dumps({'sourceCitySha256':hashfile(SRC/'out/HannoverRoute.obj'),'derivativeCitySha256':hashfile(OUT/'HannoverRoute.obj'),'verticalShiftsByObject_m':shifts,'operations':['GroundSurface minimum per building -> H54; footprint and height retained','Removed mtllib/usemtl lines; runtime texture manifest supplies original grey PNG'],'sources':['../hannover_route/provenance.json','../hannover_route_reference/waypoint-proposal.json'],'texture':'Original procedural beige paving; no aerial pixels'},indent=2))
# Reviewer overview with metric aspect ratio and exact used footprints/openings.
view=Image.new('RGB',(1400,700),'#f8f5ec');dr=ImageDraw.Draw(view);bounds=(549800,5802900,550470,5803200)
def pix(p):return ((p[0]-bounds[0])*1.9,650-(p[1]-bounds[1])*1.9)
for f in feats:
 p=shape(f['geometry']);dr.polygon([pix(p) for p in p.exterior.coords],fill='#969a9c')
for p in holes.geoms:dr.polygon([pix(q) for q in p.exterior.coords],fill='#463c39')
dr.line([pix(p) for p in curve.coords],fill='#147360',width=7);dr.ellipse((*[v-5 for v in pix(clock.coords[0])],*[v+5 for v in pix(clock.coords[0])]),fill='red')
view.save(A/'overview.png')
