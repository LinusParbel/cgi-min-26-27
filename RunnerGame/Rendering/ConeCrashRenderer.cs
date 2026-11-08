using Engine;
using Engine.Geometry;
using Engine.OpenGL;
using OpenTK.Mathematics;
using RunnerGame.Animation;
using RunnerGame.Gameplay;
using RunnerGame.Materials.RunnerLit;

namespace RunnerGame.Rendering;

/// <summary>Deforming actors and ticket contact, submitted to the normal shadowed render pass.</summary>
internal sealed class ConeCrashRenderer : IDisposable
{
    readonly VertexClip riderClip,officerClip,runClip;
    readonly VanCrashClip duckClip;
    readonly Vertex[] riderVertices,officerVertices,duckVertices,runVertices,standingVertices;
    readonly Mesh rider,officer,ticket,star,cloud;
    readonly Texture riderTexture,officerTexture,ticketTexture,whiteTexture;
    readonly RunnerLitMaterial riderMaterial,officerMaterial,ticketMaterial,white;
    readonly ConeCrashMotion motion;
    public int MeshCount=>5;
    public int TextureCount=>4;
    public ConeCrashRenderer(string assets)
    {
        string scene=Path.Combine(assets,"Animations","ConeCrash");motion=new(scene);
        riderClip=VertexClip.Open(Path.Combine(scene,"rider.vclip"));officerClip=VertexClip.Open(Path.Combine(scene,"officer.vclip"));
        runClip=VertexClip.Open(Path.Combine(assets,"Animations","ConeHat","officer_motion.vclip"));
        if(runClip.VertexCount!=officerClip.VertexCount || !runClip.Indices.SequenceEqual(officerClip.Indices))throw new InvalidDataException("Officer clip topology differs from shared run.");
        runVertices=new Vertex[runClip.VertexCount];standingVertices=new Vertex[runClip.VertexCount];runClip.Sample(0,standingVertices);
        duckClip=VanCrashClip.Load(Path.Combine(assets,"Animations","VanCrash","duck-start.vcr"));
        riderVertices=new Vertex[riderClip.VertexCount];officerVertices=new Vertex[officerClip.VertexCount];duckVertices=new Vertex[duckClip.VertexCount];
        riderClip.Sample(0,riderVertices);officerClip.Sample(0,officerVertices);duckClip.Sample(0,duckVertices);
        rider=new(new(riderVertices,riderClip.Indices));officer=new(new(officerVertices,officerClip.Indices));
        riderTexture=Texture.FromFile(Path.Combine(assets,"Models","Charakter","ScooterRider","CHR_ScooterRider.png"));
        officerTexture=Texture.FromFile(Path.Combine(assets,"Models","Charakter","Ordnungsamt","CHR_Ordnungsamt.png"));
        ticketTexture=Texture.FromFile(Path.Combine(scene,"ticket.png"));whiteTexture=Texture.FromFile(Path.Combine(scene,"white.png"));
        riderMaterial=new(riderTexture);officerMaterial=new(officerTexture);ticketMaterial=new(ticketTexture);white=new(whiteTexture);
        ticket=new(new MeshData(new Vertex[]{
            new(new(-.12f,-.16f,0),Vector3.UnitZ,new(0,0)),new(new(.12f,-.16f,0),Vector3.UnitZ,new(1,0)),
            new(new(.12f,.16f,0),Vector3.UnitZ,new(1,1)),new(new(-.12f,.16f,0),Vector3.UnitZ,new(0,1)),
            new(new(-.12f,-.16f,-.002f),-Vector3.UnitZ,new(0,0)),new(new(.12f,-.16f,-.002f),-Vector3.UnitZ,new(1,0)),
            new(new(.12f,.16f,-.002f),-Vector3.UnitZ,new(1,1)),new(new(-.12f,.16f,-.002f),-Vector3.UnitZ,new(0,1))
        },new uint[]{0,1,2,0,2,3,4,6,5,4,7,6}));
        var vertices=new List<Vertex>();var indices=new List<uint>();
        for(int i=0;i<8;i++) {
            float a=i*MathF.PI/4,b=(i+1)*MathF.PI/4;float r=i%2==0?1:.16f,r2=(i+1)%2==0?1:.16f;
            uint n=(uint)vertices.Count;vertices.Add(new(Vector3.Zero,Vector3.UnitZ,Vector2.Zero));
            vertices.Add(new(new(MathF.Cos(a)*r,MathF.Sin(a)*r,0),Vector3.UnitZ,Vector2.Zero));
            vertices.Add(new(new(MathF.Cos(b)*r2,MathF.Sin(b)*r2,0),Vector3.UnitZ,Vector2.Zero));indices.AddRange(new[]{n,n+1,n+2});
        }
        star=new(new(vertices.ToArray(),indices.ToArray()));
        vertices.Clear();indices.Clear();
        // Rounded code-native cloud lobes, deliberately stylized rather than a new prop asset.
        for(int row=0;row<=12;row++)for(int col=0;col<=24;col++) {
            float latitude=row*MathF.PI/12,longitude=col*MathF.PI*2/24;
            var normal=new Vector3(MathF.Sin(latitude)*MathF.Cos(longitude),MathF.Cos(latitude),MathF.Sin(latitude)*MathF.Sin(longitude));
            vertices.Add(new(normal,normal,Vector2.Zero));
        }
        for(int row=0;row<12;row++)for(int col=0;col<24;col++) {
            uint a=(uint)(row*25+col),b=a+25;indices.AddRange(new[]{a,a+1,b,a+1,b+1,b});
        }
        cloud=new(new(vertices.ToArray(),indices.ToArray()));
    }
    public void SetCamera(ConeCrashState state,Camera camera)
    {var s=motion.Sample(state);camera.LookAt(s.Eye,s.Target);}
    public IReadOnlyList<IntroDraw> Build(ConeCrashState state,Action<string,Matrix4> shared)
    {
        float t=state.Time;var s=motion.Sample(state);var draws=new List<IntroDraw>();
        shared("scooter",s.Scooter);
        {
            foreach(var p in new[]{new Vector3(-13,28,-28),new Vector3(12,43,-38),new Vector3(-16,49,-60)})
                for(int lobe=-1;lobe<=1;lobe++)draws.Add(new(cloud,white,Matrix4.CreateScale(3.4f,lobe==0?1.8f:1.1f,1.4f)*
                    Matrix4.CreateTranslation(p+new Vector3(state.PlayerX+lobe*2.6f,0,0))));
        }
        if(s.RiderVisible) {
            riderClip.Sample(t,riderVertices);
            if(state.WasDucking && t<.7f && duckVertices.Length==riderVertices.Length) {
                float w=ConeCrashMotion.Smooth(t/.7f);
                for(int i=0;i<riderVertices.Length;i++)riderVertices[i]=new(Vector3.Lerp(duckVertices[i].Position,riderVertices[i].Position,w),
                    Vector3.Normalize(Vector3.Lerp(duckVertices[i].Normal,riderVertices[i].Normal,w)),riderVertices[i].TexCoord);
            }
            rider.UpdateVertices(riderVertices);draws.Add(new(rider,riderMaterial,s.Rider));
        }
        if(t<12.2f) {
            officerClip.Sample(t,officerVertices);
            if(t<ConeCrashMotion.Jump) {
                runClip.Sample(ConeCrashMotion.RunFrame(t)/24,runVertices);
                float runWeight=ConeCrashMotion.Smooth(ConeCrashMotion.RunSpeed(t)/5.5f);
                float crouch=ConeCrashMotion.Smooth((t-3.65f)/.45f);
                for(int i=0;i<officerVertices.Length;i++) {
                    var run=runVertices[i];var stand=standingVertices[i];var pose=officerVertices[i];
                    var position=Vector3.Lerp(stand.Position,run.Position,runWeight);
                    var normal=Vector3.Lerp(stand.Normal,run.Normal,runWeight);
                    position=Vector3.Lerp(position,pose.Position,crouch);normal=Vector3.Lerp(normal,pose.Normal,crouch);
                    officerVertices[i]=new(position,Vector3.Normalize(normal),pose.TexCoord);
                }
            }
            officer.UpdateVertices(officerVertices);draws.Add(new(officer,officerMaterial,s.Officer));
        }
        if(s.TicketVisible)draws.Add(new(ticket,ticketMaterial,s.Ticket));
        if(t>=ConeCrashMotion.Vanish && t<16.8f) {
            float scale=.07f*MathF.Sin((t-ConeCrashMotion.Vanish)/.6f*MathF.PI);
            // Same screen position as departure, placed before the cloud layer for a readable twinkle.
            var point=s.Eye+(ConeCrashMotion.DeparturePoint(state)-s.Eye)*.12f;
            draws.Add(new(star,white,Matrix4.CreateScale(scale)*Matrix4.CreateTranslation(point)));
        }
        return draws;
    }
    public void Dispose()
    {
        riderClip.Dispose();officerClip.Dispose();runClip.Dispose();rider.Dispose();officer.Dispose();ticket.Dispose();star.Dispose();cloud.Dispose();
        riderTexture.Dispose();officerTexture.Dispose();ticketTexture.Dispose();whiteTexture.Dispose();
    }
}
