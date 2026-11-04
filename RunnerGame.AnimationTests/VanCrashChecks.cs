using Engine.Geometry;
using OpenTK.Mathematics;
using RunnerGame.Animation;
using RunnerGame.Rendering;

static class VanCrashChecks
{
    public static void Run()
    {
        foreach(float t in new[]{3.3f,3.4f,3.57f,3.8f,4.1f}) {
            var run=new RunnerGame.Gameplay.RunSimulation();run.PrepareVanCrashPreview();
            while(run.VanCrash==null)run.Step(.02f);
            run.Step(t);var pair=VanCrashActorMotion.Sample(run.VanCrash!);
            if(pair.RiderTransform!=pair.ScooterTransform || pair.RidePoseWeight!=1)
                throw new Exception($"Rider and scooter separate during fall at {t}");
            if(t>3.3f && pair.ScooterTransform.ExtractTranslation().Y>=0)
                throw new Exception("Scooter still hangs after the rider starts falling");
        }
        if(Math.Abs(VanTicketMotion.ApproachDistance(5.4f)-11.5f)>.001f || VanTicketMotion.ApproachDistance(2.5f)!=0)
            throw new Exception("Officer did not stop on the near edge");
        var release=new Vector3(.67f,1.17f,1.94f);
        if(Vector3.Distance(VanTicketMotion.FallingTicket(7.7f,release),release)>.001f)throw new Exception("Ticket teleported at release");
        foreach(float time in new[]{7.8f,8.2f,8.8f,9.5f}) {
            var p=VanTicketMotion.FallingTicket(time,release);
            if(p.Y>=release.Y||p.X<=-1.25f||p.X>=1.25f||p.Z<=-.65f||p.Z>=2.05f)throw new Exception("Ticket misses opening");
        }
        foreach(bool left in new[]{true,false}) {
            var flap=VanCrashRoadGeometry.CreateFlap(left);
            if(flap.Vertices.Any(v=>v.Normal.Y<.99f))throw new Exception("Closed road flap is lit from below");
        }
        string root=Path.Combine(AppContext.BaseDirectory,"Assets","Animations","VanCrash");
        var hand=VanTicketMotion.Load(Path.Combine(root,"officer-ticket-hand.json"));
        if(!float.IsFinite(hand.HandAt(7.7f).LengthSquared))throw new Exception("Invalid ticket grip");
        var localHand=hand.HandAt(7.7f);
        var worldHand=new Vector3(.45f-localHand.X,localHand.Y,2.35f-localHand.Z);
        if(Math.Abs(worldHand.X)>=1.25f || worldHand.Z<=-.65f || worldHand.Z>=2.05f)
            throw new Exception("Evaluated release grip is outside the opening");
        if(Vector3.Distance(VanTicketMotion.FallingTicket(7.7f,worldHand),worldHand)>.001f)
            throw new Exception("Actual ticket grip jumps on release");
        using(var officer=VertexClip.Open(Path.Combine(root,"officer-ticket.vclip"))) {
            var poses=new Vertex[officer.VertexCount];
            for(int frame=0;frame<=132;frame++) {
                officer.Sample(frame/12f,poses);
                if(poses.Min(v=>v.Position.Y)<-.002f)throw new Exception($"Officer feet penetrate street at frame {frame}");
            }
        }
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
