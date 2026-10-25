using RunnerGame.Gameplay;

namespace RunnerGame.Input;

public readonly record struct InputFrame(bool Focused, bool Left = false, bool Right = false,
    bool Jump = false, bool Duck = false, bool Start = false, bool Pause = false, bool Restart = false);

public sealed class RunnerControls(RunSimulation run)
{
    int pendingDirection;
    bool pendingJump, pendingDuck;

    public void Update(InputFrame frame)
    {
        if (!frame.Focused) { LoseFocus(); return; }
        if (frame.Restart) { run.Restart(); Clear(); return; }
        if (frame.Pause) { run.TogglePause(); Clear(); return; }
        if (run.Phase == RunPhase.Ready)
        {
            Clear();
            if (frame.Start || frame.Jump) run.Start();
            return;
        }
        if (run.Phase == RunPhase.Paused)
        {
            Clear();
            if (frame.Start) run.TogglePause();
            return;
        }
        if (run.Phase != RunPhase.Running) { Clear(); return; }
        if (frame.Left != frame.Right) pendingDirection = frame.Left ? -1 : 1;
        pendingJump |= frame.Jump;
        pendingDuck |= frame.Duck;
    }

    public void Step(float dt, bool focused)
    {
        // Fixed updates precede render input polling, so focus must be checked here too.
        if (!focused) { LoseFocus(); return; }
        if (run.Phase == RunPhase.Running)
        {
            run.Move(pendingDirection);
            if (pendingJump) run.Jump();
            if (pendingDuck) run.Duck();
        }
        Clear();
        run.Step(dt);
    }

    void LoseFocus()
    {
        if (run.Phase == RunPhase.Running) run.TogglePause();
        Clear();
    }

    void Clear()
    {
        pendingDirection = 0;
        pendingJump = pendingDuck = false;
    }
}
