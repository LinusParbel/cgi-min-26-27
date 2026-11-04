using RunnerGame.Animation;

static void Check(bool value, string message) { if (!value) throw new Exception(message); }
static void Reject(Action action) { try { action(); } catch (ArgumentException) { return; } throw new Exception("Invalid value accepted"); }
static IntroInput Key(bool down = false, bool pause = false, bool reset = false, bool focus = true) => new(focus, down, pause, reset);
static ConeIntroController Controller() => new(new[] { new IntroCue("a", .5f, "step"), new IntroCue("b", 3, "call"), new IntroCue("c", 6.4f, "impact") });
try
{
RunnerGame.RunnerOptions.Parse(new[]{"--van-crash-preview","--crash-contact","Side","--capture","preview.bmp","--crash-time","2.8","--mute"});
var c = Controller();
c.Advance(2); Check(c.Phase == IntroPhase.Ready && c.Time == 0, "Ready must not advance");
c.HandleInput(Key(true)); c.Advance(1); c.HandleInput(Key(true));
Check(c.Phase == IntroPhase.Playing && c.Time == 1, "Held start must not skip");
Check(c.DrainCues().Single().Id == "a" && c.DrainCues().Count == 0, "Cue must drain once");
c.HandleInput(Key()); Check(c.HandleInput(Key(true)).Handoff, "New start press skips");
Check(c.Time == 30 && c.Phase == IntroPhase.Complete && c.DrainCues().Count == 0, "Skip without cue backlog");
Check(!c.Advance(1).Handoff && !c.HandleInput(Key(true)).Handoff, "Handoff exactly once");
c.HandleInput(Key(reset:true)); Check(c.Time == 0 && c.Phase == IntroPhase.Ready, "Reset clears state");
c.HandleInput(Key(true)); c.HandleInput(Key()); c.Advance(2);
c.HandleInput(Key(pause:true)); c.Advance(3); Check(c.Time == 2 && c.Phase == IntroPhase.Paused, "Pause freezes");
c.HandleInput(Key(true)); Check(c.Phase == IntroPhase.Playing && c.Time == 2, "Enter resumes without skip");
c.HandleInput(Key()); c.HandleInput(Key(focus:false)); c.Advance(1);
c.HandleInput(Key()); Check(c.Phase == IntroPhase.Paused && c.Time == 2, "Focus return must not resume");
c.HandleInput(Key(pause:true)); c.Advance(2);
Check(c.Phase == IntroPhase.Playing && c.Time == 4 && c.DrainCues().Count == 2, "Resume and crossed cues");
Check(c.Advance(100).Handoff && c.Time == 30, "Completion clamps and signals");
foreach (var bad in new[] { -1f, float.NaN, float.PositiveInfinity }) Reject(() => c.Advance(bad));
Reject(() => new ConeIntroController(new[] {new IntroCue("x", 2, "s"),new IntroCue("x", 3, "s")}));
Reject(() => new ConeIntroController(new[] {new IntroCue("x", float.NaN, "s")}));
Reject(() => new ConeIntroController(new[] {new IntroCue("x", 5, "s"),new IntroCue("y", 1, "s")}));
var boundaries = new[] {0f,4f,7f,9f,11f,12.3f,15f,17f,20f,24f,27f};
for (int i=0;i<boundaries.Length;i++) { var b=Controller(); b.HandleInput(Key(true)); b.Advance(boundaries[i]); Check(b.ShotId == $"S{i+1:00}", "Shot boundary"); }
Console.WriteLine("PASS intro controller: start/hold/skip, cue crossing, pause/focus, reset, endpoints and validation");
ClipChecks.Run();
AudioChecks.Run();
SequenceChecks.Run();
Check(RunnerGame.RunnerOptions.Parse(new[]{"--mute","--volume","0.5"}).Volume==.5f,"Volume parse");
Reject(()=>RunnerGame.RunnerOptions.Parse(new[]{"--intro-time","3"}));
Reject(()=>RunnerGame.RunnerOptions.Parse(new[]{"--volume","NaN"}));
Reject(()=>RunnerGame.RunnerOptions.Parse(new[]{"--capture","x.bmp","--intro-time","3","--advance","2"}));
Reject(()=>RunnerGame.RunnerOptions.Parse(new[]{"--map","x","--record-intro","y"}));
var introAssets=Path.GetFullPath("RunnerGame/Assets/Animations/ConeHat");
var authoredScene=ConeIntroScene.Load(introAssets);
Check(authoredScene.Sample(30).Rider.Length<.001f && authoredScene.Sample(30).Scooter.Length<.001f,"Scene endpoint aligned");
Check(authoredScene.Cues.Count>=6 && authoredScene.Sample(17).Cone.Y==0,"Scene impact and cues");
// AC06 requires distance during the call and at handoff; the late chase may close the gap.
foreach(float t in new[]{0f,9f,11f,12.3f,15f,17f,20f,22f,24f,30f})
{var s=authoredScene.Sample(t);Check((s.Rider-s.Officer).Length>=12,$"Officer must remain distant at {t}: {(s.Rider-s.Officer).Length:F3} m");}
Check(authoredScene.Sample(12).Officer==authoredScene.Sample(17).Officer,"Officer should hold still through the awkward pause");
Check(authoredScene.Sample(19).Officer.Z<authoredScene.Sample(17).Officer.Z-.8f,"Officer must walk forward before running");
Check(authoredScene.Sample(20.2f).Officer.Z<authoredScene.Sample(19.4f).Officer.Z,"Officer must continue into a run");
using(var officerClip=VertexClip.Open(authoredScene.OfficerClipPath))
{
    var verts=new Engine.Geometry.Vertex[officerClip.VertexCount];
    for(int frame=2;frame<=34;frame++)
    {officerClip.Sample(frame/24f,verts);Check(verts.Min(v=>v.Position.Y)>=-.005f,"Officer walking sole penetrates ground");}
    Console.WriteLine("PASS officer walk floor clearance across all 33 loop samples");
}
var coneGeometry=Engine.Geometry.Loaders.ObjLoader.Load("RunnerGame/Assets/Models/"+authoredScene.ConeModel+".obj");
for(float t=17f;t<20;t+=.025f)
{
    var sample=authoredScene.Sample(t);
    var rotation=OpenTK.Mathematics.Matrix4.CreateRotationZ(sample.ConeRock);
    Check(coneGeometry.Vertices.Min(v=>OpenTK.Mathematics.Vector3.TransformPosition(v.Position,rotation).Y)+sample.Cone.Y>=-.001f,"Rocking cone must not sink through ground");
}
using(var realClip=VertexClip.Open(Path.Combine(introAssets,"rider.vclip")))
{
    var v=new Engine.Geometry.Vertex[realClip.VertexCount];
    var timer=System.Diagnostics.Stopwatch.StartNew();
    Check(realClip.Duration==30,"Real clip duration");
    foreach(float t in new[]{8f,10f,14f})
    {
        realClip.Sample(t,v);var top=v.Max(x=>x.Position.Y);var head=v.Where(x=>x.Position.Y>top-.12f).ToArray();
        var center=new OpenTK.Mathematics.Vector3((head.Min(x=>x.Position.X)+head.Max(x=>x.Position.X))/2,top-.05f,(head.Min(x=>x.Position.Z)+head.Max(x=>x.Position.Z))/2);
        var scene=authoredScene.Sample(t);var transform=OpenTK.Mathematics.Matrix4.CreateRotationY(scene.RiderYaw)*OpenTK.Mathematics.Matrix4.CreateTranslation(scene.Rider);
        var world=OpenTK.Mathematics.Vector3.TransformPosition(center,transform);
        Check((world-scene.Cone).Length<.035f,"Cone hat must fit the evaluated head rather than float forward");
    }
    for(int frame=0;frame<=672;frame++)
    {realClip.Sample(frame/24f,v);Check(realClip.CachedFrames<=2,"Real clip cache bound");Check(v.All(x=>float.IsFinite(x.Position.X+x.Position.Y+x.Position.Z)),"Real clip finite");}
    Console.WriteLine($"Real clip: 721 samples in {timer.Elapsed.TotalSeconds:0.00}s; decoded frame cache <=2, {realClip.VertexCount} vertices");
}
Console.WriteLine("PASS real cone scene tracks, handoff endpoint and exported clip readback");
VanCrashChecks.Run();
}
catch(Exception error) { Console.Error.WriteLine(error); Environment.ExitCode=1; }
