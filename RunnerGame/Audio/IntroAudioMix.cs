using RunnerGame.Animation;
using RunnerGame.Rendering;
namespace RunnerGame.Audio;

/// <summary>Offline mix for deterministic captures; no sound device or wall-clock timing.</summary>
public static class IntroAudioMix
{
    public static void Write(string folder,IReadOnlyList<IntroCue> cues,string output,int seconds=31)
    {
        const int rate=22050; var mix=new float[rate*seconds];
        foreach(var cue in cues)
        {
            var wave=PcmWave.Read(ModelManifest.Resolve(folder,$"audio/{cue.Sound}.wav"));
            if(wave.SampleRate!=rate||wave.Channels!=1)throw new InvalidDataException("Offline mix requires 22050Hz mono.");
            int start=(int)Math.Round(cue.Time*rate), count=wave.Data.Length/2;
            for(int i=start;i<mix.Length && (cue.Sound=="ambience"||i-start<count);i++)
            {int source=(i-start)%count;mix[i]+=BitConverter.ToInt16(wave.Data,source*2)/32768f;}
        }
        using var w=new BinaryWriter(File.Create(output));
        w.Write("RIFF"u8);w.Write(36+mix.Length*2);w.Write("WAVEfmt "u8);w.Write(16);w.Write((short)1);w.Write((short)1);
        w.Write(rate);w.Write(rate*2);w.Write((short)2);w.Write((short)16);w.Write("data"u8);w.Write(mix.Length*2);
        foreach(float sample in mix)w.Write((short)(Math.Clamp(sample,-.98f,.98f)*32767));
    }
}
