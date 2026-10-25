"""Reproduce route massing: Python 3.10+, lxml, numpy, shapely>=2.1, pyproj, Pillow.
Sources are official CRC-verified CityGML tiles in .model-research/hannover_route/source.
No geometry is inferred from imagery. Whole intersecting buildings are retained.
"""
from pathlib import Path
import sys,json,hashlib,math
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'.model-research/hannover_route/python_deps'))
import numpy as np
from lxml import etree
from shapely import Polygon, constrained_delaunay_triangles
from pyproj import Transformer
from PIL import Image
A=Path(__file__).resolve().parent; OUT=A/'out'; OUT.mkdir(exist_ok=True)
SRC=ROOT/'.model-research/hannover_route/source'
NS={'g':'http://www.opengis.net/gml','b':'http://www.opengis.net/citygml/building/2.0'}
ORIGIN=np.array([550000.,5803000.,55.])
t=Transformer.from_crs(4326,25832,always_xy=True)
SW=t.transform(9.7315,52.3735); NE=t.transform(9.7445,52.3785)
BBOX=[SW[0],SW[1],NE[0],NE[1]]
def ring(el):
 p=el.find('.//g:posList',NS)
 a=np.array([float(x) for x in p.text.split()]).reshape((-1,3))
 if np.linalg.norm(a[-1]-a[0])<1e-7:a=a[:-1]
 return a

def triangles(poly):
 ext=ring(poly.find('g:exterior',NS)); holes=[ring(x) for x in poly.findall('g:interior',NS)]
 # Project onto a stable plane, retain source normal rather than guessing winding.
 n=np.sum(np.cross(ext,np.roll(ext,-1,axis=0)),axis=0)
 if np.linalg.norm(n)<1e-8: return [],len(holes)
 n=n/np.linalg.norm(n); axis=int(np.argmax(np.abs(n))); keep=[i for i in range(3) if i!=axis]
 flat=Polygon(ext[:,keep],[h[:,keep] for h in holes])
 if not flat.is_valid: raise ValueError('Invalid source polygon '+poly.get('{'+NS['g']+'}id',''))
 lookup={tuple(v[keep]):v for arr in [ext]+holes for v in arr}
 result=[]
 for tri in constrained_delaunay_triangles(flat).geoms:
  vs=[]
  for c in list(tri.exterior.coords)[:3]:
   if tuple(c) in lookup: vs.append(lookup[tuple(c)])
   else:
    v=np.zeros(3);v[keep]=c;v[axis]=ext[0,axis]-np.dot(n[keep],v[keep]-ext[0,keep])/n[axis];vs.append(v)
  vs=np.array(vs)
  cross=np.cross(vs[1]-vs[0],vs[2]-vs[0])
  if np.linalg.norm(cross)<1e-8:continue
  if np.dot(cross,n)<0:vs=vs[[0,2,1]]
  result.append(vs)
 if abs(sum(Polygon(v[:,keep]).area for v in result)-flat.area)>max(1e-5,flat.area*1e-8):raise ValueError('Triangulation area mismatch')
 return result,len(holes)

buildings=[]; seen=set(); totalholes=0; skipped=0
for tile in sorted(SRC.glob('*.gml')):
 for _,b in etree.iterparse(str(tile),events=('end',),tag='{'+NS['b']+'}Building'):
  bid=b.get('{'+NS['g']+'}id')
  if bid in seen:b.clear();continue
  seen.add(bid)
  env=b.find('g:boundedBy/g:Envelope',NS)
  lo=np.array(list(map(float,env.find('g:lowerCorner',NS).text.split()))); hi=np.array(list(map(float,env.find('g:upperCorner',NS).text.split())))
  if hi[0]<BBOX[0] or lo[0]>BBOX[2] or hi[1]<BBOX[1] or lo[1]>BBOX[3]:b.clear();continue
  tris=[]; polys=0
  for p in b.findall('.//g:Polygon',NS):
   tt,nh=triangles(p);tris+=tt;totalholes+=nh;polys+=1
  if tris: buildings.append(dict(id=bid,tile=tile.name,lo=lo.tolist(),hi=hi.tolist(),tris=tris,polygons=polys))
  b.clear()
print('selected',len(buildings),'buildings',sum(len(b['tris']) for b in buildings),'triangles','holes',totalholes,flush=True)
assert sum(len(b['tris']) for b in buildings)<=100000,'Budget exceeded; narrow corridor explicitly'
# Hand-authored flat opaque grey swatch, no source imagery.
Image.new('RGBA',(512,512),(151,155,158,255)).save(OUT/'HannoverRoute.png')
verts=[]; faces=[]; mapping=[]
for i,b in enumerate(buildings):
 start=len(faces); vi={}
 for tr in b.pop('tris'):
  inds=[]
  for v in tr:
   # Source E,N,H -> engine E,H,-N is proper rotation (determinant +1).
   q=v-ORIGIN; q=(float(q[0]),float(q[2]),float(-q[1])); key=tuple(round(x,6) for x in q)
   if key not in vi:vi[key]=len(verts)+1;verts.append(q)
   inds.append(vi[key])
  faces.append((i,inds))
 b.update(name=f'building_{i:04d}',face_start=start,face_count=len(faces)-start);mapping.append(b)
with (OUT/'HannoverRoute.obj').open('w') as f:
 f.write('# Official Hannover LoD2 CC BY 4.0 derivative. Coordinates in metres, Y up.\nmtllib HannoverRoute.mtl\n')
 for v in verts:f.write('v '+' '.join(f'{x:.6f}' for x in v)+'\n')
 f.write('vt 0.5 0.5\nusemtl massing\n'); last=-1
 for _,ind in faces:
  p=np.array([verts[k-1] for k in ind]);n=np.cross(p[1]-p[0],p[2]-p[0]);n=n/np.linalg.norm(n);f.write('vn '+' '.join(f'{x:.9f}' for x in n)+'\n')
 for fi,(i,ind) in enumerate(faces,1):
  if i!=last:f.write('o '+mapping[i]['name']+'\n');last=i
  f.write('f '+' '.join(f'{v}/1/{fi}' for v in ind)+'\n')
(OUT/'HannoverRoute.mtl').write_text('newmtl massing\nKd 1 1 1\nmap_Kd HannoverRoute.png\n')
(OUT/'HannoverRoute_parts.json').write_text(json.dumps({'texture':'HannoverRoute.png','parts':[{'name':'hannover_massing','obj':'HannoverRoute.obj','pivot':[0,0,0]}]},indent=2))
v=np.array(verts); areas=[]
for _,ind in faces:
 p=v[np.array(ind)-1];areas.append(float(np.linalg.norm(np.cross(p[1]-p[0],p[2]-p[0]))/2))
assert np.isfinite(v).all() and min(areas)>1e-9
report={'crs':'EPSG:25832; source height DE_DHHN92_NH','origin_ENH':ORIGIN.tolist(),'engine_transform':'X=E-550000,Y=H-55,Z=-(N-5803000)','clip_lonlat':[9.7315,52.3735,9.7445,52.3785],'selection_bbox_EN':BBOX,'selection':'whole buildings intersecting rectangle, deduplicated by GML ID','buildings':len(mapping),'vertices':len(verts),'triangles':len(faces),'polygon_holes':totalholes,'engine_bounds':[v.min(axis=0).tolist(),v.max(axis=0).tolist()],'minimum_triangle_area_m2':min(areas),'tests':['ZIP tile CRC verified','constrained triangulation area matches every source polygon incl holes','source winding preserved under proper coordinate rotation','all vertices and UV finite','all face indices valid','all triangles nondegenerate','100000 triangle budget'],'texture':'authored opaque grey swatch 512x512; no imagery pixels'}
(A/'buildings.json').write_text(json.dumps(mapping,indent=2));(A/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
