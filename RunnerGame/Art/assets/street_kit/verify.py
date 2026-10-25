"""Contract checks run before baking; exported OBJ checks run with --obj."""
import json, math
from pathlib import Path
HERE = Path(__file__).resolve().parent
EXPECTED = {'road':(-3.75,3.75,-.12,0), 'pavement_left':(-5.75,-3.93,-.12,.15), 'pavement_right':(3.93,5.75,-.12,.15), 'curb_left':(-3.93,-3.75,-.12,.15), 'curb_right':(3.75,3.93,-.12,.15)}
def markings(material):
    """Evaluate the actual shader mask graph at independent contract positions."""
    def evaluate(socket,x,y):
        if not socket.is_linked:return socket.default_value
        source=socket.links[0].from_socket;node=source.node
        if node.bl_idname=='ShaderNodeSeparateXYZ':return x if source.name=='X' else y
        assert node.bl_idname=='ShaderNodeMath',node.bl_idname
        a=evaluate(node.inputs[0],x,y);b=evaluate(node.inputs[1],x,y)
        return {'ADD':lambda:a+b,'SUBTRACT':lambda:a-b,'MULTIPLY':lambda:a*b,'ABSOLUTE':lambda:abs(a),'MINIMUM':lambda:min(a,b),'LESS_THAN':lambda:float(a<b),'FLOORED_MODULO':lambda:a%b}[node.operation]()
    mask=material.node_tree.nodes['LANE_MARKING_MASK']
    # Evaluate via the mix input linked to mask, validating production graph.
    mix=next(l.to_socket for l in material.node_tree.links if l.from_node==mask)
    for y in [-9,-4,1,6]:
        for x in [-3.75,-2.5,0,2.5,3.75]:assert evaluate(mix,x,y)==0,(x,y)
        for centre in [-1.25,1.25]:
            for dx in [-.05,0,.05]:assert evaluate(mix,centre+dx,y)==1,(centre,dx,y)
            for dx in [-.07,.07]:assert evaluate(mix,centre+dx,y)==0
    for y in [-6, -1,4,9]:
        for x in [-1.25,1.25]:assert evaluate(mix,x,y)==0
    for x in [-1.25,0,1.25]:assert evaluate(mix,x,-10)==evaluate(mix,x,10)
    print('MARKING CONTRACT PASS: two 0.12m dividers +/-1.25m; three 2.5m lanes; 3m/2m dash; matching ends')
def check_bounds(name, vs):
    lo = [min(v[i] for v in vs) for i in range(3)]
    hi = [max(v[i] for v in vs) for i in range(3)]
    x0,x1,z0,z1=EXPECTED[name]
    assert all(abs(a-b)<1e-5 for a,b in zip(lo+hi,[x0,-10,z0,x1,10,z1])), (name,lo,hi)
    assert all(math.isfinite(c) for v in vs for c in v)
    return {'min':lo,'max':hi}
def geometry(parts):
    assert set(parts)==set(EXPECTED)
    result={}; total=0
    for name,objs in parts.items():
        vs=[o.matrix_world @ v.co for o in objs for v in o.data.vertices]
        tris=sum(len(p.vertices)-2 for o in objs for p in o.data.polygons)
        result[name]={'bounds':check_bounds(name,vs),'triangles':tris}; total+=tris
    assert total<=3000
    return {'total_triangles':total,'parts':result}
def exported():
    import struct
    png=(HERE/'out/ST_Street.png').read_bytes()
    assert png[:8]==b'\x89PNG\r\n\x1a\n'
    assert struct.unpack('>II',png[16:24])==(2048,2048)
    info=json.loads((HERE/'out/ST_Street_parts.json').read_text()); assert len(info['parts'])==5
    result={}; total=0
    for p in info['parts']:
        assert p['pivot']==[0,0,0]
        vs=[]; uv=[]; normals=[]; faces=[]
        for line in (HERE/'out'/p['obj']).read_text().splitlines():
            t=line.split()
            if not t: continue
            if t[0]=='v': vs.append([float(t[1]),-float(t[3]),float(t[2])])
            elif t[0]=='vt': uv.append(list(map(float,t[1:3])))
            elif t[0]=='vn': normals.append(list(map(float,t[1:4])))
            elif t[0]=='f': faces.append(t[1:])
        for f in faces:
            assert len(f)==3
            ids=[list(map(int,v.split('/'))) for v in f]
            assert all(len(i)==3 and 0<i[0]<=len(vs) and 0<i[1]<=len(uv) and 0<i[2]<=len(normals) for i in ids)
            a,b,c=[vs[i[0]-1] for i in ids]
            u=[b[j]-a[j] for j in range(3)];v=[c[j]-a[j] for j in range(3)]
            assert sum((u[(j+1)%3]*v[(j+2)%3]-u[(j+2)%3]*v[(j+1)%3])**2 for j in range(3))>1e-16
        assert all(math.isfinite(c) for v in uv+normals for c in v)
        assert all(abs(sum(c*c for c in v)-1)<.01 for v in normals)
        assert all(-1e-6<=c<=1.000001 for v in uv for c in v)
        result[p['name']]={'bounds':check_bounds(p['name'],vs),'triangles':len(faces)};total+=len(faces)
    assert total<=3000
    report={'total_triangles':total,'parts':result,'valid_uv_normals_faces':True}
    (HERE/'out/export_checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__': exported()
