using System.IO.Compression;
using Engine.Geometry;
using RunnerGame.Animation;

static class ClipChecks
{
    public static void Run()
    {
        var path = Path.GetTempFileName();
        try
        {
            using (var file = File.Create(path)) using (var w = new BinaryWriter(file))
            {
                w.Write("VCL1"u8); w.Write(3); w.Write(3); w.Write(2); w.Write(1f);
                for (int i=0;i<3;i++) { w.Write(0f); w.Write(0f); }
                for (uint i=0;i<3;i++) w.Write(i);
                long table=file.Position; w.Write(new byte[24]);
                for(int f=0;f<2;f++)
                {
                    long offset=file.Position;
                    using (var deflate=new DeflateStream(file,CompressionLevel.Fastest,true))
                    using (var frame=new BinaryWriter(deflate))
                        for(int i=0;i<3;i++) foreach(float value in new[]{(float)f,0,0,0,1,0}) frame.Write(BitConverter.HalfToUInt16Bits((Half)value));
                    long end=file.Position; file.Position=table+f*12; w.Write(offset); w.Write((uint)(end-offset)); file.Position=end;
                }
            }
            using (var clip=VertexClip.Open(path))
            {
                var vertices=new Vertex[3]; clip.Sample(.5f,vertices);
                if(Math.Abs(vertices[0].Position.X-.5f)>.00001 || vertices[0].Normal.Y!=1) throw new Exception("Clip interpolation");
                clip.Sample(12,vertices); if(vertices[0].Position.X!=1) throw new Exception("Clip clamps endpoint");
                clip.Sample(0,vertices); clip.Sample(.5f,vertices);
                if(clip.CachedFrames>2) throw new Exception("Unbounded clip cache");
            }
            var original=File.ReadAllBytes(path);
            var aliased=(byte[])original.Clone();
            "VCL2"u8.CopyTo(aliased);
            Array.Copy(aliased,56,aliased,68,12);
            File.WriteAllBytes(path,aliased);
            using(var shared=VertexClip.Open(path)) {var v=new Vertex[3];shared.Sample(.5f,v);if(v[0].Position.X!=0)throw new Exception("Aliased hold frame changed");}
            void RejectFile(byte[] data)
            {
                File.WriteAllBytes(path,data);
                try { using var bad=VertexClip.Open(path); throw new Exception("Malformed clip accepted"); } catch(InvalidDataException) { }
            }
            var oversized=(byte[])original.Clone(); BitConverter.GetBytes(100001).CopyTo(oversized,4); RejectFile(oversized);
            var index=(byte[])original.Clone(); BitConverter.GetBytes(99u).CopyTo(index,44); RejectFile(index);
            var badOffset=(byte[])original.Clone(); BitConverter.GetBytes(0L).CopyTo(badOffset,56); RejectFile(badOffset);
            var bytes=(byte[])original.Clone(); bytes[0]=0; File.WriteAllBytes(path,bytes);
            try { using var bad=VertexClip.Open(path); throw new Exception("Bad magic accepted"); } catch(InvalidDataException) { }
            File.WriteAllBytes(path,new byte[3]);
            try { using var bad=VertexClip.Open(path); throw new Exception("Truncation accepted"); } catch(InvalidDataException) { }
            Console.WriteLine("PASS vertex clip: interpolation, normals, endpoints, bounded seek/cache, invalid magic/counts/indices/offsets/truncation");
        } finally { File.Delete(path); }
    }
}
