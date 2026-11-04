using System.Text.Json;
using OpenTK.Mathematics;

namespace RunnerGame.Animation;

/// <summary>Distance-driven officer approach and exported hand contact for the ticket gag.</summary>
public sealed class VanTicketMotion
{
    public const float ReleaseTime=7.7f;
    readonly Vector3[] hands;
    readonly float fps;
    VanTicketMotion(Vector3[] hands,float fps){this.hands=hands;this.fps=fps;}
    public static VanTicketMotion Load(string path)
    {
        using var json=JsonDocument.Parse(File.ReadAllText(path));
        float fps=json.RootElement.GetProperty("fps").GetSingle();
        var points=json.RootElement.GetProperty("hand").EnumerateArray().Select(p=> {
            var a=p.EnumerateArray().Select(v=>v.GetSingle()).ToArray();
            if(a.Length!=3 || a.Any(v=>!float.IsFinite(v)))throw new InvalidDataException("Invalid ticket hand track");
            return new Vector3(a[0],a[1],a[2]);
        }).ToArray();
        if(!float.IsFinite(fps)||fps<=0||points.Length<2)throw new InvalidDataException("Invalid ticket track rate/count");
        return new(points,fps);
    }
    public Vector3 HandAt(float seconds)
    {
        float frame=Math.Clamp(seconds*fps,0,hands.Length-1);int i=(int)frame;
        return Vector3.Lerp(hands[i],hands[Math.Min(i+1,hands.Length-1)],frame-i);
    }
    public static float ApproachDistance(float seconds)
    {
        const float speed=11.5f/2.7f;
        float age=Math.Clamp(seconds-2.5f,0,2.9f);
        if(age<=2.5f)return speed*age;
        float brake=age-2.5f;
        return speed*(2.5f+brake-brake*brake/.8f);
    }
    public static Vector3 FallingTicket(float seconds,Vector3 release)
    {
        float age=Math.Max(0,seconds-ReleaseTime);
        float flutter=Math.Min(1,age*5);
        float drift=Math.Clamp(age/1.2f,0,1);drift=drift*drift*(3-2*drift);
        return release+new Vector3(.075f*MathF.Sin(age*7)*flutter,-.3f*age-.7f*age*age,-1.10f*drift);
    }
}
