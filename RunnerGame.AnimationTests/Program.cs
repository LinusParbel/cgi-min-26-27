using RunnerGame.Animation;

static void Check(bool value, string message) { if (!value) throw new Exception(message); }
static void Reject(Action action) { try { action(); } catch (ArgumentException) { return; } throw new Exception("Invalid value accepted"); }
static IntroInput Key(bool down = false, bool pause = false, bool reset = false, bool focus = true) => new(focus, down, pause, reset);
static ConeIntroController Controller() => new(new[] { new IntroCue("a", .5f, "step"), new IntroCue("b", 3, "call"), new IntroCue("c", 6.4f, "impact") });
var c = Controller();
c.Advance(2); Check(c.Phase == IntroPhase.Ready && c.Time == 0, "Ready must not advance");
c.HandleInput(Key(true)); c.Advance(1); c.HandleInput(Key(true));
Check(c.Phase == IntroPhase.Playing && c.Time == 1, "Held start must not skip");
Check(c.DrainCues().Single().Id == "a" && c.DrainCues().Count == 0, "Cue must drain once");
c.HandleInput(Key()); Check(c.HandleInput(Key(true)).Handoff, "New start press skips");
Check(c.Time == 12 && c.Phase == IntroPhase.Complete && c.DrainCues().Count == 0, "Skip without cue backlog");
Check(!c.Advance(1).Handoff && !c.HandleInput(Key(true)).Handoff, "Handoff exactly once");
c.HandleInput(Key(reset:true)); Check(c.Time == 0 && c.Phase == IntroPhase.Ready, "Reset clears state");
c.HandleInput(Key(true)); c.HandleInput(Key()); c.Advance(2);
c.HandleInput(Key(pause:true)); c.Advance(3); Check(c.Time == 2 && c.Phase == IntroPhase.Paused, "Pause freezes");
c.HandleInput(Key(true)); Check(c.Phase == IntroPhase.Playing && c.Time == 2, "Enter resumes without skip");
c.HandleInput(Key()); c.HandleInput(Key(focus:false)); c.Advance(1);
c.HandleInput(Key()); Check(c.Phase == IntroPhase.Paused && c.Time == 2, "Focus return must not resume");
c.HandleInput(Key(pause:true)); c.Advance(2);
Check(c.Phase == IntroPhase.Playing && c.Time == 4 && c.DrainCues().Count == 2, "Resume and crossed cues");
Check(c.Advance(20).Handoff && c.Time == 12, "Completion clamps and signals");
foreach (var bad in new[] { -1f, float.NaN, float.PositiveInfinity }) Reject(() => c.Advance(bad));
Reject(() => new ConeIntroController(new[] {new IntroCue("x", 2, "s"),new IntroCue("x", 3, "s")}));
Reject(() => new ConeIntroController(new[] {new IntroCue("x", float.NaN, "s")}));
Reject(() => new ConeIntroController(new[] {new IntroCue("x", 5, "s"),new IntroCue("y", 1, "s")}));
var boundaries = new[] {0f,1.5f,3f,4.25f,5f,6.5f,8f,10f};
for (int i=0;i<boundaries.Length;i++) { var b=Controller(); b.HandleInput(Key(true)); b.Advance(boundaries[i]); Check(b.ShotId == $"S{i+1:00}", "Shot boundary"); }
Console.WriteLine("PASS intro controller: start/hold/skip, cue crossing, pause/focus, reset, endpoints and validation");
VanCrashChecks.Run();
