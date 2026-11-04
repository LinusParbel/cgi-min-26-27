using OpenTK.Audio.OpenAL;
using RunnerGame.Animation;
using RunnerGame.Rendering;

namespace RunnerGame.Audio;

/// <summary>Small device adapter; deterministic event ownership remains in OpeningSequence.</summary>
public sealed class IntroAudio : IIntroAudio
{
    private ALDevice device;
    private ALContext context;
    private readonly Dictionary<string,int> buffers=[];
    private readonly List<int> sources=[];
    private bool available,paused,disposed;
    private float volume=1;
    public string Diagnostics { get; private set; }="Audio unavailable";
    public IntroAudio(string folder)
    {
        try
        {
            device=ALC.OpenDevice(null);
            if(device==ALDevice.Null) { Diagnostics="No audio device; playback continues silently."; Console.WriteLine(Diagnostics); return; }
            context=ALC.CreateContext(device,new ALContextAttributes());
            if(context==ALContext.Null || !ALC.MakeContextCurrent(context)) throw new InvalidOperationException("Cannot initialise audio context.");
            available=true;
            foreach(string name in new[]{"ambience","step","walk_short","mount_step","run","handling","kickstand","call","hey","stop","stop_firm","stop_angry","pursuit","impact","beep","takeoff"})
            {
                var wave=PcmWave.Read(ModelManifest.Resolve(folder,$"audio/{name}.wav"));
                int buffer=AL.GenBuffer(); buffers.Add(name,buffer);
                AL.BufferData(buffer,wave.Channels==1?ALFormat.Mono16:ALFormat.Stereo16,wave.Data,wave.SampleRate);
            }
            Diagnostics="OpenAL device ready; intro PCM sound buffers loaded.";
        }
        catch(Exception ex) when(ex is DllNotFoundException or InvalidOperationException or TypeInitializationException)
        { Release(); Diagnostics="Audio unavailable: "+ex.Message; }
        catch { Release(); throw; }
        Console.WriteLine(Diagnostics);
    }
    public void SetVolume(float value)
    {
        if(!float.IsFinite(value) || value<0 || value>1) throw new ArgumentOutOfRangeException(nameof(value));
        volume=value; if(available) foreach(int source in sources) AL.Source(source,ALSourcef.Gain,volume);
    }
    public void Play(IntroCue cue)
    {
        ObjectDisposedException.ThrowIf(disposed,this);
        if(!available)return;
        for(int i=sources.Count-1;i>=0;i--)
            if(State(sources[i])==ALSourceState.Stopped) { AL.DeleteSource(sources[i]); sources.RemoveAt(i); }
        if(!buffers.TryGetValue(cue.Sound,out int buffer)) throw new InvalidDataException("Unknown intro sound: "+cue.Sound);
        int source=AL.GenSource(); sources.Add(source); AL.Source(source,ALSourcei.Buffer,buffer);
        AL.Source(source,ALSourcef.Gain,volume); AL.Source(source,ALSourceb.Looping,cue.Sound=="ambience");
        AL.SourcePlay(source); if(paused) AL.SourcePause(source);
    }
    public void SetPaused(bool value)
    {
        if(paused==value)return; paused=value;
        if(!available)return;
        foreach(int source in sources)
        {
            var state=State(source);
            if(value && state==ALSourceState.Playing) AL.SourcePause(source);
            else if(!value && state==ALSourceState.Paused) AL.SourcePlay(source);
        }
    }
    public void Reset()
    {
        if(available) foreach(int source in sources) { AL.SourceStop(source); AL.DeleteSource(source); }
        sources.Clear(); paused=false;
    }
    private static ALSourceState State(int source)
    { AL.GetSource(source,ALGetSourcei.SourceState,out int state); return (ALSourceState)state; }
    private void Release()
    {
        if(available) { Reset(); foreach(int buffer in buffers.Values) AL.DeleteBuffer(buffer); buffers.Clear(); }
        available=false;
        if(context!=ALContext.Null) { ALC.MakeContextCurrent(ALContext.Null); ALC.DestroyContext(context); context=ALContext.Null; }
        if(device!=ALDevice.Null) { ALC.CloseDevice(device); device=ALDevice.Null; }
    }
    public void Dispose() { if(disposed)return; Release(); disposed=true; }
}
