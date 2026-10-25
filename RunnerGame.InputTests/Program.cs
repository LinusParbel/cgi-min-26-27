using RunnerGame.Gameplay;
using RunnerGame.Input;

var tests = new (string, Action)[]
{
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
