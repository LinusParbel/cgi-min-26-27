"""Record photo measurements for the existing navy Batavus reference design."""
from pathlib import Path
import json,shutil
HERE=Path(__file__).resolve().parent
for file in ('spec.json','refs.json'):
    backup=HERE/'checkpoints'/('before_photo_build_'+file)
    backup.parent.mkdir(exist_ok=True)
    if not backup.exists(): shutil.copy2(HERE/file,backup)
spec=json.loads((HERE/'spec.json').read_text())
# Axles: rear (456,674), front (1238,660). Use existing 1.08 m ruler;
# remove the small image roll using the axle line before converting height.
scale=1.08/(1238-456)
def yz(px,py):
    baseline=674+(px-456)*(660-674)/(1238-456)
    return [round(-(px-847)*scale,5),round(.34+(baseline-py)*scale,5)]
points={'rear_axle':[456,674],'front_axle':[1238,660],
        'bottom_bracket':[779,710],'seat_cluster':[610,350],
        'head_top':[1050,330],'head_bottom':[1090,405],
        'seatpost_top':[588,276],'saddle_top':[535,220],
        'rear_rack_back':[285,397],'rear_rack_front':[575,386],
        'front_rack_back':[1120,430],'front_rack_front':[1365,343]}
for key,pixel in points.items():
    if key.endswith('axle'): continue
    spec['dims'][key+'_yz']={'value':yz(*pixel),'source':f'ref/04.jpg pixel {pixel}; axle-line roll corrected, 1.08 m wheelbase ruler; front rack depth resolved in ref/03'}
values={
 'top_tube_r':(.017,'ref/04 frame grid: diameter approx 24px / axle spacing782px'),
 'down_tube_r':(.026,'ref/04 frame grid: diameter approx38px; larger oval down tube'),
 'seat_tube_r':(.019,'ref/04 frame grid: approx28px outside tube diameter'),
 'head_tube_r':(.027,'ref/04 frame grid: approx40px outside head tube diameter'),
 'stay_r':(.010,'ref/04 frame grid: paired rear stays approx14px'),
 'fork_r':(.014,'ref/04 and ref/03 fork legs approx20px'),
 'hub_w':(.105,'ref/03 inferred cross-bike hub width, not physically measured'),
 'spoke_count':(36,'ref/03 and ref/04 thin crossed wire spokes, count estimated from visible pattern'),
 'spoke_r':(.0011,'Thin wire appearance in ref/03; game-readable approximation'),
 'rim_outer_r':(.319,'ref/04 side image: aluminium rim inside tyre of radius .34'),
 'rim_inner_r':(.308,'ref/04 bright rim band roughly8px deep'),
 'mudguard_r':(.356,'ref/04 mudguard clearance about12px above outer tyre'),
 'mudguard_w':(.055,'ref/03 transverse mudguard width slightly wider than42mm tyre'),
 'mudguard_thick':(.002,'Thin sheet mudguard interpretation'),
 'rack_tube_r':(.006,'ref/03 and04 rack tube diameter about9px at rear'),
 'rear_rack_w':(.145,'ref/03 rear platform transverse width inferred from perspective'),
 'rear_rack_len':(.40,'ref/04 rear carrier approx290px /782px wheelbase'),
 'rear_rack_h':(.735,'ref/04 rear carrier height above axle approx285px'),
 'front_rack_w':(.30,'ref/03 broad front platform about twice rear rack width'),
 'front_rack_len':(.34,'ref/03 rack reaches over front tyre; ref/04 perspective shortening'),
 'front_rack_h':(.755,'ref/03 platform just above front mudguard'),
 'front_rack_y':(-.58,'ref/03 platform centered above front wheel'),
 'front_rack_back_h':(1.065,'ref/03 tall upright rack back reaches near handlebar stem'),
 'rear_rack_y':(.58,'ref/04 rear platform centered above rear wheel'),
 'bar_h':(1.105,'ref/03/04 handlebar upper contour compared with wheel diameter'),
 'bar_y':(-.235,'ref/03 swept-back city handlebar behind steering axis'),
 'bar_tube_r':(.011,'ref/06 chrome city handlebar diameter interpretation'),
 'grip_len':(.115,'ref/03 black grips relative to580mm handlebar width'),
 'grip_r':(.016,'ref/03 rubber grips larger than chrome tube'),
 'saddle_w':(.205,'ref/03 broad comfort saddle, cross-bike width inferred'),
 'saddle_len':(.265,'ref/04 saddle approx190px /782px wheelbase'),
 'saddle_thick':(.050,'ref/04 raised rear padding contour'),
 'chaincase_thick':(.036,'ref/03 enclosed chaincase transverse depth'),
 'chaincase_x':(-.073,'ref/03 rider right side (-X with front -Y), outside rear stays'),
 'chaincase_profile':([[.54,.265],[.59,.30],[.58,.365],[.52,.385],[.12,.385],[.045,.36],[.015,.315],[.025,.255],[.08,.23],[.18,.235],[.48,.255]],'ref/04 silhouette around rear sprocket and front chainring, in longitudinal Y/Z metres'),
 'crank_len':(.17,'ref/03/04 pedal-crank radius compared with wheel diameter'),
 'pedal_w':(.095,'ref/03 transverse pedal width interpretation'),
 'pedal_len':(.075,'ref/03 pedal fore-aft width interpretation'),
 'kickstand_r':(.008,'ref/03 deployed twin-leg centre stand'),
}
for key,(value,source) in values.items(): spec['dims'][key]={'value':value,'source':source}
spec['colors']['saddle']={'linear':[.022,.024,.029],'source':'ref/03 and04 visibly black comfort saddle; corrects earlier brown placeholder'}
spec['colors']['paint']={'linear':[.014,.019,.032],'source':'ref/04 frame: near-black navy in overcast light, interpreted without photo pixels'}
spec['colors']['fender']=dict(spec['colors']['paint'])
spec['colors']['metal']={'linear':[.42,.44,.47],'source':'ref/03/04 silver rims, chrome handlebar and hub shells; interpreted midtone'}
spec['colors']['rubber']={'linear':[.018,.020,.024],'source':'ref/04 dark tyres and grips'}
spec['measurement_limits']='Wheelbase is an existing assumed ruler, not a published Batavus measurement. Cross-bike widths and obscured details are inferred. Aim for recognisable reference silhouette, not a measured factory replica.'
(HERE/'spec.json').write_text(json.dumps(spec,indent=2))
refs=json.loads((HERE/'refs.json').read_text())
for p in refs['photos']:
    if p['file']=='ref/04.jpg':
        p['landmarks']={k:v for k,v in points.items() if k in ('rear_axle','front_axle','bottom_bracket','seat_cluster','head_top','head_bottom','seatpost_top','saddle_top')}
        p['landmarks'].update({'front_wheel_top':[1238,416],'rear_wheel_top':[456,431],'front_wheel_bottom':[1238,853],'rear_wheel_bottom':[456,895]})
        p['camera']={'loc':[-3.4,-.20,1.2],'look_at':[0,0,.60],'lens_mm':44,'roll_deg':0}
        p['sections']={'frame':[380,290,1130,790],'wheels':[180,405,1495,920],'racks':[250,175,1405,465],'cockpit':[460,65,1110,310]}
    if p['file']=='ref/03.jpg':
        p['landmarks']={'rear_axle':[354,660],'front_axle':[1067,778],'bottom_bracket':[607,743],'seat_cluster':[463,369],'head_top':[853,359],'head_bottom':[890,456],'seatpost_top':[431,286],'saddle_top':[411,241]}
        p['camera']={'loc':[-2.7,-2.0,1.4],'look_at':[0,0,.60],'lens_mm':44,'roll_deg':0}
        p['sections']={'frame':[320,315,915,815],'wheels':[175,425,1390,1000],'racks':[195,180,1260,520],'cockpit':[300,65,890,335]}
(HERE/'refs.json').write_text(json.dumps(refs,indent=1))
(HERE/'measurement_notes.json').write_text(json.dumps({'metres_per_pixel_at_axle_plane':scale,'pixels_04':points,'derived_yz':{k:yz(*p) for k,p in points.items()},'cross_widths':'inferred from ref/03 and06; not a measured replica'},indent=2))
print('MEASURED',len(values),'dimensions; 2 key photos; imported candidates unchanged')
