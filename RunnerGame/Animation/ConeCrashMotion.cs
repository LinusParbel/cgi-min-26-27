using System.Text.Json;
using Engine.Geometry.Loaders;
using RunnerGame.Rendering;
using OpenTK.Mathematics;
using RunnerGame.Gameplay;

namespace RunnerGame.Animation;

public readonly record struct ConeCrashSample(Matrix4 Rider, Matrix4 Scooter, Matrix4 Officer,
    Matrix4 Ticket, Vector3 Back, Vector3 Hand, Vector3 Eye, Vector3 Target, bool RiderVisible, bool TicketVisible);

/// <summary>One authored timeline, shared by rendering and contact/camera verification.</summary>
public sealed class ConeCrashMotion
{
    public const float Release = 1.4f, Jump = 4.1f, Attach = 7.3f, Withdraw = 7.65f, Departure = 10f, Vanish = 16.2f;
    readonly Vector3[] backs, normals, hands, scooterGroundPoints;
    readonly float fps;
    public ConeCrashMotion(string folder)
    {
        using var rider = JsonDocument.Parse(File.ReadAllText(Path.Combine(folder,"rider-contact.json")));
        using var officer = JsonDocument.Parse(File.ReadAllText(Path.Combine(folder,"officer-contact.json")));
        fps = rider.RootElement.GetProperty("fps").GetSingle();
        Vector3[] Read(JsonElement root,string name) => root.GetProperty(name).EnumerateArray().Select(p => {
            var a=p.EnumerateArray().Select(v=>v.GetSingle()).ToArray();
            if(a.Length!=3 || a.Any(v=>!float.IsFinite(v)))throw new InvalidDataException("Invalid cone contact track.");
            return new Vector3(a[0],a[1],a[2]);
        }).ToArray();
        backs=Read(rider.RootElement,"back"); normals=Read(rider.RootElement,"normal"); hands=Read(officer.RootElement,"hand");
        if(!float.IsFinite(fps)||fps<=0 || officer.RootElement.GetProperty("fps").GetSingle()!=fps ||
           backs.Length!=normals.Length || hands.Length!=backs.Length || backs.Length!=(int)(ConeCrashState.Duration*fps)+1)
            throw new InvalidDataException("Cone contact timeline mismatch.");
        string models=Path.GetFullPath(Path.Combine(folder,"..","..","Models"));
        scooterGroundPoints=ModelManifest.Read(Path.Combine(models,"Fahrzeug","ScooterVoi","VEH_ScooterVoi_parts.json"))
            .SelectMany(part=>ObjLoader.Load(part.ObjPath).Vertices.Select(v=>v.Position+part.Pivot)).Distinct().ToArray();
    }
    public static float Smooth(float x) { x=Math.Clamp(x,0,1);return x*x*(3-2*x); }
    Vector3 Track(Vector3[] points,float t)
    {
        float f=Math.Clamp(t*fps,0,points.Length-1);int i=(int)f;
        return Vector3.Lerp(points[i],points[Math.Min(i+1,points.Length-1)],f-i);
    }
    static Matrix4 Pivot(ConeCrashState s,float t)
    {
        float approach=Smooth(t/.35f);
        float u=Math.Clamp((t-.35f)/(Release-.35f),0,1);
        float a=-1.15f*u*u;
        return Matrix4.CreateTranslation(0,-.127f,.424f)*Matrix4.CreateRotationX(a)*
            Matrix4.CreateTranslation(s.PlayerX+(s.ConeX-s.PlayerX)*approach,.127f+s.PlayerY*(1-Smooth(t/Release))+9*RampDistance(t-1.1f,.3f),(s.ConeZ+.716f)*approach-.424f);
    }
    // Integral of smoothstep: continuous velocity, including ramps between flight speeds.
    static float RampDistance(float age,float ramp)
    {
        if(age<=0)return 0;
        float u=age/ramp;
        return u>=1?age-ramp*.5f:ramp*(u*u*u-.5f*u*u*u*u);
    }
    public static float RunDistance(float t) => 5.5f*(RampDistance(t-2,.35f)-RampDistance(t-3.85f,.25f));
    public static float RunSpeed(float t) => 5.5f*(Smooth((t-2)/.35f)-Smooth((t-3.85f)/.25f));
    public static float RunFrame(float t) => 35+(RunDistance(t)/1.7f%1)*40;
    static Vector3 ReleaseVelocity(Vector3 localPoint)
    {
        const float angle=-1.15f,rate=-2*1.15f/(Release-.35f);
        float y=localPoint.Y-.127f,z=localPoint.Z+.424f;
        return new(0,(-y*MathF.Sin(angle)-z*MathF.Cos(angle))*rate+9,
            (y*MathF.Cos(angle)-z*MathF.Sin(angle))*rate);
    }
    static float FlipAngle(float age)
    {
        const float duration=1.65f,start=-1.15f,rate=-2*1.15f/(Release-.35f);
        float u=Math.Clamp(age/duration,0,1),u2=u*u,u3=u2*u;
        return start*(2*u3-3*u2+1)+rate*duration*(u3-2*u2+u)-2*MathF.PI*(-2*u3+3*u2);
    }
    static Vector3 Centre(ConeCrashState s,float t)
    {
        var start=Vector3.TransformPosition(new Vector3(0,1,0),Pivot(s,Release));
        var velocity=ReleaseVelocity(new Vector3(0,1,0));
        float age=Math.Max(0,t-Release),initial=RampDistance(age,.25f),slow=RampDistance(age-1,1.8f),late=RampDistance(age-7,2);
        return start+new Vector3(.12f*initial,velocity.Y*age+(7.5f-velocity.Y)*initial-3.5f*slow+5*late,
            velocity.Z*age+(-3.2f-velocity.Z)*initial-12*late);
    }
    public static Vector3 DeparturePoint(ConeCrashState s) => Centre(s,Vanish);
    Matrix4 Rider(ConeCrashState s,float t)
    {
        if(t<=Release)return Pivot(s,t);
        float drift=Math.Max(0,t-3.05f);
        return Matrix4.CreateTranslation(0,-1,0)*Matrix4.CreateRotationX(FlipAngle(t-Release)+.08f*MathF.Sin(drift*1.4f)*Smooth(drift/.5f))*
            Matrix4.CreateRotationZ(.12f*Smooth((t-2)/2)+.06f*MathF.Sin(drift*1.7f)*Smooth(drift/.5f))*Matrix4.CreateTranslation(Centre(s,t));
    }
    Vector3 Back(ConeCrashState s,float t) => Vector3.TransformPosition(Track(backs,t),Rider(s,t));
    Vector3 Normal(ConeCrashState s,float t) => Vector3.Normalize(Vector3.TransformNormal(Track(normals,t),Rider(s,t)));
    static readonly Matrix4 OfficerRotation=Matrix4.CreateRotationY(MathF.PI);
    public Vector3 OfficerRoot(ConeCrashState s,float t)
    {
        var start=new Vector3(s.PlayerX+.6f,0,12-RunDistance(Jump));
        if(t<=Jump)return new(s.PlayerX+.6f,0,12-RunDistance(t));
        // One ballistic interception, solved once at the slap. No mid-air attachment of actors.
        var end=Back(s,Attach)+Normal(s,Attach)*.014f-Vector3.TransformPosition(Track(hands,Attach),OfficerRotation);
        float duration=Attach-Jump,age=t-Jump;
        var velocity=(end-start)/duration+new Vector3(0,1.6f*duration,0);
        float push=RampDistance(t-Attach,.25f);
        float after=Math.Max(0,t-Attach);
        return start+velocity*age+new Vector3(2*push,-1.6f*age*age-2*push-3.4f*after*after,7*push);
    }
    public float ScooterGroundClearance(Matrix4 transform)
    {
        float minimum=float.PositiveInfinity;
        foreach(var point in scooterGroundPoints)minimum=Math.Min(minimum,Vector3.TransformPosition(point,transform).Y);
        return minimum;
    }
    public Matrix4 ScooterAt(ConeCrashState s,float t)
    {
        if(t<=Release)return Pivot(s,t);
        float age=t-Release;
        var rotation=Matrix4.CreateRotationX(FlipAngle(age))*
            Matrix4.CreateRotationZ(MathF.PI*.5f*Smooth((age-.7f)/1.3f));
        var start=Pivot(s,Release).ExtractTranslation();
        var velocity=ReleaseVelocity(Vector3.Zero);
        var position=start+new Vector3(.6f*Smooth(age/1.7f),velocity.Y*age-9*age*age,velocity.Z*(age-RampDistance(age,1.3f)));
        // Resolve every visible part against the real road, including handlebar and wheel pivots.
        float support=-ScooterGroundClearance(rotation)+.002f;
        position.Y=Math.Max(position.Y,support);
        return rotation*Matrix4.CreateTranslation(position);
    }
    public ConeCrashSample Sample(ConeCrashState s)
    {
        float t=s.Time;var rider=Rider(s,t);var back=Back(s,t);var normal=Normal(s,t);
        var up=Vector3.Normalize(Vector3.TransformNormal(Vector3.UnitY,rider));
        var right=Vector3.Cross(up,normal).Normalized();up=Vector3.Cross(normal,right).Normalized();
        var paperBasis=new Matrix4(new Vector4(right,0),new Vector4(up,0),new Vector4(normal,0),new Vector4(0,0,0,1));
        var root=OfficerRoot(s,t);var officer=OfficerRotation*Matrix4.CreateTranslation(root);
        var hand=Vector3.TransformPosition(Track(hands,t),officer);
        var paper=paperBasis*Matrix4.CreateTranslation(t<Attach?hand:back+normal*.014f);
        var scooter=ScooterAt(s,t);
        float followTime=Math.Min(t,Vanish);
        var centre=t<Release?Vector3.TransformPosition(new Vector3(0,1,0),rider):Centre(s,followTime);
        var launchEye=centre+new Vector3(3,1.2f,5);
        var launchTarget=centre+new Vector3(0,.15f,0);
        float establish=Smooth(t/.9f);
        launchEye=Vector3.Lerp(new(0,2.8f,5.5f),launchEye,establish);
        launchTarget=Vector3.Lerp(new(0,1,-10),launchTarget,establish);
        var officerEye=root+new Vector3(3,1.9f,4.8f);var officerTarget=root+new Vector3(0,1.15f,0);
        float reveal=Smooth((t-2.05f)/.75f),catchup=Smooth((t-5.2f)/1.8f);
        var eye=Vector3.Lerp(launchEye,officerEye,reveal);var target=Vector3.Lerp(launchTarget,officerTarget,reveal);
        var followOffset=Vector3.Lerp(new(-1.7f,.65f,2.6f),new(-2.5f,1.2f,5),Smooth((followTime-7.6f)/2.4f));
        followOffset=Vector3.Lerp(followOffset,new(6,5,32),Smooth((followTime-Departure)/(Vanish-Departure)));
        eye=Vector3.Lerp(eye,centre+followOffset,catchup);
        target=Vector3.Lerp(target,centre+new Vector3(0,.25f,0),catchup);
        // Keep low shots inside the road; release lateral clearance smoothly above the roofs.
        eye.X=Math.Clamp(eye.X,-3.2f,3.2f)+(eye.X-Math.Clamp(eye.X,-3.2f,3.2f))*Smooth((eye.Y-8)/5);
        return new(rider,scooter,officer,paper,back,hand,eye,target,t<Vanish,t>=6.3f && t<Vanish);
    }
}
