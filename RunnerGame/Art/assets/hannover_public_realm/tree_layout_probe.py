from pathlib import Path
import json,sys,math
A=Path('RunnerGame/Art/assets/hannover_public_realm').resolve();sys.path.insert(0,str(A.parents[3]/'.model-research/hannover_route/python_deps'))
import numpy as np
from shapely.geometry import MultiPoint,Polygon,Point
from shapely.affinity import translate,scale
from shapely.ops import unary_union
# Reconstruct independent route/source geometry without running output mutations.
ns={'__file__':str(A/'verify.py')};s=(A/'verify.py').read_text();exec(s[:s.index("for prop in m['sceneProps']")],ns)
v=[]
for line in (A.parent/'street_tree/out/ENV_StreetTree.obj').read_text().splitlines():
 if line.startswith('v '):v.append(list(map(float,line.split()[1:])))
v=np.array(v);print('bounds',v.min(axis=0),v.max(axis=0))
trunk=MultiPoint(v[v[:,1]<2.568][:,[0,2]]).convex_hull;crown=MultiPoint(v[v[:,1]>=2.568][:,[0,2]]).convex_hull
print('trunk',trunk.bounds,'crown',crown.bounds)
# Source footprints in engine plane + actual parent facade projection.
buildings=translate(scale(ns['buildings'],xfact=1,yfact=-1,origin=(550000,5803000)),xoff=-550000,yoff=-5803000)
hero_v=[];hero_faces=[]
for l in (A/'out/KroepckeFacades.obj').read_text().splitlines():
 if l.startswith('v '):hero_v.append(list(map(float,l.split()[1:])))
 elif l.startswith('f '):hero_faces.append([int(x.split('/')[0])-1 for x in l.split()[1:]])
hero_v=np.array(hero_v);hero=unary_union([Polygon(hero_v[f][:,[0,2]]) for f in hero_faces if Polygon(hero_v[f][:,[0,2]]).area>1e-8]);obstacles=unary_union([buildings,hero])
public=translate(scale(ns['public'],xfact=1,yfact=-1,origin=(550000,5803000)),xoff=-550000,yoff=-5803000);tube=translate(scale(ns['tube'],xfact=1,yfact=-1,origin=(550000,5803000)),xoff=-550000,yoff=-5803000)
for x in range(-90,231,14):
 z=.335*x-39.7
 good=[]
 for row,(px,pz) in enumerate([(x,z),(x+3.176,z-9.482)]):
  tr=translate(trunk,xoff=px,yoff=pz);cr=translate(crown,xoff=px,yoff=pz)
  good.append((public.covers(tr),tr.distance(tube),cr.distance(obstacles)))
 print(x,z,good)
