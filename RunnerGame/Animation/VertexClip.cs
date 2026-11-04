using System.IO.Compression;
using Engine.Geometry;
using OpenTK.Mathematics;

namespace RunnerGame.Animation;

/// <summary>Indexed, fixed-topology animation. Only the two current frames are decoded.</summary>
public sealed class VertexClip : IDisposable
{
    private readonly FileStream file;
    private readonly Vector2[] uv;
    private readonly (long Offset, int Length)[] frames;
    private readonly Dictionary<int,float[]> cache = [];
    private readonly float fps;
    private bool disposed;
    public int VertexCount => uv.Length;
    public uint[] Indices { get; }
    public int CachedFrames => cache.Count;
    public float Duration => (frames.Length - 1) / fps;
    public static VertexClip Open(string path)
    {
        var stream = File.OpenRead(path);
        try { return new(stream); }
        catch (Exception ex) when(ex is EndOfStreamException or OverflowException or ArgumentOutOfRangeException)
        { stream.Dispose(); throw new InvalidDataException("Truncated or oversized vertex clip.",ex); }
        catch { stream.Dispose(); throw; }
    }
    private VertexClip(FileStream stream)
    {
        file=stream; using var reader=new BinaryReader(file,System.Text.Encoding.UTF8,true);
        string magic=System.Text.Encoding.ASCII.GetString(reader.ReadBytes(4));
        if(magic is not ("VCL1" or "VCL2")) throw new InvalidDataException("Unknown clip format.");
        int nv=reader.ReadInt32(), ni=reader.ReadInt32(), nf=reader.ReadInt32(); fps=reader.ReadSingle();
        if(nv is <1 or >100000 || ni is <3 or >600000 || ni%3!=0 || nf is <2 or >2000 || !float.IsFinite(fps) || fps<=0 || fps>120)
            throw new InvalidDataException("Invalid clip dimensions/rate.");
        if(20L+nv*8L+ni*4L+nf*12L>file.Length) throw new InvalidDataException("Truncated clip header.");
        uv=new Vector2[nv]; Indices=new uint[ni]; frames=new (long,int)[nf];
        for(int i=0;i<nv;i++) { uv[i]=new(reader.ReadSingle(),reader.ReadSingle()); if(!float.IsFinite(uv[i].X+uv[i].Y)) throw new InvalidDataException("Invalid UV."); }
        for(int i=0;i<ni;i++) { Indices[i]=reader.ReadUInt32(); if(Indices[i]>=nv) throw new InvalidDataException("Invalid clip index."); }
        long minimum=20L+nv*8L+ni*4L+nf*12L, prior=minimum;
        for(int i=0;i<nf;i++)
        {
            long offset=reader.ReadInt64(); int length=reader.ReadInt32();
            if(offset<minimum || (magic=="VCL1" && offset<prior) || length<=0 || length>nv*24+65536 || offset>file.Length-length)
                throw new InvalidDataException("Invalid frame bounds.");
            frames[i]=(offset,length); prior=offset+length;
        }
        var distinct=frames.Distinct().OrderBy(f=>f.Offset).ToArray();
        for(int i=1;i<distinct.Length;i++) if(distinct[i].Offset<distinct[i-1].Offset+distinct[i-1].Length)
            throw new InvalidDataException("Clip frames partially overlap.");
    }
    public void Sample(float seconds, Span<Vertex> destination)
    {
        ObjectDisposedException.ThrowIf(disposed,this);
        if(!float.IsFinite(seconds) || seconds<0) throw new ArgumentOutOfRangeException(nameof(seconds));
        if(destination.Length!=VertexCount) throw new ArgumentException("Vertex count differs from clip.");
        float position=Math.Min(frames.Length-1,seconds*fps);
        int left=(int)position,right=Math.Min(left+1,frames.Length-1); float fraction=position-left;
        foreach(var key in cache.Keys.Where(k=>k!=left && k!=right).ToArray()) cache.Remove(key);
        float[] a=ReadFrame(left),b=ReadFrame(right);
        for(int i=0;i<VertexCount;i++)
        {
            int j=i*6;
            var p=Vector3.Lerp(new(a[j],a[j+1],a[j+2]),new(b[j],b[j+1],b[j+2]),fraction);
            var n=Vector3.Lerp(new(a[j+3],a[j+4],a[j+5]),new(b[j+3],b[j+4],b[j+5]),fraction);
            n=n.LengthSquared>1e-12f?Vector3.Normalize(n):Vector3.UnitY;
            destination[i]=new(p,n,uv[i]);
        }
    }
    private float[] ReadFrame(int index)
    {
        if(cache.TryGetValue(index,out var result)) return result;
        foreach(var existing in cache)
            if(frames[existing.Key]==frames[index]) {result=existing.Value;cache.Add(index,result);return result;}
        var frame=frames[index]; file.Position=frame.Offset;
        byte[] packed=new byte[frame.Length]; file.ReadExactly(packed);
        using var input=new MemoryStream(packed,false);
        using var deflate=new DeflateStream(input,CompressionMode.Decompress);
        byte[] bytes=new byte[VertexCount*12];
        try { deflate.ReadExactly(bytes); } catch(EndOfStreamException ex) { throw new InvalidDataException("Truncated decoded frame.",ex); }
        if(deflate.ReadByte()!=-1) throw new InvalidDataException("Oversized decoded frame.");
        result=new float[VertexCount*6];
        for(int i=0;i<result.Length;i++) result[i]=(float)BitConverter.UInt16BitsToHalf(System.Buffers.Binary.BinaryPrimitives.ReadUInt16LittleEndian(bytes.AsSpan(i*2,2)));
        if(result.Any(v=>!float.IsFinite(v))) throw new InvalidDataException("Nonfinite clip vertex.");
        cache.Add(index,result); return result;
    }
    public void Dispose() { if(disposed)return; disposed=true; cache.Clear(); file.Dispose(); }
}
