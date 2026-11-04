using System.Text.Json;
using OpenTK.Mathematics;
using RunnerGame.Rendering;

namespace RunnerGame.Animation;

public sealed record ConeIntroSample(float Time, Vector3 Rider, Vector3 Scooter, Vector3 Officer,
    Vector3 Cone, Vector3 CameraPosition, Vector3 CameraTarget, float ConeRock, float RiderYaw,
    float OfficerFrame=0, float OfficerOtherFrame=0, float OfficerBlend=0, float OfficerYaw=0);
public sealed record IntroRenderState(ConeIntroScene Scene, float Time);

/// <summary>Validated immutable tracks. Coordinates use the local route-start frame.</summary>
public sealed class ConeIntroScene
{
    private readonly Dictionary<string,(float Time,Vector3 Position)[]> tracks=[];
    public string Folder { get; }
    public string ClipPath { get; }
    public string OfficerClipPath { get; }
    public float Duration => ConeIntroController.Duration;
    private readonly HashSet<float> cameraCuts=[];
    public string RiderTexture { get; }
    public string ConeModel { get; }
    public string? ConeGeometryPath { get; }
    public IReadOnlyList<IntroCue> Cues { get; }
    private readonly Dictionary<string,Vector3> stages=[];
    public Vector3 StageOffset(string key) => stages.TryGetValue(key,out var value)?value:Vector3.Zero;
    public static ConeIntroScene Load(string folder) => new(folder);
    private ConeIntroScene(string folder)
    {
        Folder=Path.GetFullPath(folder);
        using var document=JsonDocument.Parse(File.ReadAllText(ModelManifest.Resolve(Folder,"scene.json")));
        var root=document.RootElement;
        if(root.GetProperty("version").GetInt32()!=2 || root.GetProperty("duration").GetSingle()!=Duration) throw new InvalidDataException("Unsupported intro scene.");
        ClipPath=ModelManifest.Resolve(Folder,root.GetProperty("clip").GetString()!);
        OfficerClipPath=ModelManifest.Resolve(Folder,root.GetProperty("officerClip").GetString()!);
        foreach(var cut in root.GetProperty("cameraCuts").EnumerateArray()) cameraCuts.Add(cut.GetSingle());
        RiderTexture=root.GetProperty("riderTexture").GetString()!;
        ConeModel=root.GetProperty("cone").GetString()!;
        if(root.TryGetProperty("coneGeometry",out var coneGeometry))ConeGeometryPath=ModelManifest.Resolve(Folder,coneGeometry.GetString()!);
        Cues=root.GetProperty("cues").EnumerateArray().Select(x=>new IntroCue(x.GetProperty("id").GetString()!,x.GetProperty("time").GetSingle(),x.GetProperty("sound").GetString()!)).ToArray();
        _=new ConeIntroController(Cues);
        foreach(var property in root.GetProperty("tracks").EnumerateObject())
        {
            var keys=property.Value.EnumerateArray().Select(x=>x.EnumerateArray().Select(y=>y.GetSingle()).ToArray()).ToArray();
            if(keys.Length<2 || keys.Length>2000 || keys.Any(k=>k.Length!=4 || k.Any(v=>!float.IsFinite(v))) || keys[0][0]!=0 || keys[^1][0]!=Duration)
                throw new InvalidDataException("Invalid intro track.");
            for(int i=1;i<keys.Length;i++) if(keys[i][0]<=keys[i-1][0]) throw new InvalidDataException("Unsorted intro track.");
            tracks.Add(property.Name,keys.Select(k=>(k[0],new Vector3(k[1],k[2],k[3]))).ToArray());
        }
        foreach(string key in new[]{"rider","scooter","officer","cone","camera","target","riderYaw"}) if(!tracks.ContainsKey(key)) throw new InvalidDataException("Missing intro track: "+key);
        foreach(var stage in root.GetProperty("stages").EnumerateObject())
        {
            float[] values=stage.Value.EnumerateArray().Select(x=>x.GetSingle()).ToArray();
            if(values.Length!=3 || values.Any(v=>!float.IsFinite(v))) throw new InvalidDataException("Invalid stage offset.");
            stages.Add(stage.Name,new(values[0],values[1],values[2]));
        }
    }
    private Vector3 Track(string key,float time)
    {
        var keys=tracks[key]; int i=0;
        while(i<keys.Length-2 && keys[i+1].Time<time) i++;
        float t=Math.Clamp((time-keys[i].Time)/(keys[i+1].Time-keys[i].Time),0,1);
        if(key is "camera" or "target")
        {
            if(cameraCuts.Contains(keys[i+1].Time) && time<keys[i+1].Time)return keys[i].Position;
            t=t*t*(3-2*t);
        }
        return Vector3.Lerp(keys[i].Position,keys[i+1].Position,t);
    }
    public ConeIntroSample Sample(float seconds)
    {
        if(!float.IsFinite(seconds) || seconds<0) throw new ArgumentOutOfRangeException(nameof(seconds));
        float t=Math.Min(Duration,seconds);
        float rock=t>=17?MathF.Sin((t-17)*23)*.28f*MathF.Exp(-(t-17)*3):0;
        var cone=Track("cone",t);
        // The selected 50cm cone has a 30cm base. Rock about its lower edge,
        // lifting the centre so the base never clips through the ground plane.
        if(t>=17) cone.Y=.15f*MathF.Abs(MathF.Sin(rock));
        var rider=Track("rider",t);var scooter=Track("scooter",t);var officer=Track("officer",t);
        float yaw=Track("riderYaw",t).X;
        if(t is >20 and <24)
        {var velocity=Track("rider",Math.Min(Duration,t+.01f))-Track("rider",Math.Max(0,t-.01f));if(velocity.LengthSquared>1e-8)yaw=MathF.Atan2(-velocity.X,-velocity.Z);}
        var eye=Track("camera",t);var target=Track("target",t);
        if(t>=27)
        {
            float blend=Smooth((t-27)/3);
            eye=Vector3.Lerp(new(3,2,scooter.Z+2.8f),new(0,2.8f,scooter.Z+5.5f),blend);
            target=Vector3.Lerp(new(0,1,scooter.Z),new(0,1,scooter.Z-10),blend);
        }
        float frame,other=0,mix=0,officerYaw=0;
        if(t<11)frame=2+((49-officer.Z)%1)*32;
        else if(t<17f)
        {frame=0;other=1;mix=Smooth((t-11)/.35f)*(1-Smooth((t-12.3f)/.9f));officerYaw=.27f*Smooth((t-10.8f)/.8f);}
        else if(t<20f)
        {
            float distance=1.25f*Smooth((t-17)/3f);
            frame=2+(distance%1)*32;mix=1-Smooth((t-17)/.3f);
        }
        else
        {
            frame=35+(Math.Max(0,40.75f-officer.Z)/1.7f%1)*40;
            other=2+(.25f*32);mix=1-Smooth((t-20f)/.6f);
            var velocity=Track("officer",Math.Min(Duration,t+.01f))-Track("officer",Math.Max(0,t-.01f));
            if(velocity.LengthSquared>1e-8)officerYaw=MathF.Atan2(-velocity.X,-velocity.Z);
        }
        return new(t,rider,scooter,officer,cone,eye,target,rock,yaw,frame,other,mix,officerYaw);
    }
    private static float Smooth(float t){t=Math.Clamp(t,0,1);return t*t*(3-2*t);}
}
