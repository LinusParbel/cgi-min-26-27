"""Reproducible original street; run headless Blender with --export to bake."""
import sys,json,math
from pathlib import Path
import bpy
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'lib'))
sys.path.insert(0,str(HERE))
import photo_lib as pl
import verify
al=pl.al
def material(name,kind,spec):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links
    bs=n.get('Principled BSDF');bs.inputs['Roughness'].default_value=.88
    geo=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],sep.inputs[0])
    def op(kind,a,b=None):
        t=n.new('ShaderNodeMath');t.operation=kind
        if hasattr(a,'node'): l.new(a,t.inputs[0])
        else:t.inputs[0].default_value=a
        if b is not None:
            if hasattr(b,'node'):l.new(b,t.inputs[1])
            else:t.inputs[1].default_value=b
        return t.outputs[0]
    # Periodic noise domain: identical values on +/-10m snap planes.
    half=spec.d('length')/2
    angle=op('MULTIPLY',sep.outputs['Y'],math.pi/half)
    vec=n.new('ShaderNodeCombineXYZ');l.new(sep.outputs['X'],vec.inputs[0]);l.new(op('SINE',angle),vec.inputs[1]);l.new(op('COSINE',angle),vec.inputs[2])
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=95;l.new(vec.outputs[0],noise.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB');l.new(noise.outputs['Fac'],ramp.inputs[0])
    colors={'road':((.055,.060,.065,1),(.095,.100,.105,1)), 'paving':((.31,.29,.26,1),(.42,.40,.36,1)), 'curb':((.40,.41,.40,1),(.53,.54,.52,1))}[kind]
    for e,c in zip(ramp.color_ramp.elements,colors):e.color=c
    base=ramp.outputs['Color']
    if kind=='road':
        offset=spec.d('road_width')/6
        band=op('MINIMUM',op('ABSOLUTE',op('SUBTRACT',sep.outputs['X'],offset)),op('ABSOLUTE',op('ADD',sep.outputs['X'],offset)))
        stripe=op('MULTIPLY',op('LESS_THAN',band,spec.d('stripe_width')/2),op('LESS_THAN',op('FLOORED_MODULO',op('ADD',sep.outputs['Y'],half),spec.d('dash_period')),spec.d('dash_length')))
        stripe.node.name='LANE_MARKING_MASK'
        mix=n.new('ShaderNodeMixRGB');l.new(stripe,mix.inputs[0]);l.new(base,mix.inputs[1]);mix.inputs[2].default_value=(.64,.63,.55,1);base=mix.outputs[0]
    else:
        # Regular slab joints; world-space phase remains unchanged across modules.
        yjoint=op('LESS_THAN',op('FLOORED_MODULO',op('ADD',sep.outputs['Y'],half),1 if kind=='curb' else .4),.009)
        joint=yjoint
        if kind=='paving':
            xjoint=op('LESS_THAN',op('FLOORED_MODULO',sep.outputs['X'],.455),.009)
            joint=op('MAXIMUM',joint,xjoint)
        mix=n.new('ShaderNodeMixRGB');l.new(joint,mix.inputs[0]);l.new(base,mix.inputs[1]);mix.inputs[2].default_value=(.12,.115,.10,1);base=mix.outputs[0]
    l.new(base,bs.inputs['Base Color']);return m
def build(spec):
    al.clear_scene(); mats={k:material(k,k,spec) for k in ['road','paving','curb']}
    verify.markings(mats['road'])
    r=spec.d('road_width')/2;p=spec.d('pavement_width');c=spec.d('curb_width')
    h=spec.d('pavement_height');bottom=-spec.d('base_depth');half=spec.d('length')/2;b=spec.d('curb_chamfer')
    dimensions={'road':(-r,r,bottom,0),'pavement_left':(-r-p,-r-c,bottom,h),'pavement_right':(r+c,r+p,bottom,h),'curb_left':(-r-c,-r,bottom,h),'curb_right':(r,r+c,bottom,h)}
    parts={}
    for name,(x0,x1,z0,z1) in dimensions.items():
        if name.startswith('curb'):
            # Bevel only the road-facing top arris: exact end planes and no doubled end caps beyond module.
            s=1 if name.endswith('right') else -1
            cross=[(r,bottom),(r+c,bottom),(r+c,h),(r+b,h),(r,h-b)]
            verts=[(s*x,y,z) for y in [-half,half] for x,z in cross];count=len(cross)
            faces=[tuple(range(count-1,-1,-1)),tuple(range(count,2*count))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
            mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(mats['curb'])
            import bmesh
            bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
        else:o=al.box(name,(x1-x0,spec.d('length'),z1-z0),((x0+x1)/2,0,(z0+z1)/2),mats['road' if name=='road' else 'paving'],bevel=0)
        parts[name]=[o]
    bpy.context.view_layer.update();return parts
if __name__=='__main__':
    parts=build(pl.Spec(HERE/'spec.json'));checks=verify.geometry(parts);(HERE/'out').mkdir(exist_ok=True)
    (HERE/'out/geometry_checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks))
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'street_kit.blend'))
    if '--export' in sys.argv:pl.bake_shared_and_export(parts,{k:(0,0,0) for k in parts},HERE/'out','ST_Street',res=2048,samples=32)
