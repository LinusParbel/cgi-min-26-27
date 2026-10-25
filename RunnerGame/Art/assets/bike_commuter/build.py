"""Measured navy Dutch commuter. Metres, Z up, front=-Y; no imported meshes."""
import sys,math,json
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'lib'))
import photo_lib as pl
bpy=pl.bpy
al=pl.al

def mesh(name,verts,faces,mat):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
    me.materials.append(mat)
    for p in me.polygons:p.use_smooth=True
    return ob

def ring(name,centre,rad,radial,width,mat,n=96,m=8):
    # Elliptical tyre/rim cross-section; X is the axle direction.
    v=[];f=[]
    for i in range(n):
        a=2*math.pi*i/n
        for j in range(m):
            b=2*math.pi*j/m;r=rad+radial*math.cos(b)
            v.append((centre[0]+width*math.sin(b),centre[1]+r*math.cos(a),centre[2]+r*math.sin(a)))
    for i in range(n):
        for j in range(m):f.append((i*m+j,((i+1)%n)*m+j,((i+1)%n)*m+(j+1)%m,i*m+(j+1)%m))
    return mesh(name,v,f,mat)

def smooth_samples(points,steps=5,closed=False):
    points=[Vector(p) for p in points];out=[];n=len(points)
    def at(i):return points[i%n] if closed else points[max(0,min(n-1,i))]
    for i in range(n if closed else n-1):
        a,b,c,d=(at(j) for j in [i-1,i,i+1,i+2])
        for j in range(steps):
            t=j/steps
            out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
    if not closed:out.append(points[-1])
    return out

def curved_tube(name,points,r,mat,closed=False):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=1
    cu.bevel_depth=r;cu.bevel_resolution=2;cu.resolution_u=1;cu.use_fill_caps=True
    sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
    for dst,src in zip(sp.points,points):dst.co=(*src,1)
    sp.use_cyclic_u=closed
    ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);cu.materials.append(mat)
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    bpy.ops.object.convert(target='MESH')
    for poly in ob.data.polygons:poly.use_smooth=True
    return ob

def build(spec):
    d,c=spec.d,spec.c
    mat={name:al.flat(name,c(name),roughness=.28 if name=='metal' else .55) for name in spec.colors}
    for name,material in mat.items():material.diffuse_color=(*c(name),1)
    # A restrained metal response is retained in editable material, bake records colour.
    metal=mat['metal'].node_tree.nodes.get('Principled BSDF')
    if metal:metal.inputs['Metallic'].default_value=.65
    parts={'body':[],'wheel_front':[],'wheel_rear':[]};body=parts['body'].append
    R=d('wheel_d')/2;W=d('wheelbase');front=Vector((0,-W/2,R));rear=Vector((0,W/2,R))
    def yz(key):return Vector((0,*d(key+'_yz')))
    bb,seat,ht,hb,post=(yz(k) for k in ['bottom_bracket','seat_cluster','head_top','head_bottom','seatpost_top'])
    def tube(name,a,b,r,material='paint',verts=12):
        ob=pl.tube(name,a,b,r,mat[material],verts=verts);body(ob);return ob
    def path(name,points,r,material='paint',verts=10):
        return [tube(name+'_'+str(i),a,b,r,material,verts) for i,(a,b) in enumerate(zip(points,points[1:]))]
    def box(name,size,loc,material='paint',bevel=0):
        ob=al.box(name,size,loc,mat[material],bevel=bevel);body(ob);return ob
    for key,centre in [('wheel_front',front),('wheel_rear',rear)]:
        add=parts[key].append
        add(ring(key+'_tyre',centre,R-d('wheel_w')/2,d('wheel_w')/2,d('wheel_w')/2,mat['rubber']))
        add(ring(key+'_rim',centre,(d('rim_outer_r')+d('rim_inner_r'))/2,(d('rim_outer_r')-d('rim_inner_r'))/2,d('wheel_w')*.38,mat['metal']))
        add(al.cyl(key+'_hub',d('wheel_w')*.65,d('hub_w'),centre,mat['metal'],axis='X',verts=20,bevel=0))
        for side in [-1,1]:
            add(al.cyl(key+'_flange_'+str(side),d('wheel_w'),d('spoke_r')*3,centre+Vector((side*d('hub_w')*.34,0,0)),mat['metal'],axis='X',verts=20,bevel=0))
        count=int(d('spoke_count'))
        for i in range(count):
            a=i*2*math.pi/count;side=1 if i%2 else -1;b=a+side*2*math.pi*5/count
            p=centre+Vector((side*d('hub_w')*.34,d('wheel_w')*math.cos(b),d('wheel_w')*math.sin(b)))
            q=centre+Vector((side*d('spoke_r'),d('rim_inner_r')*math.cos(a),d('rim_inner_r')*math.sin(a)))
            add(pl.tube(key+'_spoke_'+str(i),p,q,d('spoke_r'),mat['metal'],verts=6))
    tube('top_tube',seat,ht,d('top_tube_r'));tube('down_tube',hb,bb,d('down_tube_r'))
    tube('seat_tube',bb,seat,d('seat_tube_r'));tube('head_tube',hb,ht,d('head_tube_r'))
    tube('seatpost',seat,post,d('seat_tube_r')*.7,'metal')
    tube('bottom_bracket_shell',bb-Vector((d('hub_w')/2,0,0)),bb+Vector((d('hub_w')/2,0,0)),d('seat_tube_r')*1.3)
    for side in [-1,1]:
        dropout=rear+Vector((side*d('hub_w')/2,0,0))
        path('chainstay_'+str(side),[bb+Vector((side*d('seat_tube_r'),0,0)),Vector((side*d('hub_w')*.52,rear.y*.65,bb.z)),dropout],d('stay_r'))
        tube('seatstay_'+str(side),seat+Vector((side*d('seat_tube_r'),0,0)),dropout,d('stay_r'))
        x=side*(d('hub_w')/2)
        path('fork_'+str(side),[(x,hb.y,hb.z),(x,hb.y-.035,hb.z-.12),(x,front.y+.018,front.z+.07),(x,front.y,front.z)],d('fork_r'))
    tube('fork_crown',(-d('hub_w')/2,hb.y,hb.z),(d('hub_w')/2,hb.y,hb.z),d('fork_r'))
    for key,centre,angles in [('front',front,(0,165)),('rear',rear,(-15,175))]:
        body(pl.arc_shell(key+'_mudguard',centre,d('mudguard_r'),d('mudguard_w'),*angles,d('mudguard_thick'),mat['fender'],step_deg=5))
        for side in [-1,1]:
            for angle in [35,145]:
                a=math.radians(angle)
                tube(key+'_mudguard_stay_'+str(side)+'_'+str(angle),centre+Vector((side*d('hub_w')/2,0,0)),centre+Vector((side*d('mudguard_w')/2,d('mudguard_r')*math.cos(a),d('mudguard_r')*math.sin(a))),d('spoke_r')*1.5,'metal',6)
    # Rounded comfort saddle, broad rear and narrow forward nose; elliptical sections.
    sy=post.y;length=d('saddle_len');width=d('saddle_w');thick=d('saddle_thick');top=d('saddle_top_yz')[1]
    sections=smooth_samples([(-.53,.025,-.018),(-.46,.23,-.009),(-.18,.32,-.007),(.06,.72,0),(.30,1,.016),(.43,.91,.023),(.53,.025,.011)],steps=5)
    vs=[];fs=[];ns=16
    for t,w,lift in sections:
        for j in range(ns):
            a=2*math.pi*j/ns
            vs.append((width*w*.5*math.cos(a),sy+length*t,top-thick/2+lift+thick*.5*math.sin(a)))
    for i in range(len(sections)-1):
        for j in range(ns):fs.append((i*ns+j,i*ns+(j+1)%ns,(i+1)*ns+(j+1)%ns,(i+1)*ns+j))
    fs.extend([tuple(reversed(range(ns))),tuple((len(sections)-1)*ns+j for j in range(ns))]);body(mesh('padded_saddle',vs,fs,mat['saddle']))
    clampz=post.z+thick*.50
    tube('saddle_post_clamp_riser',post,(0,post.y,clampz),d('seat_tube_r')*.65,'metal')
    tube('saddle_rail_clamp',(-width*.19,post.y,clampz),(width*.19,post.y,clampz),d('stay_r')*.8,'metal')
    for side in [-1,1]:
        x=side*width*.10
        railpoints=[(x,post.y-length*.25,top-thick*.78),(x,post.y-length*.12,clampz),(x,post.y+length*.10,clampz),(x,post.y+length*.28,top-thick*.50)]
        body(curved_tube('saddle_rail_'+str(side),smooth_samples(railpoints,steps=4),d('spoke_r')*3,mat['metal']))
    # Swept city bar; separate grips and brake levers.
    barz=d('bar_h');bary=d('bar_y');half=d('bar_w')/2
    stem=Vector((0,ht.y+.03,barz-.055));tube('stem_riser',ht,stem,d('bar_tube_r')*1.2,'metal')
    tube('stem_extension',stem,(0,bary-.10,barz-.045),d('bar_tube_r')*1.2,'metal')
    for side in [-1,1]:
        path('swept_bar_'+str(side),[(0,bary-.10,barz-.045),(side*half*.45,bary-.10,barz-.03),(side*(half-d('grip_len')),bary-.04,barz),(side*half,bary,barz)],d('bar_tube_r'),'metal')
        grip0=Vector((side*(half-d('grip_len')),bary-.04,barz));grip1=Vector((side*half,bary,barz))
        tube('rubber_grip_'+str(side),grip0,grip1,d('grip_r'),'rubber')
        path('brake_lever_'+str(side),[grip0,(side*(half-d('grip_len')*.5),bary-.10,barz-.035),(side*(half-.015),bary-.075,barz-.045)],d('bar_tube_r')*.32,'metal',8)
        path('brake_cable_'+str(side),[grip0,Vector((side*.12,bary-.14,barz-.13)),Vector((side*.035,hb.y-.07,hb.z+.04)),hb+Vector((side*.035,-.02,0))],d('spoke_r')*1.1,'rubber',6)
    body(al.cyl('bell',d('grip_r')*1.5,d('grip_r'),(half*.45,bary-.07,barz),mat['metal'],verts=20,bevel=0))
    # Enclosed chain case: side silhouette extruded across its measured depth.
    profile=smooth_samples(d('chaincase_profile'),steps=6,closed=True);n=len(profile);x=d('chaincase_x');t=d('chaincase_thick')
    vs=[(x+off,y,z) for off in [-t/2,t/2] for y,z in profile]
    fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    case=mesh('enclosed_chaincase',vs,fs,mat['paint']);body(case)
    case.data.polygons[0].use_smooth=False;case.data.polygons[1].use_smooth=False
    outward=-1 if x<0 else 1
    cover_x=x+outward*(t/2+d('chainring_cover_t')/2)
    cover=al.cyl('chainring_silver_cover',d('chainring_cover_r'),d('chainring_cover_t'),(cover_x,bb.y,bb.z),mat['metal'],axis='X',verts=48,bevel=d('chainring_cover_t')*.25,segments=1);body(cover)
    body(ring('chainring_cover_inset',Vector((cover_x+outward*d('chainring_cover_t')*.6,bb.y,bb.z)),d('chainring_cover_r')*.77,d('chaincase_strip_r')*.35,d('chaincase_strip_r')*.4,mat['paint'],n=48,m=6))
    strip=[(x+outward*(t/2+d('chaincase_strip_r')*.3),y,z) for y,z in [(bb.y+.085,bb.z+.060),(bb.y+.18,bb.z+.066),(rear.y-.05,bb.z+.057)]]
    body(curved_tube('chaincase_inset_strip',smooth_samples(strip),d('chaincase_strip_r'),mat['metal']))
    for side in [-1,1]:
        cy=bb.y+side*d('crank_len');cx=side*(abs(d('chaincase_x'))+d('chaincase_thick'))
        tube('crank_'+str(side),(cx,bb.y,bb.z),(cx,cy,bb.z),d('stay_r')*.7,'metal')
        tube('pedal_axle_'+str(side),(cx,cy,bb.z),(cx+side*d('pedal_w')*.5,cy,bb.z),d('stay_r')*.5,'metal')
        box('pedal_'+str(side),(d('pedal_w'),d('pedal_len'),d('stay_r')*2),(cx+side*d('pedal_w')*.5,cy,bb.z),'pedal',d('stay_r')*.3)
    # Open tubular racks, with connected load-bearing struts to both axles.
    for key,centre in [('front',front),('rear',rear)]:
        rw=d(key+'_rack_w');rl=d(key+'_rack_len');ry=d(key+'_rack_y');rz=d(key+'_rack_h');rr=d('rack_tube_r')
        corner=min(d('rack_corner_r'),rw*.23)
        outline=[]
        for cx,cy,a0 in [(rw/2-corner,ry+rl/2-corner,0),(-rw/2+corner,ry+rl/2-corner,90),(-rw/2+corner,ry-rl/2+corner,180),(rw/2-corner,ry-rl/2+corner,270)]:
            for j in range(7):
                a=math.radians(a0+j*90/6);outline.append((cx+corner*math.cos(a),cy+corner*math.sin(a),rz))
        body(curved_tube(key+'_rack_rounded_perimeter',outline,rr,mat['paint'],closed=True))
        for side in [-1,1]:
            x=side*rw/2
            for j,yy in enumerate([ry-rl*.37,ry+rl*.37]):
                tube(key+'_rack_support_'+str(side)+'_'+str(j),centre+Vector((side*d('hub_w')*.58,0,0)),(x,yy,rz),rr*.8)
        for i in range(1,4):
            y=ry+rl*(i/4-.5);tube(key+'_rack_cross_'+str(i),(-rw/2,y,rz),(rw/2,y,rz),rr)
        if key=='front':
            y=ry+rl/2
            top=d('front_rack_back_h');back=[(-rw/2,y,rz),(-rw/2,y,top-corner)]
            for j in range(7):
                a=math.pi-j*math.pi/12;back.append((-rw/2+corner+corner*math.cos(a),y,top-corner+corner*math.sin(a)))
            back.append((rw/2-corner,y,top))
            for j in range(7):
                a=math.pi/2-j*math.pi/12;back.append((rw/2-corner+corner*math.cos(a),y,top-corner+corner*math.sin(a)))
            back.append((rw/2,y,rz));body(curved_tube('front_rack_rounded_back',back,rr,mat['paint']))
            z=rz+(top-rz)*.5;tube('front_rack_back_cross',(-rw/2,y,z),(rw/2,y,z),rr)
        else:
            tube('rear_rack_bridge',(0,ry-rl/2,rz),seat,d('rack_tube_r'))
    # Twin-leg centre stand, feet sit just above ground.
    for side in [-1,1]:
        end=(side*d('pedal_w')*1.2,bb.y+.13,d('kickstand_r'))
        tube('stand_leg_'+str(side),bb+Vector((side*d('seat_tube_r'),.035,-.015)),end,d('kickstand_r'),'metal')
        box('stand_foot_'+str(side),(d('kickstand_r')*3,d('kickstand_r')*5,d('kickstand_r')*2),end,'rubber')
    # Front lamp faces -Y; rear lamp sits beneath the carrier's tail.
    lamp=(0,d('front_rack_y')-d('front_rack_len')/2,d('front_rack_h')-.04)
    body(al.cyl('front_lamp_housing',d('grip_r')*1.6,d('grip_r')*2,lamp,mat['rubber'],axis='Y',verts=20,bevel=0))
    body(al.cyl('front_lamp_lens',d('grip_r')*1.4,d('spoke_r')*2,Vector(lamp)+Vector((0,-d('grip_r'),0)),mat['light_front'],axis='Y',verts=20,bevel=0))
    box('rear_light',(d('rear_rack_w')*.55,d('rack_tube_r')*2,d('grip_r')*2),(0,d('rear_rack_y')+d('rear_rack_len')/2,d('rear_rack_h')-.025),'reflector_red',d('rack_tube_r')*.4)
    landmarks={'front_axle':front,'rear_axle':rear,'bottom_bracket':bb,'seat_cluster':seat,'head_top':ht,'head_bottom':hb,'seatpost_top':post,'saddle_top':(0,*d('saddle_top_yz'))}
    for key,centre in [('front',front),('rear',rear)]:
        landmarks[key+'_wheel_top']=centre+Vector((0,0,R));landmarks[key+'_wheel_bottom']=centre-Vector((0,0,R))
    for name,loc in landmarks.items():pl.landmark(name,loc)
    bpy.context.view_layer.update()
    return parts

def preview(parts,out):
    scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH'
    scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
    scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
    scene.display.shading.background_type='WORLD';scene.world.color=(.75,.75,.75)
    scene.render.resolution_x=1024;scene.render.resolution_y=640;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='Standard'
    out=Path(out);out.parent.mkdir(exist_ok=True,parents=True)
    for name,loc in [('side',(-3.4,0,.70)),('three_quarter',(-2.7,-2,1.5))]:
        camera=pl.match_camera((1024,640),{'loc':loc,'look_at':[0,0,.57],'lens_mm':48,'roll_deg':0})
        camera.data.type='ORTHO';camera.data.ortho_scale=2.05
        scene.render.filepath=str(out.with_name(out.stem+'_'+name+'.png'));bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'bike_commuter.blend'))

def main(argv):
    al.clear_scene();parts=build(pl.Spec(HERE/'spec.json'))
    if '--export' in argv:
        pivots={'body':(0,0,0),'wheel_front':tuple(bpy.data.objects['LM_front_axle'].location),'wheel_rear':tuple(bpy.data.objects['LM_rear_axle'].location)}
        pl.bake_shared_and_export(parts,pivots,str((HERE/'out').resolve()),'VEH_BikeCommuter',res=json.loads((HERE/'spec.json').read_text())['tex_res'],samples=32)
    elif '--preview' in argv:preview(parts,Path(argv[argv.index('--preview')+1]).resolve())

if __name__=='__main__':main(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
