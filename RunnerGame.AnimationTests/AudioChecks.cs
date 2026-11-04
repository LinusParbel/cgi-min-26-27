using RunnerGame.Audio;

static class AudioChecks
{
    public static void Run()
    {
        var path=Path.GetTempFileName();
        try
        {
            File.WriteAllBytes(path,new byte[10]);
            try { PcmWave.Read(path); throw new Exception("Bad WAV accepted"); } catch(InvalidDataException) { }
            using(var stream=File.Create(path)) using(var w=new BinaryWriter(stream))
            {
                w.Write("RIFF"u8); w.Write(38); w.Write("WAVEfmt "u8); w.Write(16);
                w.Write((short)1); w.Write((short)1); w.Write(22050); w.Write(44100); w.Write((short)2); w.Write((short)16);
                w.Write("data"u8); w.Write(2); w.Write((short)1234);
            }
            var wave=PcmWave.Read(path); if(wave.SampleRate!=22050 || wave.Channels!=1 || wave.Data.Length!=2) throw new Exception("PCM WAV read");
            Console.WriteLine("PASS PCM WAV: valid mono PCM16 and invalid/truncated headers");
        } finally {File.Delete(path);}
    }
}
