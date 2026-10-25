"""Separate navy protective carrier, guided by user rear photo and front references."""
from pathlib import Path
import sys, math
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent

def add_vest():
    assert 'Vest front shell' not in bpy.data.objects
    rig=bpy.data.objects['Human.rig']
    collection=bpy.data.collections.new('Protective vest'); bpy.context.scene.collection.children.link(collection)
    def mat(name,color,rough=.86):
        m=bpy.data.materials.new(name); m.use_nodes=True; m.diffuse_color=(*color,1)
        p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough; p.inputs['Specular IOR Level'].default_value=.15
        n=m.node_tree.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value=450
        b=m.node_tree.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value=.16; b.inputs['Distance'].default_value=.00025
        m.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']); m.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
        return m
    fabric=mat('Vest midnight navy Cordura',(.005,.009,.018))
    binding=mat('Vest bound edges',(.003,.005,.010))
    velcro=mat('Vest black hook and loop',(.0025,.0035,.005))
    thread=mat('Vest seam thread',(.014,.020,.029))
    metal=mat('Vest dark zipper hardware',(.025,.030,.038),.45)
    # The front is informed by comparable municipal carriers, not asserted to be
    # the unseen front of a uniquely identified Dortmund issue vest.
    for o in list(bpy.data.objects):
        if o.name in ('Back identification backing','Chest identification backing') or o.name.startswith(('Chest pocket','Pocket flap','Pocket snap','Lower pocket welt','Shoulder tab','Shoulder button','Shoulder radio','Radio speaker','Radio coiled','Zipper ','Central zipper')):
            o.hide_render=True; o.hide_set(True)
    def mesh(name,verts,faces,material,thickness=0):
        me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update()
        ob=bpy.data.objects.new(name,me); collection.objects.link(ob); me.materials.append(material); ob.parent=rig
        for p in me.polygons: p.use_smooth=True
        if thickness:
            s=ob.modifiers.new('Padded carrier thickness','SOLIDIFY'); s.thickness=thickness; s.offset=-1
            bevel=ob.modifiers.new('Soft bound edge','BEVEL'); bevel.width=.002; bevel.segments=2
        return ob
    def tube(name,pts,radius,material):
        cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=radius; cu.bevel_resolution=2
        s=cu.splines.new('POLY'); s.points.add(len(pts)-1)
        for p,v in zip(s.points,pts): p.co=(*v,1)
        ob=bpy.data.objects.new(name,cu); collection.objects.link(ob); cu.materials.append(material); ob.parent=rig; return ob
    def cube(name,loc,dims,material):
        bpy.ops.mesh.primitive_cube_add(size=1,location=loc); ob=bpy.context.object; ob.name=name; ob.dimensions=dims
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        for c in list(ob.users_collection): c.objects.unlink(ob)
        collection.objects.link(ob); ob.parent=rig; ob.data.materials.append(material)
        b=ob.modifiers.new('Rounded corners','BEVEL'); b.width=.003; b.segments=3
        ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return ob
    # Evaluate the completed garment (including its closed front) in world space.
    bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get(); verts=[]; faces=[]
    for name in ('Service jacket and trousers','Jacket front closure and inner collar','Pale blue shirt neckline'):
        ob=bpy.data.objects.get(name)
        if not ob: continue
        ev=ob.evaluated_get(dg); me=ev.to_mesh(); start=len(verts)
        verts.extend(ob.matrix_world @ v.co for v in me.vertices); faces.extend(tuple(start+i for i in p.vertices) for p in me.polygons); ev.to_mesh_clear()
    cloth=BVHTree.FromPolygons(verts,faces)
    def interp(x,values):
        for (a,b),(c,d) in zip(values,values[1:]):
            if x<=c: return b+(d-b)*max(0,min(1,(x-a)/(c-a)))
        return values[-1][1]
    def radius_x(z): return interp(z,[(1.10,.255),(1.30,.255),(1.42,.245),(1.50,.235),(1.57,.21)])
    # Fit a smooth padded envelope to garment cross-sections, rather than copying
    # each jacket fold or switching abruptly at a missing shoulder ray.
    profiles={False:[],True:[]}; cy=-.025
    for back in (False,True):
        for j in range(49):
            z=1.10+j*.47/48; candidates=[]; rx=radius_x(z)
            for i in range(17):
                x=-.16+i*.02
                p,_,_,_=cloth.ray_cast(Vector((x,1 if back else -1,z)),Vector((0,-1 if back else 1,0)))
                if p is not None and (p.y>0 if back else p.y<0):
                    depth=(p.y-cy) if back else (cy-p.y)
                    candidates.append(depth/math.sqrt(max(.1,1-(x/rx)**2)))
            fallback=interp(z,[(1.10,.19),(1.40,.18),(1.50,.115),(1.57,.045)])
            radius=(max(candidates) if candidates else fallback)+.026
            profiles[back].append((z,radius))
        values=profiles[back]
        profiles[back]=[]
        for j,(z,r) in enumerate(values):
            neighbors=values[max(0,j-2):min(len(values),j+3)]
            profiles[back].append((z,sum(value for _,value in neighbors)/len(neighbors)))
    def outer_y(x,z,back):
        radius=interp(z,profiles[back]); curvature=math.sqrt(max(.08,1-(x/radius_x(z))**2))
        return cy+radius*curvature*(1 if back else -1)
    def point(u,v,back):
        a=abs(u)
        top=interp(a,[(0,1.535 if back else 1.49),(.28,1.54 if back else 1.505),(.48,1.56),(.72,1.566),(.88,1.55),(1,1.49)])
        bottom=1.105+.015*a**4
        z=bottom+(top-bottom)*v
        width=interp(z,[(1.10,.197),(1.25,.208),(1.34,.202),(1.40,.171),(1.46,.177),(1.49,.190),(1.57,.182)])
        x=u*width
        return Vector((x,outer_y(x,z,back),z))
    shells={}; nu=48; nv=40
    for back in (False,True):
        vs=[point(-1+2*i/nu,j/nv,back) for j in range(nv+1) for i in range(nu+1)]; fs=[]
        for j in range(nv):
            for i in range(nu):
                a=j*(nu+1)+i; f=(a,a+1,a+nu+2,a+nu+1); fs.append(tuple(reversed(f)) if back else f)
        ob=mesh('Vest back shell' if back else 'Vest front shell',vs,fs,fabric,.011); shells[back]=ob
        perimeter=vs[:nu+1]+[vs[j*(nu+1)+nu] for j in range(1,nv+1)]+list(reversed(vs[nv*(nu+1):]))+[vs[j*(nu+1)] for j in range(nv-1,0,-1)]
        tube('Vest rear edge binding' if back else 'Vest front edge binding',perimeter+[perimeter[0]],.0025,binding)
    # Actual shoulder bridges join front and rear; arm openings remain below them.
    for side in (-1,1):
        vs=[]; fs=[]; nx=10; ny=12
        for j in range(ny+1):
            t=j/ny
            for i in range(nx+1):
                u=side*(.48+.39*i/nx); f=point(u,1,False); b=point(u,1,True)
                p=f.lerp(b,t); p.z+=.010*math.sin(math.pi*t); vs.append(p)
        for j in range(ny):
            for i in range(nx):
                a=j*(nx+1)+i; fs.append((a,a+1,a+nx+2,a+nx+1))
        mesh(f'Vest shoulder bridge {side}',vs,fs,fabric,.008)
        tabverts=[]; tabfaces=[]
        for j in range(7):
            t=.18+j*.10
            for i in range(5):
                u=side*(.52+.28*i/4); f=point(u,1,False); b=point(u,1,True)
                p=f.lerp(b,t); p.z+=.010*math.sin(math.pi*t)+.003; tabverts.append(p)
        for j in range(6):
            for i in range(4):
                a=j*5+i; tabfaces.append((a,a+1,a+6,a+5))
        mesh(f'Vest shoulder hook and loop overlap {side}',tabverts,tabfaces,velcro,.003)
        for level in (0,1):
            z0=1.15+level*.095; vs=[]; fs=[]
            for j,z in enumerate((z0,z0+.064)):
                yf=outer_y(side*.197,z,False); yb=outer_y(side*.197,z,True)
                for i in range(21):
                    t=i/20; vs.append((side*(.197+.022*math.sin(math.pi*t)),yf+(yb-yf)*t,z))
            for i in range(20): fs.append((i,i+1,i+22,i+21))
            mesh(f'Vest side fastening band {side} {level}',vs,fs,velcro,.006)
    bpy.context.view_layer.update()
    trees={back:BVHTree.FromObject(ob,bpy.context.evaluated_depsgraph_get()) for back,ob in shells.items()}
    def fit(x,z,back=False,offset=.004):
        p,_,_,_=trees[back].ray_cast(Vector((x,1 if back else -1,z)),Vector((0,-1 if back else 1,0)))
        if p is None: raise ValueError(f'Vest surface missing at {x,z,back}')
        return p+Vector((0,offset if back else -offset,0))
    def patch(name,x0,x1,z0,z1,material,back=False,offset=.005):
        nx=32; nz=16; vs=[fit(x0+(x1-x0)*i/nx,z0+(z1-z0)*j/nz,back,offset) for j in range(nz+1) for i in range(nx+1)]; fs=[]
        for j in range(nz):
            for i in range(nx):
                a=j*(nx+1)+i; f=(a,a+1,a+nx+2,a+nx+1); fs.append(tuple(reversed(f)) if back else f)
        ob=mesh(name,vs,fs,material); uv=ob.data.uv_layers.new()
        for f in ob.data.polygons:
            for li in f.loop_indices:
                vi=ob.data.loops[li].vertex_index; u=vi%(nx+1)/nx; uv.data[li].uv=(1-u if back else u,vi//(nx+1)/nz)
        return ob
    label=mat('Vest ORDNUNGSAMT woven label',(.01,.015,.02))
    tex=label.node_tree.nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(str(HERE/'source/ordnungsamt_patch.png'),check_existing=True)
    label.node_tree.links.new(tex.outputs['Color'],label.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
    patch('Vest back ORDNUNGSAMT label',-.143,.143,1.436,1.492,label,True,.006)
    patch('Vest front ORDNUNGSAMT label',.033,.158,1.402,1.428,label,False,.006)
    patch('Vest lower back reinforcement',-.151,.151,1.137,1.286,velcro,True,.004)
    tube('Vest lower back pocket seam',[fit(-.145+i*.29/40,1.282,True,.006) for i in range(41)],.0012,thread)
    tube('Vest upper rear panel seam',[fit(-.146+i*.292/40,1.397,True,.005) for i in range(41)],.0008,thread)
    for side in (-1,1):
        a,b=sorted((side*.035,side*.16))
        patch(f'Vest vertical front pocket {side}',a,b,1.205,1.381,fabric,offset=.006)
        patch(f'Vest front pocket flap {side}',a,b,1.346,1.387,velcro,offset=.010)
        tube(f'Vest pocket seam {side}',[fit(a+(b-a)*i/30,1.211,offset=.008) for i in range(31)],.0007,thread)
        patch(f'Vest front side adjustment {side}',a,b,1.15,1.194,velcro,offset=.011)
        tube(f'Vest upper chest pocket zip {side}',[fit(a+(b-a)*i/30,1.443,offset=.006) for i in range(31)],.0018,binding)
        cube(f'Vest upper pocket zip pull {side}',fit(b-.008,1.443,offset=.010),(.007,.004,.015),metal)
    tube('Vest central front zip',[fit(0,1.124+i*.008) for i in range(46)],.0033,binding)
    for i in range(43): cube(f'Vest zipper tooth {i}',fit(0,1.132+i*.008,offset=.007),(.006,.002,.0016),metal)
    cube('Vest zipper pull',fit(0,1.47,offset=.012),(.010,.005,.024),metal)
    p=fit(-.128,1.46,offset=.015)
    cube('Vest shoulder radio microphone',p,(.044,.028,.064),velcro)
    for i in range(5): cube(f'Vest radio grille {i}',p+Vector((0,-.016,-.016+i*.006)),(.029,.002,.0014),metal)
    cube('Vest radio clip',fit(-.128,1.415,offset=.01),(.034,.009,.035),binding)
    points=[]
    for i in range(101):
        t=i/100; q=fit(-.14-.012*math.sin(math.pi*t),1.425-.25*t,offset=.012)
        q.x+=.002*math.cos(t*30*math.pi); q.y+=.002*math.sin(t*30*math.pi); points.append(q)
    tube('Vest radio coiled lead',points,.0014,binding)
    # The supplied rear photo also shows flat cargo pockets on the duty trousers.
    trouser_material=bpy.data.materials.get('Navy trouser twill') or fabric
    for side in (-1,1):
        def legpoint(y,z,offset):
            p,_,_,_=cloth.ray_cast(Vector((side*2,y,z)),Vector((-side,0,0)))
            if p is None: raise ValueError('Trouser pocket has no fitting surface')
            return p+Vector((side*offset,0,0))
        for flap in (False,True):
            z0,z1=(.795,.835) if flap else (.66,.824)
            nx=8; nz=12; vs=[]; fs=[]
            for j in range(nz+1):
                for i in range(nx+1): vs.append(legpoint(-.105+i*.14/nx,z0+(z1-z0)*j/nz,.012 if flap else .007))
            for j in range(nz):
                for i in range(nx):
                    a=j*(nx+1)+i; fs.append((a,a+1,a+nx+2,a+nx+1))
            mesh(f'Duty trouser cargo {"flap" if flap else "pocket"} {side}',vs,fs,trouser_material,.002)
    bpy.context.view_layer.update()
    print('VEST_CREATED',len(collection.objects),flush=True)
    return shells

if __name__=='__main__':
    bpy.ops.wm.open_mainfile(filepath=str(HERE/'checkpoints/pre_vest.blend'))
    add_vest()
    scene=bpy.context.scene; draft='--draft' in sys.argv
    scene.cycles.samples=12 if draft else 40; scene.render.resolution_x=700 if draft else 1000; scene.render.resolution_y=900 if draft else 1250
    cam=scene.camera
    views=[('front',(0,-6,1.7),(0,0,.91),2.05),('back',(-2,6,2.4),(0,0,.91),2.05),('three_quarter',(3,-6,2.5),(0,0,.91),2.05),('vest_front',(0,-5,1.6),(0,0,1.32),.78),('vest_side',(4,-2,1.8),(0,0,1.32),.86),('face',(.5,-5,1.9),(0,-.025,1.65),.49)]
    bpy.ops.file.pack_all(); bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'officer_v2.blend'))
    for name,loc,target,scale in views:
        cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=scale
        scene.render.filepath=str(HERE/'previews'/f'{name}.png'); bpy.ops.render.render(write_still=True)
    cam.location=(3,-6,2.5); cam.rotation_euler=(Vector((0,0,.91))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=2.05
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'officer_v2.blend'))
