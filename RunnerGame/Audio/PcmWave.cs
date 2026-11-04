namespace RunnerGame.Audio;

public sealed record PcmWave(int Channels,int SampleRate,byte[] Data)
{
    public static PcmWave Read(string path)
    {
        using var stream=File.OpenRead(path);
        if(stream.Length<44 || stream.Length>64*1024*1024) throw new InvalidDataException("Invalid WAV size.");
        using var r=new BinaryReader(stream);
        string Tag()=>System.Text.Encoding.ASCII.GetString(r.ReadBytes(4));
        if(Tag()!="RIFF") throw new InvalidDataException("Expected RIFF WAV.");
        uint size=r.ReadUInt32(); if(size+8L!=stream.Length || Tag()!="WAVE") throw new InvalidDataException("Invalid WAV length/type.");
        int channels=0,rate=0; byte[]? data=null;
        while(stream.Position+8<=stream.Length)
        {
            string tag=Tag(); uint length=r.ReadUInt32(); long end=stream.Position+length;
            if(end>stream.Length) throw new InvalidDataException("WAV chunk exceeds file.");
            if(tag=="fmt ")
            {
                if(length<16 || r.ReadUInt16()!=1) throw new InvalidDataException("Expected PCM WAV.");
                channels=r.ReadUInt16(); rate=r.ReadInt32(); int bytesPerSecond=r.ReadInt32(); int alignment=r.ReadUInt16(),bits=r.ReadUInt16();
                if(channels is <1 or >2 || rate is <8000 or >192000 || bits!=16 || alignment!=channels*2 || bytesPerSecond!=rate*alignment)
                    throw new InvalidDataException("Expected mono/stereo PCM16.");
            }
            else if(tag=="data") data=r.ReadBytes((int)length);
            stream.Position=end+(length&1);
        }
        if(channels==0 || data==null || data.Length==0 || data.Length%(channels*2)!=0) throw new InvalidDataException("WAV data/format missing.");
        return new(channels,rate,data);
    }
}
