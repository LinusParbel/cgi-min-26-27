using Engine.Geometry;
using OpenTK.Mathematics;

namespace RunnerGame.Rendering;

/// <summary>Two complementary jagged halves of the road, before hinge transforms.</summary>
public static class VanCrashRoadGeometry
{
    public static MeshData CreateFlap(bool left)
    {
        float outer=left?-1:1;
        float[] z=[-.65f,-.18f,.3f,.75f,1.2f,1.6f,2.05f];
        float[] edge=[0,.10f,-.08f,.13f,-.1f,.06f,0];
        var vertices=new List<Vertex>();var indices=new List<uint>();
        for(int i=0;i<z.Length-1;i++)
        {
            Vector3 a=new(outer,0,z[i]),b=new(outer,0,z[i+1]),c=new(edge[i+1],0,z[i+1]),d=new(edge[i],0,z[i]);
            if(!left)(b,d)=(d,b);
            Vector3 normal=Vector3.Normalize(Vector3.Cross(b-a,c-a));uint n=(uint)vertices.Count;
            foreach(var p in new[]{a,b,c,d})vertices.Add(new(p,normal,new Vector2(.978f,.728f)));
            indices.AddRange(new[]{n,n+1,n+2,n,n+2,n+3});
        }
        return new(vertices.ToArray(),indices.ToArray());
    }
}
