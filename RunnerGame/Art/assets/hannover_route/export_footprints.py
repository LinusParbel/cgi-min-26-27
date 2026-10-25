"""Export selected source GroundSurface footprints, EPSG:25832, with original holes."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'.model-research/hannover_route/python_deps'))
from lxml import etree
from shapely import Polygon,union_all
from shapely.geometry import mapping
A=Path(__file__).resolve().parent;S=ROOT/'.model-research/hannover_route/source'
NS={'g':'http://www.opengis.net/gml','b':'http://www.opengis.net/citygml/building/2.0'}
selected={b['id']:b for b in json.loads((A/'buildings.json').read_text())};features=[];seen=set();counts={}
def readring(e):
 v=list(map(float,e.find('.//g:posList',NS).text.split()));return [v[i:i+3] for i in range(0,len(v),3)]
def poly(p):
 ext=readring(p.find('g:exterior',NS));holes=[readring(h) for h in p.findall('g:interior',NS)]
 return Polygon([v[:2] for v in ext],[[v[:2] for v in r] for r in holes]),[v[2] for r in [ext]+holes for v in r]
for tile in sorted(S.glob('*.gml')):
 for _,b in etree.iterparse(str(tile),events=('end',),tag='{'+NS['b']+'}Building'):
  bid=b.get('{'+NS['g']+'}id')
  if bid not in selected or bid in seen:b.clear();continue
  seen.add(bid);ps=b.findall('.//b:GroundSurface//g:Polygon',NS);source='GroundSurface';polygons=[];heights=[]
  if not ps:ps=b.findall('.//b:RoofSurface//g:Polygon',NS)+b.findall('.//b:WallSurface//g:Polygon',NS);source='fallback_projected_RoofSurface_WallSurface_union'
  for p in ps:
   q,h=poly(p)
   if q.area>1e-8:
    if not q.is_valid:raise ValueError('Invalid footprint polygon '+bid)
    polygons.append(q);heights.extend(h)
  if not polygons:raise ValueError('No nonzero projected footprint '+bid)
  geom=union_all(polygons);rec=selected[bid]
  features.append({'type':'Feature','id':bid,'properties':{'gml_id':bid,'obj_name':rec['name'],'source_tile':tile.name,'footprint_source':source,'ground_height_min':min(heights),'ground_height_max':max(heights),'source_bbox_height_min':rec['lo'][2],'source_bbox_height_max':rec['hi'][2],'area_m2':geom.area},'geometry':mapping(geom)})
  counts[source]=counts.get(source,0)+1;b.clear()
assert len(features)==len(selected)
features.sort(key=lambda f:f['properties']['obj_name'])
result={'type':'FeatureCollection','name':'Hannover selected LoD2 source footprints','crs':{'type':'name','properties':{'name':'urn:ogc:def:crs:EPSG::25832'}},'coordinate_note':'Projected E,N metres, EPSG25832; not RFC7946 longitude/latitude. Height properties source DE_DHHN92_NH.','counts':counts,'features':features}
(A/'footprints.geojson').write_text(json.dumps(result,indent=2));print(json.dumps(counts));print('Features',len(features))
# nearby station forecourt source ground heights, spatial query only, not semantic labels
from shapely.geometry import shape,Point
p=Point(550420,5803165)
near=sorted(features,key=lambda f:shape(f['geometry']).distance(p))[:12]
print(json.dumps([dict(f['properties'],distance_to_station_front_m=shape(f['geometry']).distance(p)) for f in near],indent=2))
