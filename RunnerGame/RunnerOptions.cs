using System.Globalization;
namespace RunnerGame;

public sealed class RunnerOptions
{
    public string? Capture {get;private set;}
    public string? MapFolder {get;private set;}
    public bool Overview {get;private set;}
    public float? Inspect {get;private set;}
    public bool Duck {get;private set;}
    public float Advance {get;private set;}
    public float? IntroTime {get;private set;}
    public string? RecordIntro {get;private set;}
    public bool Mute {get;private set;}
    public bool DisableCulling {get;private set;}
    public float Volume {get;private set;}=1;
    public bool VanCrashPreview {get;private set;}
    public bool ConeCrashPreview {get;private set;}
    public float CrashTime {get;private set;}
    public float CrashDistance {get;private set;}
    public string? CrashFilm {get;private set;}
    public Gameplay.VanCrashPreviewContact CrashContact {get;private set;}
    public static RunnerOptions Parse(string[] args)
    {
        var o=new RunnerOptions();
        for(int i=0;i<args.Length;i++)
        {
            string Value(){if(i+1>=args.Length)throw new ArgumentException("Missing value for "+args[i]);return args[++i];}
            float Number(float max)
            {if(!float.TryParse(Value(),NumberStyles.Float,CultureInfo.InvariantCulture,out float v)||!float.IsFinite(v)||v<0||v>max)throw new ArgumentException("Invalid numeric option.");return v;}
            switch(args[i])
            {
                case "--capture":o.Capture=Path.GetFullPath(Value());break;
                case "--map":o.MapFolder=Path.GetFullPath(Value());break;
                case "--overview":o.Overview=true;break;
                case "--inspect":o.Inspect=Number(float.MaxValue);break;
                case "--duck":o.Duck=true;break;
                case "--advance":o.Advance=Number(60);break;
                case "--intro-time":o.IntroTime=Number(ConeIntroDuration);break;
                case "--record-intro":o.RecordIntro=Path.GetFullPath(Value());break;
                case "--mute":o.Mute=true;break;
                case "--no-culling":o.DisableCulling=true;break;
                case "--volume":o.Volume=Number(1);break;
                case "--cone-crash-preview":o.ConeCrashPreview=true;break;
                case "--van-crash-preview":o.VanCrashPreview=true;break;
                case "--crash-distance":o.CrashDistance=Number(100000);break;
                case "--crash-time":o.CrashTime=Number(Gameplay.ConeCrashState.Duration);break;
                case "--crash-film":o.CrashFilm=Path.GetFullPath(Value());break;
                case "--crash-contact":
                    if(!Enum.TryParse(Value(),true,out Gameplay.VanCrashPreviewContact contact)||!Enum.IsDefined(contact))throw new ArgumentException("Invalid crash contact.");
                    o.CrashContact=contact;break;
                default:throw new ArgumentException("Unknown option: "+args[i]);
            }
        }
        if(o.Capture==null&&(o.Duck||o.Advance>0||o.IntroTime.HasValue))throw new ArgumentException("--duck, --advance and --intro-time require --capture.");
        if(o.MapFolder==null&&(o.Overview||o.Inspect.HasValue))throw new ArgumentException("--overview and --inspect require --map.");
        if(o.IntroTime.HasValue&&(o.Duck||o.Advance>0||o.Overview||o.Inspect.HasValue))throw new ArgumentException("Intro captures cannot combine gameplay/inspection options.");
        if(o.RecordIntro!=null&&(o.Capture!=null||o.Overview||o.Inspect.HasValue))throw new ArgumentException("Recording cannot combine capture/inspection options.");
        if(o.MapFolder!=null&&(o.IntroTime.HasValue||o.RecordIntro!=null))throw new ArgumentException("The cinematic intro currently supports road mode only.");
        if(o.VanCrashPreview && o.ConeCrashPreview)throw new ArgumentException("Choose one crash preview.");
        if((o.VanCrashPreview||o.ConeCrashPreview)&&(o.MapFolder!=null||o.IntroTime.HasValue||o.RecordIntro!=null||o.Duck||o.Advance>0))throw new ArgumentException("Crash previews require street mode without intro or gameplay capture options.");
        if(o.CrashDistance>0 && !(o.ConeCrashPreview||o.VanCrashPreview))throw new ArgumentException("--crash-distance requires a crash preview.");
        if(o.CrashTime>0&&(!(o.VanCrashPreview||o.ConeCrashPreview)||o.Capture==null))throw new ArgumentException("--crash-time requires a crash preview and --capture.");
        if(o.CrashFilm!=null&&(!(o.VanCrashPreview||o.ConeCrashPreview)||o.Capture!=null))throw new ArgumentException("--crash-film requires a crash preview without --capture.");
        if(!o.ConeCrashPreview && o.CrashTime>Gameplay.VanCrashState.Duration)throw new ArgumentException("Van crash timestamp exceeds duration.");
        return o;
    }
    private const float ConeIntroDuration=Animation.ConeIntroController.Duration;
}
