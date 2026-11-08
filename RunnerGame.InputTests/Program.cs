using RunnerGame.Gameplay;
using RunnerGame.Input;

var tests = new (string, Action)[]
{
    ("cone cinematic pauses on focus loss, clears input and resets at every beat", () => {
        foreach(float t in new[]{0f,1.4f,3.4f,7.9f,8f,10.5f,12f,14.5f,16.9f}) {
            var run=new RunSimulation();var controls=new RunnerControls(run);run.PrepareConeCrashPreview();
            while(run.ConeCrash==null)controls.Step(.02f,true);
            controls.Step(t,true);float time=run.ConeCrash.Time,distance=run.Distance;
            controls.Update(new(true,Right:true,Jump:true));controls.Step(.1f,false);
            Check(run.Phase==RunPhase.Paused);Near(run.ConeCrash.Time,time);Near(run.Distance,distance);
            controls.Step(.1f,true);Check(run.Phase==RunPhase.Paused);
            controls.Update(new(true,Start:true));Check(run.Phase==RunPhase.ConeCrash);
            controls.Step(.01f,true);Near(run.PlayerX,0);Near(run.Distance,distance);
            controls.Update(new(true,Restart:true));controls.Step(.02f,true);
            Check(run.Phase==RunPhase.Ready&&run.ConeCrash==null&&run.ElapsedTime==0);
        }
    }),
    ("van crash freezes world, pauses on focus loss, resumes without movement, resets", () => {
        var run = new RunSimulation(); var controls = new RunnerControls(run);
        run.PrepareVanCrashPreview();
        for (int i=0;i<200 && run.VanCrash == null;i++) controls.Step(.02f,true);
        Check(run.Phase == RunPhase.VanCrash);
        var crash=run.VanCrash!; float distance=run.Distance; int score=run.Score;
        var traffic=run.WorldObjects.Select(o=>o.Z).ToArray();
        controls.Update(new(true, Right:true, Jump:true)); controls.Step(.5f,true);
        Near(run.Distance,distance); Check(run.Score==score && run.WorldObjects.Select(o=>o.Z).SequenceEqual(traffic));
        controls.Step(.5f,false); Near(crash.Time,.5f); Check(run.Phase==RunPhase.Paused);
        controls.Step(.5f,true); Near(crash.Time,.5f);
        controls.Update(new(true,Start:true)); controls.Step(.5f,true);
        Check(run.Phase==RunPhase.VanCrash); Near(crash.Time,1);
        controls.Step(5,true); Check(run.Phase==RunPhase.VanCrash); Near(crash.Time,6);
        controls.Step(2.2f,true); controls.Step(.3f,false); Near(crash.Time,8.2f);
        controls.Step(.5f,true); Near(crash.Time,8.2f); Check(run.Phase==RunPhase.Paused);
        controls.Update(new(true,Start:true)); controls.Step(.1f,true); Near(crash.Time,8.3f);
        controls.Step(10,true); Check(run.Phase==RunPhase.Caught); Near(crash.Time,11);
        controls.Update(new(true,Restart:true)); Check(run.Phase==RunPhase.Ready && run.VanCrash==null && run.Distance==0);
    }),
    ("restart clears crash at every action beat", () => {
        foreach(float t in new[]{0f,.5f,1.6f,2.8f,3.8f,5.5f,6.8f,7.7f,9.5f}) {
            var run=new RunSimulation(); var controls=new RunnerControls(run); run.PrepareVanCrashPreview();
            while(run.VanCrash==null) controls.Step(.02f,true);
            controls.Step(t,true); controls.Update(new(true,Restart:true)); controls.Step(.02f,true);
            Check(run.Phase==RunPhase.Ready && run.VanCrash==null && run.ElapsedTime==0);
        }
    }),
    ("focus loss freezes before simulation and clears pending input", () => {
        var (run, controls) = Running();
        controls.Update(new(true, Right: true, Jump: true, Duck: true));
        controls.Step(.1f, false);
        Check(run.Phase == RunPhase.Paused && run.Distance == 0 && run.ElapsedTime == 0);
        controls.Step(.1f, true);
        Check(run.Phase == RunPhase.Paused && run.Distance == 0);
        controls.Update(new(true, Start: true));
        controls.Step(.1f, true);
        Check(run.PlayerX == 0 && run.PlayerY == 0 && !run.IsDucking);
    }),
    ("lane input survives render frames and is consumed once", () => {
        var (run, controls) = Running();
        run.Move(-1); run.Step(.15f);
        controls.Update(new(true, Right: true));
        controls.Update(new(true)); controls.Update(new(true));
        controls.Step(.05f, true); controls.Step(.05f, true); controls.Step(.05f, true);
        Near(run.PlayerX, 0);
    }),
    ("jump starts ready without jumping", () => {
        var run = new RunSimulation(); var controls = new RunnerControls(run);
        controls.Update(new(true, Jump: true)); controls.Step(.1f, true);
        Check(run.Phase == RunPhase.Running && run.PlayerY == 0 && run.Distance > 0);
    }),
    ("pause freezes and start resumes", () => {
        var (run, controls) = Running();
        controls.Update(new(true, Pause: true, Jump: true)); controls.Step(.1f, true);
        Check(run.Phase == RunPhase.Paused && run.Distance == 0);
        controls.Update(new(true, Start: true)); controls.Step(.1f, true);
        Check(run.Phase == RunPhase.Running && run.Distance > 0 && run.PlayerY == 0);
    }),
    ("restart returns ready and clears buffered commands", () => {
        var (run, controls) = Running();
        controls.Update(new(true, Right: true, Jump: true, Duck: true));
        controls.Update(new(true, Restart: true, Start: true));
        Check(run.Phase == RunPhase.Ready);
        controls.Update(new(true, Start: true)); controls.Step(.1f, true);
        Check(run.PlayerX == 0 && run.PlayerY == 0 && !run.IsDucking);
    }),
    ("simultaneous directions are neutral", () => {
        var (run, controls) = Running();
        controls.Update(new(true, Left: true, Right: true)); controls.Step(.15f, true);
        Check(run.PlayerX == 0);
    }),
    ("jump and duck survive empty render frames", () => {
        var (run, controls) = Running();
        controls.Update(new(true, Jump: true)); controls.Update(new(true));
        controls.Step(.05f, true); Check(run.PlayerY > 0);
        controls.Update(new(true, Duck: true)); controls.Update(new(true));
        controls.Step(.05f, true); Check(run.IsDucking);
    }),
    ("update focus loss pauses and clears", () => {
        var (run, controls) = Running();
        controls.Update(new(true, Right: true)); controls.Update(new(false, Restart: true));
        Check(run.Phase == RunPhase.Paused);
        controls.Update(new(true, Start: true)); controls.Step(.15f, true);
        Check(run.PlayerX == 0);
    })
};
int failures = 0;
foreach (var (name, test) in tests)
{
    try { test(); Console.WriteLine($"PASS {name}"); }
    catch (Exception error) { failures++; Console.WriteLine($"FAIL {name}: {error.Message}"); }
}
Console.WriteLine($"{tests.Length - failures}/{tests.Length} passed");
return failures == 0 ? 0 : 1;

static (RunSimulation, RunnerControls) Running()
{
    var run = new RunSimulation(); run.Start(); return (run, new RunnerControls(run));
}
static void Check(bool condition) { if (!condition) throw new Exception("Assertion failed"); }
static void Near(float actual, float expected) => Check(Math.Abs(actual - expected) < .001f);
