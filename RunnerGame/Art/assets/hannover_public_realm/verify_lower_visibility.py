"""Ray tests use geometric CCW front faces, exactly as OpenGL backface culling."""
from pathlib import Path
import sys,json
A=Path(__file__).resolve().parent
sys.path.insert(0,str(A.parents[3]/'.model-research/hannover_route/python_deps'))
import numpy as np
from shapely.geometry import Polygon
p=json.loads((A/'placements-source.json').read_text());proposal=json.loads((A.parent/'hannover_route_reference/waypoint-proposal.json').read_text())
def geo(q):return (549750+q[0]*.5,5803400-q[1]*.5)
def local(q):return np.array([q[0]-550000,5803000-q[1]])
polys=[Polygon([geo(q) for q in p['mainOpeningPixels']]),Polygon(proposal['opening_polygons'][1]['coordinates'])]
v=[];faces=[]
for line in (A/'out/PedestrianGround.obj').read_text().splitlines():
 if line.startswith('v '):v.append(list(map(float,line.split()[1:])))
 elif line.startswith('f '):faces.append([int(x.split('/')[0])-1 for x in line.split()[1:]])
tri=np.array(v)[np.array(faces)];norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);floor=np.all(np.abs(tri[:,:,1]+4)<1e-7,axis=1);walls=(tri[:,:,1].min(axis=1)==-4)&(tri[:,:,1].max(axis=1)==-1)
def ray(origin,direction,triangles):
 direction=np.array(direction,float);direction/=np.linalg.norm(direction);e1=triangles[:,1]-triangles[:,0];e2=triangles[:,2]-triangles[:,0];pv=np.cross(direction,e2);det=np.einsum('ij,ij->i',e1,pv);good=det>1e-9;inv=np.zeros(len(det));inv[good]=1/det[good];tv=np.array(origin)-triangles[:,0];u=np.einsum('ij,ij->i',tv,pv)*inv;qv=np.cross(tv,e1);w=qv@direction*inv;t=np.einsum('ij,ij->i',e2,qv)*inv;ok=good&(u>=-1e-7)&(w>=-1e-7)&(u+w<=1+1e-7)&(t>1e-7)
 return float(t[ok].min()) if ok.any() else None
assert np.all(norm[floor,1]>0)
floor_rays=[];wall_rays=[]
for poly in polys:
 c=local(poly.centroid.coords[0]);origin=[c[0],2,c[1]];hit=ray(origin,[0,-1,0],tri);assert hit is not None and abs(hit-6)<1e-5;floor_rays.append(hit)
 assert ray(origin,[0,-1,0],tri[~floor]) is None,'Missing floor regression did not fail'
 coords=list(poly.exterior.coords)
 for a,b in zip(coords,coords[1:]):
  aa=local(a);bb=local(b);mid=(aa+bb)/2;direction=mid-c;origin=np.array([c[0],-2.5,c[1]]);d=[direction[0],0,direction[1]];hit=ray(origin,d,tri[walls]);assert hit is not None and abs(hit-np.linalg.norm(direction))<1e-5;wall_rays.append(hit)
  reverse=ray(origin,d,tri[walls][:,[0,2,1]]);assert reverse is None or abs(reverse-np.linalg.norm(direction))>1e-3,'Reversed wall regression did not fail'
# Cuboid rails are emitted in groups of 10 triangles: 8 outward sides, 2 upper cap.
railtri=tri[(tri[:,:,1].min(axis=1)>=-1)&(tri[:,:,1].max(axis=1)>-1)]
assert len(railtri)%10==0
for group in railtri.reshape((-1,10,3,3)):
 center=group.reshape(-1,3).mean(axis=0);normal=np.cross(group[:,1]-group[:,0],group[:,2]-group[:,0]);assert np.all(np.einsum('ij,ij->i',normal[:8],group[:8].mean(axis=1)-center)>0)
 assert np.all(normal[8:,1]>0)
result={'frontFaceConvention':'CCW, geometric cross product; ray determinant positive only','floorTriangleCount':int(floor.sum()),'verticalFloorRayDistances_m':floor_rays,'insideWallRayCount':len(wall_rays),'wallNormalsFaceInside':True,'railSideNormalsFaceOutside':True,'floorNormalsUp':True,'negativeMissingFloorDetected':True,'negativeReversedWallsDetected':True}
(A/'lower-visibility-verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
