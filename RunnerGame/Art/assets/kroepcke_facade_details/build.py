"""Reproducible world-coordinate architectural overlay. No source imagery pixels.
python RunnerGame/Art/assets/kroepcke_facade_details/build.py
"""
from pathlib import Path
import json,sys,math,hashlib
import numpy as np
from PIL import Image,ImageDraw
A=Path(__file__).resolve().parent; ROOT=A.parents[3]
sys.path.insert(0,str(ROOT/'.model-research/hannover_route/python_deps'))
from shapely.geometry import Polygon,box
from shapely.ops import triangulate
from lxml import etree
S=json.loads((A/'spec.json').read_text());OUT=A/'out';OUT.mkdir(exist_ok=True)
NS={'g':'http://www.opengis.net/gml','b':'http://www.opengis.net/citygml/building/2.0'}
meta={b['name']:b for b in json.loads((A.parent/'hannover_route/buildings.json').read_text())}
feats=json.loads((A.parent/'hannover_route/footprints.geojson').read_text())['features'];grounds={f['properties']['obj_name']:f['properties']['ground_height_min'] for f in feats}
# Authored opaque atlas: 8 procedural swatches, subtle limestone bedding, glass haze.
colors=[S['colors'][k] for k in ['cream','glass','glassLight','frame','roof']]+[[154,155,145],[179,178,164],[45,56,60]]
im=Image.new('RGB',(1024,1024));px=im.load()
for j,c in enumerate(colors):
 ox=(j%4)*256;oy=(j//4)*512
 for y in range(512):
  for x in range(256):
   n=((x*17+y*31)%13-6)*.22
   if j in [0,5,6]:n-=2 if y%100<2 else 0
   if j in [1,2,7]:n+=4*math.sin(x*.018)+2*math.sin(y*.012)
   px[ox+x,oy+y]=tuple(max(0,min(255,int(v+n))) for v in c)
im.save(OUT/'KroepckeFacades.png')
verts=[];uvs=[];norms=[];faces=[];components={};object_name=''
def emit(v,mat):
 v=np.array(v,float);n=np.cross(v[1]-v[0],v[2]-v[0]);ln=np.linalg.norm(n)
 if ln<1e-9:return
 n/=ln;start=len(verts)+1
 # Per-face corner UV mapping remains strictly inside opaque swatch.
 for i,p in enumerate(v):
  verts.append(p.tolist());u=((mat%4)*256+24+(i%2)*190)/1024;w=((mat//4)*512+40+(i//2)*420)/1024;uvs.append([u,1-w]);norms.append(n.tolist())
 for i in range(1,len(v)-1):faces.append((object_name,(start,start+i,start+i+1)));components[object_name]=components.get(object_name,0)+1

def panel(poly,origin,tangent,normal,offset,mat):
 if poly.is_empty:return
 polys=list(poly.geoms) if hasattr(poly,'geoms') else [poly]
 for p in polys:
  if p.geom_type!='Polygon' or p.area<1e-7:continue
  for tri in triangulate(p):
   if not p.covers(tri.representative_point()):continue
   vv=[origin+tangent*x+np.array([0,y,0])+normal*offset for x,y in list(tri.exterior.coords)[:3]]
   if np.dot(np.cross(vv[1]-vv[0],vv[2]-vv[0]),normal)<0:vv=vv[::-1]
   emit(vv,mat)

def strip(poly,o,t,n,x0,x1,y0,y1,offset,mat):panel(poly.intersection(box(x0,y0,x1,y1)),o,t,n,offset,mat)

# Cover every original triangle with an outward offset clone. Vertex normals
# preserve joins around rounded corners; roof and hidden returns receive finishes.
source=(A.parent/'hannover_route/out/HannoverRoute.obj').read_text().splitlines();sv=[np.array(list(map(float,l.split()[1:]))) for l in source if l.startswith('v ')]
owned={};name=None
for l in source:
 if l.startswith('o '):name=l[2:]
 if l.startswith('f ') and name in S['buildingIds'].values():owned.setdefault(name,[]).append([int(x.split('/')[0])-1 for x in l.split()[1:]])
for name,ff in owned.items():
 object_name=name+'_complete_stone_shell';acc={}
 for f in ff:
  p=np.array([sv[k] for k in f]);n=np.cross(p[1]-p[0],p[2]-p[0]);n/=np.linalg.norm(n)
  for k in f:acc[k]=acc.get(k,np.zeros(3))+n
 for f in ff:
  p=[]
  for k in f:
   v=sv[k].copy();v[1]+=54-grounds[name];nn=acc[k]/max(np.linalg.norm(acc[k]),1e-9);v+=nn*.045;p.append(v)
  normal=np.cross(p[1]-p[0],p[2]-p[0]);mat=4 if normal[1]>.3*np.linalg.norm(normal) else 0
  emit(p,mat)

root=etree.parse(str(ROOT/'.model-research/hannover_route/source/5500_5802.gml'))
wall_report=[]
for kind,name in S['buildingIds'].items():
 b=root.xpath('//*[@g:id="'+meta[name]['id']+'"]',namespaces=NS)[0]
 ground=grounds[name]
 for wi,wall in enumerate(b.findall('.//b:WallSurface',NS)):
  po=wall.find('.//g:Polygon',NS)
  if po is None:continue
  pos=po.find('.//g:exterior//g:posList',NS)
  if pos is None:continue
  pts=np.array(list(map(float,pos.text.split()))).reshape(-1,3)
  if np.linalg.norm(pts[-1]-pts[0])<1e-5:pts=pts[:-1]
  ev=np.array([[x-550000,z-ground-1,5803000-y] for x,y,z in pts]);n=np.sum(np.cross(ev,np.roll(ev,-1,axis=0)),axis=0);n/=np.linalg.norm(n)
  if abs(n[1])>.05:continue
  t=np.array([-n[2],0,n[0]]);o=ev[0].copy();o[1]=0
  xy=[(np.dot(v-o,t),v[1]) for v in ev];poly=Polygon(xy)
  if not poly.is_valid:poly=poly.buffer(0)
  if poly.is_empty:continue
  x0,y0,x1,y1=poly.bounds;length=x1-x0
  if kind=='center' and y1>17:
   poly=box(x0,min(y0,-1),x1,28.1);x0,y0,x1,y1=poly.bounds
  object_name=name+'_'+kind+'_facade'
  # Low source wall step edges below podium are finished, not decorated.
  if length<.12 or y1<1:continue
  is_tower=kind=='magis' and y1>25 and np.mean(pts[:,1])>5802992
  if kind=='magis':
   if is_tower:
    strip(poly,o,t,n,x0,x1,.2,y1-.45,.125,7)
    for y in np.arange(.3,y1,.92):strip(poly,o,t,n,x0,x1,y,y+.045,.21,5)
    for x in np.arange(x0,x1,.70):strip(poly,o,t,n,x,x+.045,.2,y1-.45,.22,5)
   else:
    # Ground shops and continuous display ribbon; no ad imagery or brands.
    for a,z in [(.05,3.15),(4.05,6.85)]:strip(poly,o,t,n,x0,x1,a,z,.125,2 if a>1 else 7)
    for a,z in [(3.15,3.95),(6.85,7.25)]:
     strip(poly,o,t,n,x0,x1,a,z,.26,5 if a<4 else 0)
    for a,z in [(8.2,10.4),(12.05,14.25),(15.9,18.1),(19.75,21.95)]:
     strip(poly,o,t,n,x0,x1,a,z,.125,1 if a>17 else 2)
     strip(poly,o,t,n,x0,x1,a-.12,a,.25,3)
     strip(poly,o,t,n,x0,x1,z,z+.14,.25,0)
     # Dense thin mullions in continuous bands: geometry, no tiled-window map.
     for x in np.arange(x0+.05,x1,.9):strip(poly,o,t,n,x,x+.045,a,z,.22,3)
     if a<20:strip(poly,o,t,n,x0,x1,a+.3,a+.34,.23,3)
    strip(poly,o,t,n,x0,x1,22.05,22.7,.27,0)
    for x in np.arange(x0,x1,2.8):strip(poly,o,t,n,x,x+.075,.05,6.85,.22,3)
  else:
   # Complete opaque new envelope behind every opening/band.
   panel(poly,o,t,n,.065,0)
   # Center's tall pale piers and recessed vertically proportioned windows.
   # Prow arcade uses a double-height glazed ground level with deep piers.
   strip(poly,o,t,n,x0,x1,.02,5.65,.12,7)
   for a,z in [(6.15,9.55),(10.35,13.75),(14.55,17.95),(18.75,22.15),(22.95,26.35)]:
    strip(poly,o,t,n,x0,x1,a,z,.11,1 if a>17 else 2)
    strip(poly,o,t,n,x0,x1,a-.18,a,.25,5)
    strip(poly,o,t,n,x0,x1,z,z+.22,.25,0)
   pitch=2.65;count=max(1,round(length/pitch));pitch=length/count
   for k in range(count+1):
    x=x0+k*pitch;strip(poly,o,t,n,x-.3,x+.3,.02,min(y1,27.1),.36,0)
    # Narrow shadow jamb beside the projecting limestone pier.
    strip(poly,o,t,n,x+.3,x+.36,5.8,min(y1,26.5),.20,3)
   strip(poly,o,t,n,x0,x1,5.65,6.15,.38,0)
   strip(poly,o,t,n,x0,x1,26.6,min(y1,28.1),.28,0)
  wall_report.append({'building':name,'wall':wi,'length_m':length,'height_range':[y0,y1],'tower':bool(is_tower)})

# Rebuilt Center roof cap: closed 29.1m envelope based on six-storey photo.
object_name='building_0271_redeveloped_roof_cap'
from shapely.geometry import shape
fp=shape(next(f['geometry'] for f in feats if f['properties']['obj_name']=='building_0271'))
for tr in triangulate(fp):
 if fp.covers(tr.representative_point()):
  vv=[[x-550000,28.1,5803000-y] for x,y in list(tr.exterior.coords)[:3]]
  if np.cross(np.array(vv[1])-vv[0],np.array(vv[2])-vv[0])[1]<0:vv=vv[::-1]
  emit(vv,4)
# Distinctive Magis architectural silhouette: a rounded projecting corner skin,
# recessed highest ribbon and a tall glazed narrow stair drum at the right return.
# Source shell remains fully covered; these additions follow the source east axis.
object_name='building_0307_magis_rounded_corner_and_stair_tower'
def band_arc(cx,cz,r,a0,a1,z0,z1,mat,steps=12):
 for i in range(steps):
  a=a0+(a1-a0)*i/steps;b=a0+(a1-a0)*(i+1)/steps
  p=[[cx+r*math.cos(a),z0,cz+r*math.sin(a)],[cx+r*math.cos(b),z0,cz+r*math.sin(b)],[cx+r*math.cos(b),z1,cz+r*math.sin(b)],[cx+r*math.cos(a),z1,cz+r*math.sin(a)]]
  # Arc viewed externally, winding follows outward radial direction.
  n=np.cross(np.array(p[1])-p[0],np.array(p[2])-p[0]);rad=np.array([math.cos((a+b)/2),0,math.sin((a+b)/2)])
  if np.dot(n,rad)<0:p=p[::-1]
  emit(p,mat)
# Continuous outside skin joins the quarter-round at its tangent endpoints.
# A2m podium projection allows the source sharp corner to remain hidden inside.
for ax,az,tx,tz,nx,nz,length in [(252.5,26.41,.314,-.949,.949,.314,24.4),(252.5,26.41,-.949,-.314,-.314,.949,20.8)]:
 o=np.array([ax,0,az]);t=np.array([tx,0,tz]);n=np.array([nx,0,nz]);poly=box(0,-1,length,22.85)
 panel(poly,o,t,n,1.82,0)
 for a,z in [(-.98,3.15),(4.05,6.85),(8.2,10.4),(12.05,14.25),(15.9,18.1),(19.75,21.95)]:
  strip(poly,o,t,n,0,length,a,z,1.94,2 if a>3 else 7)
  pitch=.9 if a>7 else 2.8
  for x in np.arange(0,length,pitch):strip(poly,o,t,n,x,x+.045,a,z,2.01,3)
  if a>7:strip(poly,o,t,n,0,length,a+.3,a+.345,2.02,3)
 for a,z in [(3.15,4.05),(6.85,8.2),(10.4,12.05),(14.25,15.9),(18.1,19.75),(21.95,22.85)]:strip(poly,o,t,n,0,length,a,z,2.04,0)
# Rounded SE corner (source E252.5,N2973.59), projecting to cover sharp LoD2.
# 1.8m radius is a photo-derived interpretation, not a surveyed footprint change.
cx,cz=252.50,26.41
for a,z in [(-.98,3.15),(4.05,6.85),(8.2,10.4),(12.05,14.25),(15.9,18.1),(19.75,21.95)]:
 band_arc(cx,cz,1.94,.319,1.890,a,z,2)
 for i in range(7):
  angle=.319+1.571*i/6;band_arc(cx,cz,2.01,angle-.013,angle+.013,a,z,3,1)
for a,z in [(3.15,4.05),(6.85,8.2),(10.4,12.05),(14.25,15.9),(18.1,19.75),(21.95,22.85)]:band_arc(cx,cz,2.04,.319,1.890,a,z,0)
# Narrow glazed stair tower at north/east return, aligns the source tallest wing.
cx,cz=260.3,3.0
band_arc(cx,cz,1.68,-2.0,1.15,3.2,26.8,7,14)
for i in range(9):
 angle=-2+3.15*i/8;band_arc(cx,cz,1.75,angle-.015,angle+.015,3.2,26.8,5,1)
for y in np.arange(3.2,26.8,1.38):band_arc(cx,cz,1.75,-2,1.15,y,y+.055,5,14)
band_arc(cx,cz,1.95,-2,1.15,26.8,27.35,0,14)

with (OUT/'KroepckeFacades.obj').open('w') as f:
 f.write('# Official CityGML CC BY 4.0 derivative; measured historic facade interpretation. Engine X=E-550000,Y=H-ground-1,Z=5803000-N.\nmtllib KroepckeFacades.mtl\n')
 for p in verts:f.write('v '+' '.join(f'{a:.7f}' for a in p)+'\n')
 for p in uvs:f.write('vt '+' '.join(f'{a:.7f}' for a in p)+'\n')
 for p in norms:f.write('vn '+' '.join(f'{a:.9f}' for a in p)+'\n')
 f.write('usemtl facade\n');last=None
 for name,face in faces:
  if name!=last:f.write('o '+name+'\n');last=name
  f.write('f '+' '.join(f'{k}/{k}/{k}' for k in face)+'\n')
(OUT/'KroepckeFacades.mtl').write_text('newmtl facade\nKd 1 1 1\nd 1\nmap_Kd KroepckeFacades.png\n')
(OUT/'KroepckeFacades_parts.json').write_text(json.dumps({'texture':'KroepckeFacades.png','parts':[{'name':'kroepcke_key_facades','obj':'KroepckeFacades.obj','pivot':[0,0,0]}]},indent=2))
assert len(faces)<=S['tri_budget'],len(faces)
(A/'wall-measurements.json').write_text(json.dumps(wall_report,indent=2))
(A/'REPORT.json').write_text(json.dumps({'triangles':len(faces),'vertices':len(verts),'components':components,'buildings':{k:meta[v] for k,v in S['buildingIds'].items()},'texture':'authored RGB opaque1024x1024','sourceGeometrySha256':hashlib.sha256((A.parent/'hannover_route/out/HannoverRoute.obj').read_bytes()).hexdigest(),'limitations':S['limitations']},indent=2))
print(json.dumps({'triangles':len(faces),'vertices':len(verts),'components':components},indent=2))
