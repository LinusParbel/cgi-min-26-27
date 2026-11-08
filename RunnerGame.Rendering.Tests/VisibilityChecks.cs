using Engine;
using Engine.Geometry;
using Engine.Geometry.Loaders;
using OpenTK.Mathematics;
using RunnerGame.Animation;
using RunnerGame.Rendering;

static class VisibilityChecks
{
    public static void Run()
    {
        int checks=0;
        void Check(bool value,string message) {if(!value)throw new Exception(message);checks++;}
        var camera=new Camera(Vector3.Zero,-Vector3.UnitZ){NearPlane=1,FarPlane=10,FieldOfViewDegrees=90};
        var matrix=camera.ViewMatrix*camera.GetProjectionMatrix(1);
        var view=new ViewFrustum(matrix);
        Bounds3 Box(Vector3 center,float half=.1f)=>new(center-new Vector3(half),center+new Vector3(half));
        Check(view.Intersects(Box(new(0,0,-3))),"Visible object rejected.");
        foreach(var point in new[]{new Vector3(-5,0,-3),new(5,0,-3),new(0,-5,-3),new(0,5,-3),new(0,0,-.5f),new(0,0,-11),new(0,0,3)})
            Check(!view.Intersects(Box(point)),"Outside clip plane accepted: "+point);
        Check(view.Intersects(Box(new(0,0,-1),.2f)),"Near-plane intersection rejected.");
        Check(view.Intersects(Box(Vector3.Zero,20)),"Camera-inside volume rejected.");
        Check(view.Intersects(Box(new(3,0,-3),.2f)),"Side-plane intersection rejected.");

        var random=new Random(884);
        for(int i=0;i<1000;i++)
        {
            var bounds=Box(new(random.NextSingle()*20-10,random.NextSingle()*20-10,random.NextSingle()*24-12),random.NextSingle()*2+.01f);
            var transform=Matrix4.CreateScale(-.5f,2,3)*Matrix4.CreateRotationY(random.NextSingle()*6)*Matrix4.CreateRotationX(.3f)*Matrix4.CreateTranslation(3,2,-4);
            var corners=new List<Vector3>();
            foreach(float x in new[]{bounds.Min.X,bounds.Max.X})foreach(float y in new[]{bounds.Min.Y,bounds.Max.Y})foreach(float z in new[]{bounds.Min.Z,bounds.Max.Z})
                corners.Add(Vector3.TransformPosition(new(x,y,z),transform));
            var transformed=bounds.Transform(transform);
            Check((transformed.Min-new Vector3(corners.Min(p=>p.X),corners.Min(p=>p.Y),corners.Min(p=>p.Z))).Length<.0001f
                && (transformed.Max-new Vector3(corners.Max(p=>p.X),corners.Max(p=>p.Y),corners.Max(p=>p.Z))).Length<.0001f,"Transformed bounds lost a corner.");
            var clip=new List<Vector4>();
            foreach(float x in new[]{bounds.Min.X,bounds.Max.X})foreach(float y in new[]{bounds.Min.Y,bounds.Max.Y})foreach(float z in new[]{bounds.Min.Z,bounds.Max.Z})
                clip.Add(new Vector4(x,y,z,1)*matrix);
            bool outside=clip.All(p=>p.X < -p.W-.001f)||clip.All(p=>p.X>p.W+.001f)
                ||clip.All(p=>p.Y < -p.W-.001f)||clip.All(p=>p.Y>p.W+.001f)
                ||clip.All(p=>p.Z < -p.W-.001f)||clip.All(p=>p.Z>p.W+.001f);
            Check(view.Intersects(bounds)||outside,"Plane extraction disagrees with clip-space reference.");
        }

        camera=new Camera(new(0,2.8f,5.5f),new(0,1,-10)){NearPlane=.08f,FarPlane=300,FieldOfViewDegrees=58};
        view=new(camera.ViewMatrix*camera.GetProjectionMatrix(1.6f));
        var light=new ViewFrustum(MapShadowPass.CreateLightSpace(Vector3.Zero));
        foreach(float elapsed in new[]{0f,1,10,100})
        {
            var hidden=PursuerVisibility.RunBounds.Transform(PursuerVisibility.Transform(elapsed,elapsed*10,0,false));
            Check(!PursuerVisibility.IsNeeded(hidden,view,light),"Hidden pursuer still requests animation.");
        }
        var close=PursuerVisibility.RunBounds.Transform(PursuerVisibility.Transform(10,100,0,true));
        Check(PursuerVisibility.IsNeeded(close,view,light),"Close pursuer was culled.");
        // A caster outside the image can still shadow the visible road.
        var caster=Box(new(-5,12,2),1);
        Check(!view.Intersects(caster)&&light.Intersects(caster),"Offscreen caster fixture is invalid.");
        Check(PursuerVisibility.IsNeeded(caster,view,light),"Visible shadow influence was culled.");

        string root=Path.GetFullPath("RunnerGame/Assets");
        using(var clip=VertexClip.Open(Path.Combine(root,"Animations/ConeHat/officer_motion.vclip")))
        {
            var vertices=new Vertex[clip.VertexCount];
            for(int frame=35;frame<=75;frame++) {
                clip.Sample(frame/24f,vertices);var b=Bounds3.FromVertices(vertices);
                var full=PursuerVisibility.RunBounds;
                Check(b.Min.X>=full.Min.X && b.Min.Y>=full.Min.Y && b.Min.Z>=full.Min.Z
                    && b.Max.X<=full.Max.X && b.Max.Y<=full.Max.Y && b.Max.Z<=full.Max.Z,"Run bound does not contain complete clip pose at "+frame+": "+b);
            }
        }
        string models=Path.Combine(root,"Models/Gebaeude/ShopfrontKit");
        var shop=ObjLoader.Load(Path.Combine(models,"AR_Shopfront_shop_ground.obj"));
        var stone=ObjLoader.Load(Path.Combine(models,"AR_Shopfront_sandstone_upper.obj"));
        var brick=ObjLoader.Load(Path.Combine(models,"AR_Shopfront_brick_upper.obj"));
        var whole=StreetCityGeometry.CreateNeighbourhood(shop,stone,brick);
        var chunks=StreetCityGeometry.CreateNeighbourhoodChunks(shop,stone,brick);
        Check(chunks.Count>20 && chunks.Count<StreetCityGeometry.Buildings().Count,"Chunks are not spatial groups.");
        Check(chunks.Sum(c=>c.Indices.Length)==whole.Indices.Length && chunks.Sum(c=>c.Vertices.Length)==whole.Vertices.Length,"Chunk split changed geometry counts.");
        // Full vertex multiset verifies geometry, normals and UVs survive regrouping.
        var expected=whole.Vertices.GroupBy(v=>v).ToDictionary(g=>g.Key,g=>g.Count());
        foreach(var chunk in chunks)foreach(var vertex in chunk.Vertices)expected[vertex]--;
        Check(expected.Values.All(count=>count==0),"Chunk split changed source geometry or UVs.");
        Console.WriteLine($"PASS {checks} visibility checks: clip planes, transforms, shadow influence, full run bounds and lossless city partition.");
    }
}
