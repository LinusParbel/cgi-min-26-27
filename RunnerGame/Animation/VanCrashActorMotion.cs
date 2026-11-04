using OpenTK.Mathematics;
using RunnerGame.Gameplay;

namespace RunnerGame.Animation;

public readonly record struct VanCrashActorSample(Matrix4 RiderTransform,Matrix4 ScooterTransform,float RidePoseWeight,bool Visible);

/// <summary>Rider and scooter share one fall, preserving deck/foot and bar/hand contact.</summary>
public static class VanCrashActorMotion
{
    public const float FallStart=3.3f;
    static float Smooth(float x){x=Math.Clamp(x,0,1);return x*x*(3-2*x);}
    public static VanCrashActorSample Sample(VanCrashState state)
    {
        float t=state.Time,age=Math.Max(0,t-FallStart);
        float y=state.PlayerY*(1-Smooth(t/1.5f))-7*age*age;
        float z=state.ReboundZ*Smooth(t/1.1f);
        var shared=Matrix4.CreateRotationX(-.35f*Smooth(age/.5f))*
            Matrix4.CreateRotationZ(.22f*Smooth(age/.6f))*Matrix4.CreateTranslation(state.PlayerX,y,z);
        float ride=t>=FallStart?1:Smooth((t-3)/.3f);
        float hover=.14f*Smooth((t-1.5f)/.75f)*(1-ride);
        var rider=ride==1?shared:Matrix4.CreateTranslation(0,hover,0)*shared;
        return new(rider,shared,ride,y> -8);
    }
}
