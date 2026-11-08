using Engine.Geometry;
using Engine.Geometry.Loaders;
using Engine.OpenGL;
using OpenTK.Mathematics;
using RunnerGame.Animation;
using RunnerGame.Materials.RunnerLit;

namespace RunnerGame.Rendering;

public sealed record IntroDraw(Mesh Mesh,RunnerLitMaterial Material,Matrix4 Transform);

/// <summary>Scene-specific actors; shares installed model files and atlas textures.</summary>
public sealed class ConeIntroRenderer : IDisposable
{
    private readonly VertexClip clip;
    private readonly Vertex[] vertices;
    private readonly Mesh rider;
    private readonly VertexClip officerClip;
    private readonly Vertex[] officerVertices,officerOther;
    private readonly Mesh officerMesh;
    private readonly RunnerLitMaterial officerMaterial;
    private readonly RunnerLitMaterial riderMaterial;
    private readonly Dictionary<string,(Mesh Mesh,RunnerLitMaterial Material)> parts=[];
    private readonly Dictionary<string,Texture> textures=[];
    private readonly List<(string Key,Vector3 Pivot,bool Wheel)> scooter=[];
    private float lastTime=-1;
    private readonly Vector3 settledCone;
    public int MeshCount=>parts.Count+2;
    public int TextureCount=>textures.Count;
    public ConeIntroRenderer(string assets,ConeIntroScene scene)
    {
        settledCone=scene.Sample(scene.Duration).Cone;
        string root=Path.Combine(assets,"Models");
        clip=VertexClip.Open(scene.ClipPath); vertices=new Vertex[clip.VertexCount]; clip.Sample(0,vertices);
        rider=new Mesh(new MeshData(vertices,clip.Indices));
        Texture TextureAt(string path)
        {
            if(!textures.TryGetValue(path,out var texture)) {texture=Texture.FromFile(path);textures.Add(path,texture);} return texture;
        }
        riderMaterial=new(TextureAt(ModelManifest.Resolve(root,scene.RiderTexture)));
        void Load(string key,string obj,string png)
        {
            var material=new RunnerLitMaterial(TextureAt(png));
            parts.Add(key,(new Mesh(ObjLoader.Load(obj)),material));
        }
        Load("cone",scene.ConeGeometryPath ?? ModelManifest.Resolve(root,scene.ConeModel+".obj"),ModelManifest.Resolve(root,scene.ConeModel+".png"));
        string officer=ModelManifest.Resolve(root,"Charakter/Ordnungsamt/CHR_Ordnungsamt.png");
        officerClip=VertexClip.Open(scene.OfficerClipPath);
        officerVertices=new Vertex[officerClip.VertexCount];officerOther=new Vertex[officerClip.VertexCount];
        officerClip.Sample(0,officerVertices);officerMesh=new Mesh(new MeshData(officerVertices,officerClip.Indices));
        officerMaterial=new RunnerLitMaterial(TextureAt(officer));
        foreach(var part in ModelManifest.Read(ModelManifest.Resolve(root,"Fahrzeug/ScooterVoi/VEH_ScooterVoi_parts.json")))
        {string key="scooter"+part.Name;Load(key,part.ObjPath,part.TexturePath);scooter.Add((key,part.Pivot,part.Name.StartsWith("wheel")));}
    }
    public IReadOnlyList<IntroDraw> Build(ConeIntroSample sample,Matrix4 stage)
    {
        if(lastTime!=sample.Time) {clip.Sample(sample.Time,vertices);rider.UpdateVertices(vertices);lastTime=sample.Time;}
        var draws=new List<IntroDraw>();
        void Add(string key,Matrix4 transform) {var p=parts[key];draws.Add(new(p.Mesh,p.Material,transform*stage));}
        draws.Add(new(rider,riderMaterial,Matrix4.CreateRotationY(sample.RiderYaw)*Matrix4.CreateTranslation(sample.Rider)*stage));
        foreach(var part in scooter)
        {
            float wheel=(18-sample.Scooter.Z)/.127f;
            Add(part.Key,(part.Wheel?Matrix4.CreateRotationX(wheel):Matrix4.Identity)*Matrix4.CreateTranslation(part.Pivot)*Matrix4.CreateTranslation(sample.Scooter));
        }
        // Existing officer frames face +Z, while the route-local forward is -Z.
        SampleOfficer(sample.OfficerFrame,sample.OfficerOtherFrame,sample.OfficerBlend);
        draws.Add(new(officerMesh,officerMaterial,Matrix4.CreateRotationY(MathF.PI+sample.OfficerYaw)*Matrix4.CreateTranslation(sample.Officer)*stage));
        Add("cone",Matrix4.CreateRotationZ(sample.ConeRock)*Matrix4.CreateTranslation(sample.Cone));
        return draws;
    }
    public IntroDraw SettledCone(Matrix4 stage)
    {var part=parts["cone"];return new(part.Mesh,part.Material,Matrix4.CreateTranslation(settledCone)*stage);}
    private void SampleOfficer(float frame,float other,float blend)
    {
        officerClip.Sample(frame/24,officerVertices);
        if(blend>0)
        {
            officerClip.Sample(other/24,officerOther);
            for(int i=0;i<officerVertices.Length;i++)
            {
                var a=officerVertices[i];var b=officerOther[i];var normal=Vector3.Lerp(a.Normal,b.Normal,blend);
                officerVertices[i]=new(Vector3.Lerp(a.Position,b.Position,blend),normal.LengthSquared>1e-10?Vector3.Normalize(normal):Vector3.UnitY,a.TexCoord);
            }
        }
        officerMesh.UpdateVertices(officerVertices);
    }
    public IntroDraw Pursuer(float elapsed,float distance,float playerX,bool close)
    {
        SampleOfficer(35+((28+elapsed*3.37f)/1.7f%1)*40,0,0);
        return new(officerMesh,officerMaterial,PursuerVisibility.Transform(elapsed,distance,playerX,close));
    }
    public void Dispose()
    {clip.Dispose();officerClip.Dispose();rider.Dispose();officerMesh.Dispose();foreach(var p in parts.Values)p.Mesh.Dispose();foreach(var t in textures.Values)t.Dispose();parts.Clear();textures.Clear();}
}
