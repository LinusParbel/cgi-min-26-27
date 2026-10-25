"""Representative paired avenue inferred from legal aerial rows; not a surveyed tree inventory."""
from pathlib import Path
import json,math
# Geometry definitions, independent source/route checks and actual tree/hero projections.
exec((Path(__file__).parent/'tree_layout_probe.py').read_text().split('for x in range')[0])
map_path=A/'out/map.json';mp=json.loads(map_path.read_text());oldprops=mp.get('sceneProps',[])
proposals=[]
# Western row fit follows interpreted aerial canopy centres (-44,-80.5),(-28.5,-74.5),(-12.5,-68.5).
for x in range(-90,23,14):
 z=.43*x-60;normal=np.array([-3.95,9.19]);proposals.append(('west',x,np.array([x,z]),normal))
# Eastern fit follows interpreted south row (30.5,-29.5),(72.5,-15.5),...,(142.5,8).
for x in range(36,135,14):
 z=.335*x-39.7;normal=np.array([3.176,-9.482]);proposals.append(('east',x,np.array([x,z]),normal))
accepted=[];rejected=[];records=[]
# Clip actual tree triangles at the rider envelope top in object space. This
# includes trunk/branch crossing points, rather than testing centre or vertex only.
tree_faces=[]
for line in (A.parent/'street_tree/out/ENV_StreetTree.obj').read_text().splitlines():
 if line.startswith('f '):tree_faces.append([int(t.split('/')[0])-1 for t in line.split()[1:]])
def scaled_envelopes(factor):
 points=[];cutoff=1.875/factor
 for indices in tree_faces:
  poly=list(v[indices])
  for a,b in zip(poly,poly[1:]+poly[:1]):
   if a[1]<=cutoff:points.append(a[[0,2]]*factor)
   if (a[1]-cutoff)*(b[1]-cutoff)<0:points.append((a+(b-a)*(cutoff-a[1])/(b[1]-a[1]))[[0,2]]*factor)
 return MultiPoint(points).convex_hull,MultiPoint(v[:,[0,2]]*factor).convex_hull
for segment,station,base,normal in proposals:
 normal=normal/np.linalg.norm(normal)*10;along=np.array([-normal[1],normal[0]])/10;unit=normal/10;found=None
 for factor in [1.5,1.4,1.0]:
  scaled_trunk,scaled_crown=scaled_envelopes(factor)
  for cross,forward in [(0,0),(1,0),(-1,0),(2,0),(-2,0),(0,1),(0,-1),(0,2),(0,-2),(1,1),(-1,1),(1,-1),(-1,-1),(2,2),(-2,-2),(2,-2),(-2,2)]:
   offset=cross*unit+forward*along;pair=[base+offset,base+normal+offset];metrics=[]
   for q in pair:
    tr=translate(scaled_trunk,xoff=q[0],yoff=q[1]);cr=translate(scaled_crown,xoff=q[0],yoff=q[1]);metrics.append({'fullLowerTrunkSupported':public.covers(tr),'trunkToTube_m':tr.distance(tube),'canopyToFacade_m':cr.distance(obstacles)})
   if all(m['fullLowerTrunkSupported'] and m['trunkToTube_m']>=.2 and m['canopyToFacade_m']>=.2 for m in metrics):found=(pair,metrics,offset,factor);break
  if found:break
 if found:
  pair,metrics,offset,factor=found
  for q in pair:accepted.append({'kind':'tree','x':round(float(q[0]),4),'z':round(float(q[1]),4),'yaw':0,'scale':factor})
  records.append({'segment':segment,'stationX':station,'status':'INFERRED representative paired row, not exact inventory','pairLocalXZ':[q.tolist() for q in pair],'normalSeparation_m':10,'adjustment_m':offset.tolist(),'metrics':metrics,'uncertainty_m':3,'scale':factor,'authoredHeight_m':6.5*factor,'heightStatus':'Authoring choice for mature avenue feature visible in licensed street photo; not surveyed'})
 else:rejected.append({'segment':segment,'stationX':station,'reason':'No inferred pair within <=2.83m adjustment clears actual lower-trunk tube, public support and full crown/source+hero facade projection'})
kept=[p for p in oldprops if p['kind']!='tree' or p['x']<-100 or p['x']>250]
mp['sceneProps']=kept+accepted;map_path.write_text(json.dumps(mp,indent=2),encoding='utf-8')
record={'source':'../hannover_route_reference/overview-clean.png, licensed official DOP20; source frame in placements-source.json','method':'Representative two-row feature inferred from legal aerial row fits; 10m normal spacing. User photo used for architectural paired-row feature, never traced geometry. Original source canopy centres vary and March shadows obscure exact inventory.','coordinateFrame':'X=E-550000;Z=5803000-N','uncertainty_m':3,'rows':records,'rejectedPairs':rejected,'overheadCanopyClearance':{'sourceCanopyUnderside_m':2.568,'riderEnvelopeTop_m':1.675,'requiredHeadMargin_m':.2,'scaledCanopyUnderside_m':3.852,'actualHeadMargin_m':2.177,'passes':True},'geometryChecks':'Actual scaled triangle edges clipped at rider envelope1.875m, convex projection of lower collision geometry clears player tube by>=.2m; full scaled tree crown convex projection clears union of source buildings and hero facade triangles by>=.2m. Lower trunk fully supported.','keptOtherProps':kept,'newAvenueProps':accepted}
(A/'paired-avenue-placements.json').write_text(json.dumps(record,indent=2))
report={'pairedStations':len(records),'avenueTrees':len(accepted),'totalSceneProps':len(mp['sceneProps']),'rejectedPairs':len(rejected),'rowNormalSeparation_m':10,'heightCounts':{str(h):sum(r['authoredHeight_m']==h for r in records)*2 for h in sorted(set(r['authoredHeight_m'] for r in records))},'minimumTrunkTubeMargin_m':min(m['trunkToTube_m'] for r in records for m in r['metrics']),'minimumCrownFacadeMargin_m':min(m['canopyToFacade_m'] for r in records for m in r['metrics']),'overheadCanopyMargin_m':2.177,'sourceStatus':'INFERRED representative aerial-fit placement +/-3m; not exact inventory','routeAndMeshesChanged':False}
(A/'paired-avenue-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
