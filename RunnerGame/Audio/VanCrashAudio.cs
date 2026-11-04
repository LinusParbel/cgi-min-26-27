using System.Runtime.InteropServices;
using RunnerGame.Gameplay;

namespace RunnerGame.Audio;

/// <summary>One scene mix on a private waveOut device. Pause retains the exact buffer position.</summary>
internal sealed class VanCrashAudio : IDisposable
{
    readonly byte[] pcm;
    readonly int rate;
    readonly bool muted;
    readonly float volume;
    IntPtr device,header;
    GCHandle pinned;
    VanCrashState? active;
    bool paused,unavailable;
    float bufferStart;
    [StructLayout(LayoutKind.Explicit,Size=12)]
    struct Position { [FieldOffset(0)] public uint Type; [FieldOffset(4)] public uint Samples; }
    [StructLayout(LayoutKind.Sequential,Pack=2)]
    struct Format { public ushort Tag,Channels; public uint Rate,BytesPerSecond; public ushort Align,Bits,Extra; }
    [StructLayout(LayoutKind.Sequential)]
    struct Header { public IntPtr Data; public uint Length,Recorded; public UIntPtr User; public uint Flags,Loops; public IntPtr Next; public UIntPtr Reserved; }
    [DllImport("winmm.dll")] static extern uint waveOutOpen(out IntPtr h,uint id,ref Format f,IntPtr callback,IntPtr instance,uint flags);
    [DllImport("winmm.dll")] static extern uint waveOutPrepareHeader(IntPtr h,IntPtr p,uint n);
    [DllImport("winmm.dll")] static extern uint waveOutWrite(IntPtr h,IntPtr p,uint n);
    [DllImport("winmm.dll")] static extern uint waveOutPause(IntPtr h);
    [DllImport("winmm.dll")] static extern uint waveOutRestart(IntPtr h);
    [DllImport("winmm.dll")] static extern uint waveOutReset(IntPtr h);
    [DllImport("winmm.dll")] static extern uint waveOutUnprepareHeader(IntPtr h,IntPtr p,uint n);
    [DllImport("winmm.dll")] static extern uint waveOutClose(IntPtr h);
    [DllImport("winmm.dll")] static extern uint waveOutSetVolume(IntPtr h,uint volume);
    [DllImport("winmm.dll")] static extern uint waveOutGetPosition(IntPtr h,ref Position position,uint size);
    internal float PlaybackTime
    {
        get
        {
            if(device==IntPtr.Zero)return float.NaN;
            var position=new Position {Type=2};
            return waveOutGetPosition(device,ref position,12)==0 && position.Type==2 ? bufferStart+position.Samples/(float)rate : float.NaN;
        }
    }
    public VanCrashAudio(string path,bool muted,float volume=1)
    {
        if(!float.IsFinite(volume)||volume<0||volume>1)throw new ArgumentOutOfRangeException(nameof(volume));
        this.muted=muted||volume==0;this.volume=volume;
        using var r=new BinaryReader(File.OpenRead(path));
        if(new string(r.ReadChars(4))!="RIFF")throw new InvalidDataException("Expected scene WAV");
        r.ReadUInt32();if(new string(r.ReadChars(4))!="WAVE")throw new InvalidDataException("Expected WAVE");
        byte[]? data=null;bool valid=false;
        while(r.BaseStream.Position+8<=r.BaseStream.Length) {
            string id=new(r.ReadChars(4));int size=r.ReadInt32();long next=r.BaseStream.Position+size+(size&1);
            if(size<0||next>r.BaseStream.Length)throw new InvalidDataException("Invalid WAV chunk");
            if(id=="fmt ") {if(size<16)throw new InvalidDataException("Invalid WAV format");ushort tag=r.ReadUInt16(),channels=r.ReadUInt16();rate=r.ReadInt32();r.ReadInt32();ushort align=r.ReadUInt16(),bits=r.ReadUInt16();valid=tag==1&&channels==1&&rate==44100&&align==2&&bits==16;}
            if(id=="data")data=r.ReadBytes(size);
            r.BaseStream.Position=next;
        }
        if(!valid||data==null||data.Length!=(int)(rate*2*VanCrashState.Duration))throw new InvalidDataException("Scene PCM mix duration must match van-crash playback");
        pcm=data;
    }
    public void Update(RunSimulation run)
    {
        var scene=run.VanCrash;
        if(!ReferenceEquals(scene,active)) {Stop();active=scene;}
        if(scene==null||scene.Complete) {Stop();return;}
        bool playing=run.Phase==RunPhase.VanCrash;
        if(muted||unavailable||!OperatingSystem.IsWindows())return;
        if(device!=IntPtr.Zero && playing && !paused && Math.Abs(PlaybackTime-scene.Time)>.075f)Stop();
        if(device==IntPtr.Zero && playing)Start(scene.Time);
        if(device!=IntPtr.Zero && paused==playing) {
            if(playing)waveOutRestart(device);else waveOutPause(device);
            paused=!playing;
        }
    }
    void Start(float seconds)
    {
        var format=new Format {Tag=1,Channels=1,Rate=(uint)rate,BytesPerSecond=(uint)rate*2,Align=2,Bits=16};
        if(waveOutOpen(out device,uint.MaxValue,ref format,IntPtr.Zero,IntPtr.Zero,0)!=0) {device=IntPtr.Zero;unavailable=true;Console.Error.WriteLine("Van crash audio device unavailable; scene remains playable.");return;}
        uint level=(uint)MathF.Round(volume*ushort.MaxValue);waveOutSetVolume(device,level|(level<<16));
        int offset=Math.Clamp((int)(seconds*rate)*2,0,pcm.Length-2);
        bufferStart=offset/(2f*rate);
        pinned=GCHandle.Alloc(pcm,GCHandleType.Pinned);
        header=Marshal.AllocHGlobal(Marshal.SizeOf<Header>());
        Marshal.StructureToPtr(new Header {Data=pinned.AddrOfPinnedObject()+offset,Length=(uint)(pcm.Length-offset)},header,false);
        uint size=(uint)Marshal.SizeOf<Header>();
        if(waveOutPrepareHeader(device,header,size)!=0||waveOutWrite(device,header,size)!=0) {Stop();unavailable=true;Console.Error.WriteLine("Van crash audio playback failed.");}
        paused=false;
    }
    void Stop()
    {
        if(device!=IntPtr.Zero) {waveOutReset(device);if(header!=IntPtr.Zero)waveOutUnprepareHeader(device,header,(uint)Marshal.SizeOf<Header>());waveOutClose(device);device=IntPtr.Zero;}
        if(header!=IntPtr.Zero){Marshal.FreeHGlobal(header);header=IntPtr.Zero;}
        if(pinned.IsAllocated)pinned.Free();paused=false;
    }
    public void Dispose()=>Stop();
}
