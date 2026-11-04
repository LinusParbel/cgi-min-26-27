using Engine;
using Engine.Geometry;
using Engine.OpenGL;
using OpenTK.Graphics.OpenGL4;
using OpenTK.Mathematics;
using RunnerGame.Animation;
using RunnerGame.Gameplay;
using RunnerGame.Materials.RunnerLit;

namespace RunnerGame.Rendering;

/// <summary>Scene-only road replacement and deforming actor, using the game's renderer.</summary>
internal sealed class VanCrashRenderer : IDisposable
{
    readonly VanCrashClip clip;
    readonly VanCrashClip duckClip;
    readonly Vertex[] vertices;
    readonly Vertex[] duckVertices;
    readonly Vertex[] rideVertices;
    readonly Mesh rider, left, right, cracks, pebble;
    readonly Texture riderTexture, asphaltTexture, darkTexture;
    readonly RunnerLitMaterial riderMaterial, asphalt, dark;
    readonly VertexClip officerClip;
    readonly Vertex[] officerVertices;
    readonly Mesh officer,ticket;
    readonly Texture officerTexture,ticketTexture;
    readonly RunnerLitMaterial officerMaterial,ticketMaterial;
    readonly VanTicketMotion ticketMotion;
    Mesh? ground, walls;
    VanCrashState? staged;
    float centre,half;
    public int MeshCount => 9;
    public int TextureCount => 5;
    public int DrawCount { get; private set; }
    public VanCrashRenderer(string assets)
    {
        string scene=Path.Combine(assets,"Animations","VanCrash");
        clip=VanCrashClip.Load(Path.Combine(scene,"rider.vcr"));
        duckClip=VanCrashClip.Load(Path.Combine(scene,"duck-start.vcr"));
        duckVertices=new Vertex[duckClip.VertexCount];duckClip.Sample(0,duckVertices);
        vertices=new Vertex[clip.VertexCount];clip.Sample(0,vertices);rider=new(new(vertices,clip.Indices));
        rideVertices=(Vertex[])vertices.Clone();
        riderTexture=Texture.FromFile(Path.Combine(assets,"Models","Charakter","ScooterRider","CHR_ScooterRider.png"));
        asphaltTexture=Texture.FromFile(Path.Combine(assets,"Models","Umgebung","StreetKit","ST_Street.png"));
        darkTexture=Texture.FromFile(Path.Combine(scene,"void.png"));
        riderMaterial=new(riderTexture);asphalt=new(asphaltTexture);dark=new(darkTexture);
        left=Flap(true);right=Flap(false);cracks=Crack();pebble=new(Primitives.CreateCube(.09f));
        officerClip=VertexClip.Open(Path.Combine(scene,"officer-ticket.vclip"));
        officerVertices=new Vertex[officerClip.VertexCount];officerClip.Sample(0,officerVertices);
        officer=new(new(officerVertices,officerClip.Indices));
        officerTexture=Texture.FromFile(Path.Combine(assets,"Models","Charakter","Ordnungsamt","CHR_Ordnungsamt.png"));
        ticketTexture=Texture.FromFile(Path.Combine(scene,"ticket.png"));
        officerMaterial=new(officerTexture);ticketMaterial=new(ticketTexture);
        ticketMotion=VanTicketMotion.Load(Path.Combine(scene,"officer-ticket-hand.json"));
        ticket=new(new MeshData(new Vertex[]{
            new(new(-.12f,-.34f,0),Vector3.UnitZ,new(0,0)),new(new(.12f,-.34f,0),Vector3.UnitZ,new(1,0)),
            new(new(.12f,0,0),Vector3.UnitZ,new(1,1)),new(new(-.12f,0,0),Vector3.UnitZ,new(0,1))
        },new uint[]{0,1,2,0,2,3}));
    }
    static float S(float x) {x=Math.Clamp(x,0,1);return x*x*(3-2*x);}
    static Mesh Geometry(Action<Action<Vector3,Vector3,Vector3,Vector3>> build)
    {
        var v=new List<Vertex>();var ix=new List<uint>();
        void Quad(Vector3 a,Vector3 b,Vector3 c,Vector3 d) {
            var normal=Vector3.Normalize(Vector3.Cross(b-a,c-a));uint n=(uint)v.Count;
            foreach(var p in new[]{a,b,c,d})v.Add(new(p,normal,new Vector2(.978f,.728f)));
            ix.AddRange(new[]{n,n+1,n+2,n,n+2,n+3});
        }
        build(Quad);return new(new(v.ToArray(),ix.ToArray()));
    }
    static Mesh Flap(bool isLeft) => new(VanCrashRoadGeometry.CreateFlap(isLeft));
    static Mesh Crack() => Geometry(q=> {
        float[] z=[-.65f,-.18f,.3f,.75f,1.2f,1.6f,2.05f];float[] x=[0,.1f,-.08f,.13f,-.1f,.06f,0];
        for(int i=0;i<z.Length-1;i++)q(new(x[i]-.018f,.008f,z[i]),new(x[i+1]-.018f,.008f,z[i+1]),new(x[i+1]+.018f,.008f,z[i+1]),new(x[i]+.018f,.008f,z[i]));
    });
    void Stage(VanCrashState state)
    {
        if(ReferenceEquals(staged,state))return;
        staged=state;ground?.Dispose();walls?.Dispose();
        // Keep the entire opening inside the road, even on an outer-lane contact.
        centre=Math.Clamp(state.PlayerX,-2.45f,2.45f);half=1.25f;
        float lo=centre-half,hi=centre+half,z0=state.OpeningFrontZ,z1=state.ReboundZ+2.05f;
        ground=Geometry(q=> {
            void Road(float x0,float x1,float a,float b)=>q(new(x0,0,a),new(x0,0,b),new(x1,0,b),new(x1,0,a));
            Road(-3.75f,lo,-150,30);Road(hi,3.75f,-150,30);
            Road(lo,hi,-150,z0);Road(lo,hi,z1,30);
        });
        walls=Geometry(q=> {
            q(new(lo,0,z0),new(lo,-9,z0),new(hi,-9,z0),new(hi,0,z0));
            q(new(hi,0,z1),new(hi,-9,z1),new(lo,-9,z1),new(lo,0,z1));
            q(new(lo,0,z1),new(lo,-9,z1),new(lo,-9,z0),new(lo,0,z0));
            q(new(hi,0,z0),new(hi,-9,z0),new(hi,-9,z1),new(hi,0,z1));
            q(new(lo,-9,z0),new(lo,-9,z1),new(hi,-9,z1),new(hi,-9,z0));
        });
    }
    void Draw(OpenGlRenderer renderer,Mesh mesh,RunnerLitMaterial material,Matrix4 transform,Camera camera)
    {renderer.Draw(mesh,material,transform,camera);DrawCount++;}
    public void SetCamera(VanCrashState state,Camera camera)
    {
        float blend=S(state.Time/.65f);
        var from=new Vector3(0,2.8f,5.5f);var to=new Vector3(state.PlayerX+3.1f,2.5f,3.7f+state.ReboundZ);
        float shake=.045f*MathF.Sin(state.Time*65)*(1-S(state.Time/.35f));
        var eye=Vector3.Lerp(from,to,blend)+new Vector3(shake,0,0);
        var target=Vector3.Lerp(new(0,1,-10),new(state.PlayerX,.7f,state.ReboundZ-.4f),blend);
        float aftermath=S((state.Time-4.45f)/.9f),close=S((state.Time-6.4f)/.7f);
        var aftermathEye=Vector3.Lerp(new(Math.Clamp(state.PlayerX+3.8f,-5.4f,5.4f),2.55f,state.ReboundZ+5.8f),new(state.PlayerX+2.7f,2.2f,state.ReboundZ+4.1f),close);
        eye=Vector3.Lerp(eye,aftermathEye,aftermath);
        target=Vector3.Lerp(target,new(state.PlayerX+.4f,.9f,state.ReboundZ+1.7f),aftermath);
        camera.LookAt(eye,target);
    }
    public void RenderGround(VanCrashState state,OpenGlRenderer renderer,Camera camera)
    {
        Stage(state);DrawCount=0;float t=state.Time;
        GL.Disable(EnableCap.CullFace);
        Draw(renderer,ground!,asphalt,Matrix4.Identity,camera);Draw(renderer,walls!,dark,Matrix4.Identity,camera);
        float angle=S((t-1.5f)/.8f)*1.5f;
        Matrix4 Flap(bool l)=>Matrix4.CreateTranslation(l?1:-1,0,0)*Matrix4.CreateScale(half,1,1)*Matrix4.CreateRotationZ(l?-angle:angle)*Matrix4.CreateTranslation(centre+(l?-half:half),0,state.ReboundZ);
        Draw(renderer,left,asphalt,Flap(true),camera);Draw(renderer,right,asphalt,Flap(false),camera);
        if(t>.45f && t<1.55f)Draw(renderer,cracks,dark,Matrix4.CreateScale(1,1,S((t-.45f)/.9f))*Matrix4.CreateTranslation(centre,0,state.ReboundZ),camera);
        if(t>1.5f && t<4.3f) {
            for(int i=0;i<5;i++) {
                float age=Math.Max(0,t-1.5f-i*.06f);
                Draw(renderer,pebble,asphalt,Matrix4.CreateRotationX(age*5+i)*Matrix4.CreateTranslation(centre+MathF.Sin(i*4)*.8f,-4*age*age,state.ReboundZ+.2f+i*.32f),camera);
            }
        }
        GL.Enable(EnableCap.CullFace);
    }
    public void RenderActors(VanCrashState state,OpenGlRenderer renderer,Camera camera,Action<string,Matrix4> drawShared)
    {
        float t=state.Time;
        var pair=VanCrashActorMotion.Sample(state);
        if(pair.Visible) {
            drawShared("scooter",pair.ScooterTransform);
            if(pair.RidePoseWeight==1)Array.Copy(rideVertices,vertices,vertices.Length);
            else {
                clip.Sample(t,vertices);
                if(pair.RidePoseWeight>0)for(int i=0;i<vertices.Length;i++) {
                    var a=vertices[i];var b=rideVertices[i];var n=Vector3.Lerp(a.Normal,b.Normal,pair.RidePoseWeight);
                    vertices[i]=new(Vector3.Lerp(a.Position,b.Position,pair.RidePoseWeight),n.LengthSquared>1e-12f?Vector3.Normalize(n):Vector3.UnitY,a.TexCoord);
                }
            }
            if(state.WasDucking && t<.7f)
            {
                float blend=S(t/.7f);
                for(int i=0;i<vertices.Length;i++)vertices[i]=new(Vector3.Lerp(duckVertices[i].Position,vertices[i].Position,blend),Vector3.Normalize(Vector3.Lerp(duckVertices[i].Normal,vertices[i].Normal,blend)),vertices[i].TexCoord);
            }
            rider.UpdateVertices(vertices);
            Draw(renderer,rider,riderMaterial,pair.RiderTransform,camera);
        }
        RenderOfficer(state,renderer,camera);
    }
    static Matrix4 OfficerTransform(VanCrashState state,float seconds)=>Matrix4.CreateRotationY(MathF.PI)*
        Matrix4.CreateTranslation(state.PlayerX+.45f,0,state.ReboundZ+13.85f-VanTicketMotion.ApproachDistance(seconds));
    void RenderOfficer(VanCrashState state,OpenGlRenderer renderer,Camera camera)
    {
        float t=state.Time;
        if(t<2.5f)return;
        officerClip.Sample(t,officerVertices);officer.UpdateVertices(officerVertices);
        var world=OfficerTransform(state,t);
        Draw(renderer,officer,officerMaterial,world,camera);
        if(t<6.4f)return;
        bool released=t>=VanTicketMotion.ReleaseTime;
        float gripTime=released?VanTicketMotion.ReleaseTime:t;
        var hand=Vector3.TransformPosition(ticketMotion.HandAt(gripTime),OfficerTransform(state,gripTime));
        float age=Math.Max(0,t-VanTicketMotion.ReleaseTime),weight=S(age/.12f);
        var position=released?VanTicketMotion.FallingTicket(t,hand):hand;
        var rotation=Matrix4.CreateRotationZ(.4f*MathF.Sin(age*8)*weight)*Matrix4.CreateRotationX(.65f*MathF.Sin(age*6)*weight)*Matrix4.CreateRotationY(.65f+age*.5f);
        GL.Disable(EnableCap.CullFace);
        Draw(renderer,ticket,ticketMaterial,rotation*Matrix4.CreateTranslation(position),camera);
        GL.Enable(EnableCap.CullFace);
    }
    public void Dispose()
    {
        rider.Dispose();left.Dispose();right.Dispose();cracks.Dispose();pebble.Dispose();ground?.Dispose();walls?.Dispose();
        riderTexture.Dispose();asphaltTexture.Dispose();darkTexture.Dispose();
        officer.Dispose();ticket.Dispose();officerClip.Dispose();officerTexture.Dispose();ticketTexture.Dispose();
    }
}
