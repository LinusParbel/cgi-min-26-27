using Engine.Geometry;
using OpenTK.Mathematics;
using RunnerGame.Animation;
using RunnerGame.Gameplay;

static class ConeCrashChecks
{
    static void Check(bool value,string message) {if(!value)throw new Exception(message);}
    public static void Run()
    {
        string folder=Path.Combine(AppContext.BaseDirectory,"Assets","Animations","ConeCrash");
        var motion=new ConeCrashMotion(folder);
        using var rider=VertexClip.Open(Path.Combine(folder,"rider.vclip"));
        using var officer=VertexClip.Open(Path.Combine(folder,"officer.vclip"));
        Check(rider.Duration==17&&officer.Duration==17,"Cone clip durations");
        var verts=new Vertex[rider.VertexCount];var previous=new Vertex[rider.VertexCount];rider.Sample(0,previous);rider.Sample(3,verts);
        Check(verts.Zip(previous).Any(p=>(p.First.Position-p.Second.Position).Length>.1f),"Cone rider is rigid");
        var uniformStart=new Vertex[officer.VertexCount];var uniformReach=new Vertex[officer.VertexCount];
        officer.Sample(0,uniformStart);officer.Sample(88f/12,uniformReach);
        for(int triangle=0;triangle<officer.Indices.Length;triangle+=3)for(int edge=0;edge<3;edge++) {
            int a=(int)officer.Indices[triangle+edge],b=(int)officer.Indices[triangle+(edge+1)%3];
            Check(!((uniformStart[a].Position-uniformStart[b].Position).Length<.04f &&
                (uniformReach[a].Position-uniformReach[b].Position).Length>.18f),"Officer uniform stretches to a nearby hand");
        }
        foreach(var contact in Enum.GetValues<VanCrashPreviewContact>()) {
            var run=new RunSimulation();run.PrepareConeCrashPreview(contact);while(run.ConeCrash==null)run.Step(.02f);
            run.Step(.35f);var contactPose=motion.Sample(run.ConeCrash!);
            var axle=Vector3.TransformPosition(new Vector3(0,.127f,-.424f),contactPose.Scooter);
            Check(Math.Abs(axle.X-run.ConeCrash!.ConeX)<.001f && Math.Abs(axle.Z-.127f-(run.ConeCrash.ConeZ+.165f))<.002f,"Front wheel never meets cone base");
            run.Restart();run.PrepareConeCrashPreview(contact);while(run.ConeCrash==null)run.Step(.02f);
            run.Step(1.4f);var release=motion.Sample(run.ConeCrash!);run.Step(.0001f);var after=motion.Sample(run.ConeCrash!);
            Check((release.Scooter.ExtractTranslation()-after.Scooter.ExtractTranslation()).Length<.01f,"Scooter teleports at release");
            Check((release.Rider.ExtractTranslation()-after.Rider.ExtractTranslation()).Length<.01f,"Rider teleports at release");
            run.Restart();run.PrepareConeCrashPreview(contact);while(run.ConeCrash==null)run.Step(.02f);
            float prior=0;
            foreach(float t in new[]{0f,.8f,1.4f,2f,3.4f,4.1f,6.5f,7.299f,7.3f,7.7f,8.5f,10f,12f,14.8f,16.2f,17f}) {
                run.Step(t-prior);prior=t;var sample=motion.Sample(run.ConeCrash!);
                Check(float.IsFinite(sample.Rider.Determinant+sample.Officer.Determinant+sample.Eye.LengthSquared),"Nonfinite cone scene");
                Check((sample.Eye-sample.Target).Length>1,"Degenerate cone camera");
                if(t<=1.4f)Check(sample.Rider==sample.Scooter,"Scooter/rider separate before release");
                if(Math.Abs(t-ConeCrashMotion.Attach)<.0001f)Check((sample.Hand-sample.Back).Length<.025f,"Ticket palm misses back");
                if(t>=ConeCrashMotion.Attach&&t<ConeCrashMotion.Vanish)Check((sample.Ticket.ExtractTranslation()-sample.Back).Length<.025f,"Ticket leaves rider back");
                if(t>=8.5f&&t<=12)Check((sample.Hand-sample.Back).Length>.15f,"Officer hand never withdraws");
                if(t>=ConeCrashMotion.Vanish)Check(!sample.RiderVisible&&!sample.TicketVisible,"Departed rider remains visible");
            }
        }
        var flowing=new RunSimulation();flowing.PrepareConeCrashPreview();while(flowing.ConeCrash==null)flowing.Step(.02f);
        flowing.Step(2);float previousHeight=Vector3.TransformPosition(new Vector3(0,1,0),motion.Sample(flowing.ConeCrash!).Rider).Y;
        for(int i=0;i<1400;i++) {
            flowing.Step(.01f);var frame=motion.Sample(flowing.ConeCrash!);
            float height=Vector3.TransformPosition(new Vector3(0,1,0),frame.Rider).Y;
            Check(height>previousHeight+.035f,"Rider hovered or stopped climbing");previousHeight=height;
        }
        foreach(float boundary in new[]{1.4f,2.05f,2.8f,4.1f,5.2f,7f,7.3f,7.65f,10f,16.2f}) {
            var a=new RunSimulation();a.PrepareConeCrashPreview();while(a.ConeCrash==null)a.Step(.02f);a.Step(boundary-.0001f);
            var left=motion.Sample(a.ConeCrash!);a.Step(.0002f);var right=motion.Sample(a.ConeCrash!);
            Check((left.Eye-right.Eye).Length<.05f && (left.Target-right.Target).Length<.05f,"Camera cut in continuous pursuit");
        }
        var throwRun=new RunSimulation();throwRun.PrepareConeCrashPreview();while(throwRun.ConeCrash==null)throwRun.Step(.02f);
        throwRun.Step(ConeCrashMotion.Release-.001f);var beforeThrow=motion.Sample(throwRun.ConeCrash!);
        throwRun.Step(.001f);var atThrow=motion.Sample(throwRun.ConeCrash!);throwRun.Step(.001f);var afterThrow=motion.Sample(throwRun.ConeCrash!);
        foreach(var point in new[]{Vector3.Zero,new Vector3(0,1,0),new Vector3(0,1.6f,0)}) {
            Vector3 Velocity(Matrix4 a,Matrix4 b)=>(Vector3.TransformPosition(point,b)-Vector3.TransformPosition(point,a))/.001f;
            Check((Velocity(beforeThrow.Rider,atThrow.Rider)-Velocity(atThrow.Rider,afterThrow.Rider)).Length<.12f,"Rider velocity notches at release");
            Check((Velocity(beforeThrow.Scooter,atThrow.Scooter)-Velocity(atThrow.Scooter,afterThrow.Scooter)).Length<.12f,"Scooter velocity notches at release");
        }
        var carry=(Vector3.TransformPosition(new Vector3(0,1,0),atThrow.Rider)-Vector3.TransformPosition(new Vector3(0,1,0),beforeThrow.Rider))/.001f;
        Check(carry.Y>6,"Flip stops before beginning a separate launch");
        var turn=(Vector3.TransformNormal(Vector3.UnitY,atThrow.Rider)-Vector3.TransformNormal(Vector3.UnitY,beforeThrow.Rider))/.001f;
        Check(turn.Length>1.5f,"Flip rotation stops at release");
        var contactScene=new ConeCrashState(0,0,false,1,0,-1.03f);
        for(float t=1.4f;t<=6;t+=.02f)
            Check(motion.ScooterGroundClearance(motion.ScooterAt(contactScene,t))>=-.001f,"Scooter passes through the road during its flip or landing");
        Check(motion.ScooterGroundClearance(motion.ScooterAt(contactScene,6))<.004f,"Scooter does not settle onto the road");
        var approachRun=new RunSimulation();approachRun.PrepareConeCrashPreview();while(approachRun.ConeCrash==null)approachRun.Step(.02f);
        approachRun.Step(ConeCrashMotion.Jump);
        for(int i=0;i<64;i++) {
            var frame=motion.Sample(approachRun.ConeCrash!);
            Check(frame.Officer.ExtractTranslation().Y+1.3f<=frame.Back.Y+.12f,"Officer overshoots above the rider before the slap");
            approachRun.Step(.05f);
        }
        Check(ConeCrashMotion.RunDistance(4.1f)>9 && ConeCrashMotion.RunSpeed(3)>5,"Officer does not run before takeoff");
        Console.WriteLine("PASS cone pursuit: continuous rise/camera, run-up, shared pivot/release, passing slap, attachment, separation, uniform skin and departure");
    }
}
