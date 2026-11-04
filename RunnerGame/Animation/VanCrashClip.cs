using System.IO.Compression;
using Engine.Geometry;
using OpenTK.Mathematics;

namespace RunnerGame.Animation;

/// <summary>Scene-local fixed-topology, half-float vertex animation.</summary>
public sealed class VanCrashClip
{
    readonly Vector2[] uv;
    readonly ushort[][] frames;
    readonly float fps;
    public int VertexCount => uv.Length;
    public uint[] Indices { get; }
    private VanCrashClip(Vector2[] uv,uint[] indices,ushort[][] frames,float fps)
    { this.uv=uv; Indices=indices; this.frames=frames; this.fps=fps; }
    public static VanCrashClip Load(string path)
    {
        using var file=File.OpenRead(path);
        using var zip=new ZLibStream(file,CompressionMode.Decompress);
        using var r=new BinaryReader(zip);
        if(new string(r.ReadChars(4))!="VCR1") throw new InvalidDataException("Unknown crash clip format");
        int nv=r.ReadInt32(),ni=r.ReadInt32(),nf=r.ReadInt32();float fps=r.ReadSingle();
        if(nv is <1 or >100000 || ni is <3 or >600000 || ni%3!=0 || nf is <2 or >200 || !float.IsFinite(fps)||fps<=0||fps>60)
            throw new InvalidDataException("Invalid crash clip dimensions");
        var uv=new Vector2[nv];var indices=new uint[ni];var frames=new ushort[nf][];
        for(int i=0;i<nv;i++) {uv[i]=new(r.ReadSingle(),r.ReadSingle());if(!float.IsFinite(uv[i].X+uv[i].Y))throw new InvalidDataException("Invalid UV");}
        for(int i=0;i<ni;i++) {indices[i]=r.ReadUInt32();if(indices[i]>=nv)throw new InvalidDataException("Invalid index");}
        for(int f=0;f<nf;f++) {
            frames[f]=new ushort[nv*6];
            for(int j=0;j<frames[f].Length;j++) {ushort value=r.ReadUInt16();if(!System.Half.IsFinite(BitConverter.UInt16BitsToHalf(value)))throw new InvalidDataException("Invalid vertex");frames[f][j]=value;}
        }
        if(zip.ReadByte()!=-1) throw new InvalidDataException("Unexpected crash clip data");
        return new(uv,indices,frames,fps);
    }
    public void Sample(float seconds,Vertex[] output)
    {
        if(!float.IsFinite(seconds)||seconds<0)throw new ArgumentOutOfRangeException(nameof(seconds));
        if(output.Length!=VertexCount)throw new ArgumentException("Vertex count mismatch",nameof(output));
        float p=Math.Min(frames.Length-1,seconds*fps);int left=(int)p,right=Math.Min(left+1,frames.Length-1);float alpha=p-left;
        for(int i=0;i<VertexCount;i++) {
            float V(int c) {int j=i*6+c;float a=(float)BitConverter.UInt16BitsToHalf(frames[left][j]);float b=(float)BitConverter.UInt16BitsToHalf(frames[right][j]);return a+(b-a)*alpha;}
            var normal=new Vector3(V(3),V(4),V(5));normal=normal.LengthSquared>1e-10f?Vector3.Normalize(normal):Vector3.UnitY;
            output[i]=new(new Vector3(V(0),V(1),V(2)),normal,uv[i]);
        }
    }
}
