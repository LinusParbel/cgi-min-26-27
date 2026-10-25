"""Original city token: Blender headless build, contract checks then optional single bake."""
import sys,json,math
from pathlib import Path
import bpy,bmesh
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'lib'));sys.path.insert(0,str(HERE))
import photo_lib as pl
import verify

def build(s):
    pl.al.clear_scene()
    def mat(name,color):
        m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Metallic'].default_value=.65;b.inputs['Roughness'].default_value=.4;return m
    bronze=mat('Warm bronze body',(.35,.17,.047));gold=mat('Raised muted gold',(.65,.40,.105))
    n=s['segments'];r=s['diameter']/2;t=s['thickness']/2;f=s['face_depth']
    profile=[(.14,-f),(.146,-f),(.150,-t),(.157,-t),(r,-.0145),(r,.0145),(.157,t),(.150,t),(.146,f),(.14,f)]
    vs=[(rr*math.cos(i*2*math.pi/n),y,rr*math.sin(i*2*math.pi/n)) for rr,y in profile for i in range(n)]
    fs=[tuple(range(n-1,-1,-1)),tuple(range((len(profile)-1)*n,len(profile)*n))]
    fs += [(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(profile)-1) for i in range(n)]
    mesh=bpy.data.meshes.new('Disc with stepped bevel rim');mesh.from_pydata(vs,[],fs);mesh.update();disc=bpy.data.objects.new('Disc',mesh);bpy.context.collection.objects.link(disc);mesh.materials.append(bronze);mesh.materials.append(gold)
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
    for p in mesh.polygons:
        if abs(p.center.y)>.013:p.material_index=1
    obs=[disc];w=s['motif_width'];h=s['motif_height'];stroke=s['stroke']
    for side,sign in [('front',-1),('rear',1)]:
        for name,size,loc in [('left',(stroke,t-f,h),(-(w-stroke)/2,sign*(t+f)/2,0)),('right',(stroke,t-f,h),((w-stroke)/2,sign*(t+f)/2,0)),('cross',(w-2*stroke,t-f,stroke),(0,sign*(t+f)/2,0))]:
            obs.append(pl.al.box(side+'_H_'+name,size,loc,gold,bevel=0))
    bpy.context.view_layer.update();return {'token':obs}
if __name__=='__main__':
    s=json.loads((HERE/'spec.json').read_text());parts=build(s);result=verify.geometry(parts);(HERE/'out/geometry_checks.json').write_text(json.dumps(result,indent=2));print(result)
    bpy.context.scene.render.threads_mode='FIXED';bpy.context.scene.render.threads=s['threads']
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'city_token.blend'))
    if '--export' in sys.argv:pl.bake_shared_and_export(parts,{'token':(0,0,0)},HERE/'out','PROP_CityToken',res=s['atlas'],samples=s['samples'])
