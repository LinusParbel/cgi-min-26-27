using Engine.Geometry;
using OpenTK.Mathematics;

namespace RunnerGame.Rendering;

public readonly record struct StreetBackdropBuilding(Vector3 Centre, Vector3 Size, bool Brick);

/// <summary>Closed building volumes and a batched surrounding district, reusing shared street/shop atlases.</summary>
public static class StreetCityGeometry
{
    static readonly Vector2 Masonry=new(.035f,.08f),Roof=new(.19f,.08f);
    static readonly Vector2 Asphalt=new(.08f,.35f),Paving=new(.58f,.35f);
    sealed class Builder
    {
        readonly List<Vertex> vertices=[];
        readonly List<uint> indices=[];
        public void Add(MeshData mesh,Matrix4 transform,Vector2? wall=null,Vector2? top=null)
        {
            uint start=(uint)vertices.Count;
            var inverse=Matrix4.Invert(transform);var normals=Matrix4.Transpose(inverse);
            foreach(var v in mesh.Vertices) {
                var normal=Vector3.TransformNormal(v.Normal,normals).Normalized();
                var uv=wall.HasValue?(v.Normal.Y>.5f?top??wall.Value:wall.Value):v.TexCoord;
                vertices.Add(new(Vector3.TransformPosition(v.Position,transform),normal,uv));
            }
            foreach(uint index in mesh.Indices)indices.Add(start+index);
        }
        public void Box(Vector3 low,Vector3 high,Vector2 wall,Vector2 roof)
            =>Add(Primitives.CreateCube(1),Matrix4.CreateScale(high-low)*Matrix4.CreateTranslation((low+high)*.5f),wall,roof);
        public MeshData Finish()=>new(vertices.ToArray(),indices.ToArray());
    }
    public static MeshData CreateFacadeCore()
    {
        var b=new Builder();
        b.Box(new(-3,0,-8.4f),new(3,6.4f,-.25f),Masonry,Roof);
        // Low parapet and small roof fixtures give the aerial silhouette a finished surface.
        b.Box(new(-3,6.4f,-8.4f),new(-2.85f,6.58f,-.25f),Masonry,Roof);
        b.Box(new(2.85f,6.4f,-8.4f),new(3,6.58f,-.25f),Masonry,Roof);
        b.Box(new(-3,6.4f,-8.4f),new(3,6.58f,-8.25f),Masonry,Roof);
        b.Box(new(-1.9f,6.4f,-5.8f),new(-.8f,6.9f,-4.6f),Roof,Roof);
        b.Box(new(1.2f,6.4f,-3.1f),new(1.65f,7.1f,-2.65f),Masonry,Roof);
        return b.Finish();
    }
    public static MeshData CreateStreetBuilding(MeshData shop,MeshData upper)
    {
        var b=new Builder();b.Add(CreateFacadeCore(),Matrix4.Identity);b.Add(shop,Matrix4.Identity);
        b.Add(upper,Matrix4.CreateTranslation(0,3.2f,0));return b.Finish();
    }
    public static float WrappedDistance(float a,float b)
    {
        float delta=Math.Abs(a-b)%420;
        return Math.Min(delta,420-delta);
    }
    public static IReadOnlyList<StreetBackdropBuilding> Buildings()
    {
        var result=new List<StreetBackdropBuilding>();
        for(int row=0;row<5;row++)for(int column=0;column<17;column++)foreach(int side in new[]{-1,1}) {
            float x=side*(23+row*26),z=-12-column*24;
            var size=new Vector3(10+(row*7+column*5+row*column)%5*2,7.7f+(row+column*3)%4*1.5f,12+(row+column)%3*2);
            // Reserve the complete existing plazas, enclosing wings and landmark footprints.
            bool townHall=x-size.X*.5f< -5 && x+size.X*.5f> -135 && WrappedDistance(z,-6)<58+size.Z*.5f;
            bool clock=x-size.X*.5f<28 && x+size.X*.5f>5 && WrappedDistance(z,18)<25+size.Z*.5f;
            if(townHall||clock)continue;
            result.Add(new(new(x,.15f,z),size,(row+column)%3==0));
        }
        return result;
    }
    public static MeshData CreateNeighbourhood(MeshData shop,MeshData sandstone,MeshData brick)
    {
        var b=new Builder();var core=CreateFacadeCore();
        foreach(var building in Buildings()) {
            var scale=building.Size/new Vector3(6,6.4f,8.4f);
            var world=Matrix4.CreateScale(scale)*Matrix4.CreateTranslation(building.Centre+new Vector3(0,0,4*scale.Z));
            void Facade(Matrix4 local) {
                b.Add(shop,local*world);
                b.Add(building.Brick?brick:sandstone,Matrix4.CreateTranslation(0,3.2f,0)*local*world);
            }
            b.Add(core,world);Facade(Matrix4.Identity);
            Facade(Matrix4.CreateRotationY(MathF.PI)*Matrix4.CreateTranslation(0,0,-8));
            Facade(Matrix4.CreateScale(8f/6,1,1)*Matrix4.CreateRotationY(MathF.PI/2)*Matrix4.CreateTranslation(3,0,-4));
            Facade(Matrix4.CreateScale(8f/6,1,1)*Matrix4.CreateRotationY(-MathF.PI/2)*Matrix4.CreateTranslation(-3,0,-4));
        }
        return b.Finish();
    }
    public static MeshData CreateNeighbourhoodPaving()
    {
        var b=new Builder();
        foreach(var building in Buildings()) {
            var half=building.Size*.5f;
            b.Box(new(building.Centre.X-half.X-1,0,building.Centre.Z-half.Z-1),
                new(building.Centre.X+half.X+1,.14f,building.Centre.Z+half.Z+1),Paving,Paving);
        }
        return b.Finish();
    }
    public static MeshData CreateGround()
    {
        var b=new Builder();
        // The road owns its own surface and the van scene can open it: never cap that opening underneath.
        b.Box(new(-230,-.35f,-630),new(-3.75f,-.14f,210),Asphalt,Asphalt);
        b.Box(new(3.75f,-.35f,-630),new(230,-.14f,210),Asphalt,Asphalt);
        return b.Finish();
    }
}
