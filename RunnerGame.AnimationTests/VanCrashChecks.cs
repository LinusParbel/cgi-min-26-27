using Engine.Geometry;
using OpenTK.Mathematics;
using RunnerGame.Animation;
using RunnerGame.Rendering;

static class VanCrashChecks
{
    public static void Run()
    {
        foreach(bool left in new[]{true,false}) {
            var flap=VanCrashRoadGeometry.CreateFlap(left);
            if(flap.Vertices.Any(v=>v.Normal.Y<.99f))throw new Exception("Closed road flap is lit from below");
        }
        string root=Path.Combine(AppContext.BaseDirectory,"Assets","Animations","VanCrash");
        var clip=VanCrashClip.Load(Path.Combine(root,"rider.vcr"));
        var duck=VanCrashClip.Load(Path.Combine(root,"duck-start.vcr"));
        var a=new Vertex[clip.VertexCount]; var b=new Vertex[clip.VertexCount];
        clip.Sample(0,a); clip.Sample(2.8f,b);
        duck.Sample(0,b);
        if(a.Max(v=>v.Position.Y)-b.Max(v=>v.Position.Y)<.3f)throw new Exception("Duck contact lost its initial crouch");
        clip.Sample(2.8f,b);
        if (!a.Zip(b).Any(p=>Vector3.Distance(p.First.Position,p.Second.Position)>.1f)) throw new Exception("Crash actor remains rigid");
        foreach(float t in new[]{0f,.3f,1.5f,2.8f,3.7f,6f}) {
            clip.Sample(t,b);
            if(b.Any(v=>!float.IsFinite(v.Position.LengthSquared)||Math.Abs(v.Normal.Length-1)>.01f)) throw new Exception("Invalid sampled actor");
        }
        clip.Sample(20,b); var end=new Vertex[clip.VertexCount];clip.Sample(6,end);
        if(!b.Select(v=>v.Position).SequenceEqual(end.Select(v=>v.Position))) throw new Exception("Clip endpoint not clamped");
        Console.WriteLine("PASS crash clip: deforming frames, duck endpoint, finite normals, endpoint clamp");
    }
}
