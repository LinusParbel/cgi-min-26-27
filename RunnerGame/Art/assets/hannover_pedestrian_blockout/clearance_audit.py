"""Independent source-space obstruction audit; no source geometry edits."""
exec(open(__file__.replace('clearance_audit.py','build.py')).read().split('step=')[0])
h=Polygon(proposal['opening_polygons'][0]['coordinates']);edge=LineString([h.exterior.coords[0],h.exterior.coords[1]])
rows=[]
for f in feats:
 p=shape(f['geometry']);dist=p.distance(edge)
 if dist<5:rows.append({'id':f['id'],'object':f['properties']['obj_name'],'distance_to_NW_lip_m':dist,'opening_overlap_m2':p.intersection(h).area,'opening_overlap_bounds':None if p.intersection(h).is_empty else list(p.intersection(h).bounds)})
data={'status':'BLOCKED: source building footprints and manually interpreted opening leave no connected upper NW route','required_center_to_building_m':2.1,'required_center_to_opening_m':2.3,'attempts':[{'grid_m':.75,'building_buffer_m':2.35,'opening_buffer_m':2.65,'result':'disconnected'},{'grid_m':.25,'building_buffer_m':2.15,'opening_buffer_m':2.35,'result':'disconnected'}],'nearby_buildings':rows,'proposed_route_hole_intersection_area_m2':LineString(original).buffer(1.8).intersection(holes).area,'recommendation':'Reinterpret uncertain opening polygon against stronger evidence, or explicitly choose SE corridor with a larger proposal deviation. Do not shrink footprints/openings to force fit.'}
(A/'clearance-audit.json').write_text(json.dumps(data,indent=2));print(json.dumps(data,indent=2))
