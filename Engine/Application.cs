using OpenTK.Windowing.Common;
using OpenTK.Windowing.Desktop;
using OpenTK.Windowing.GraphicsLibraryFramework;

namespace Engine;

// Base class for applications: separates the logic (FixedUpdate, Update) from drawing (Render).
// Sequence per frame: 0..n × FixedUpdate, then Update once, then Render once.
// The OpenTK callbacks are sealed so that this sequence cannot be bypassed.
public abstract class Application : GameWindow
{
    // Limits catching up after a stutter; otherwise FixedUpdate could delay the frame further and further.
    private const int MaxFixedStepsPerFrame = 5;

    private double _fixedDeltaTime = 1.0 / 50.0;
    private double _fixedTimeAccumulator;

    protected Application(GameWindowSettings gameSettings, NativeWindowSettings windowSettings)
        : base(gameSettings, windowSettings) { }

    // Time step of FixedUpdate in seconds (default: 50 steps per second).
    public double FixedDeltaTime
    {
        get => _fixedDeltaTime;
        set => _fixedDeltaTime = value > 0 ? value : throw new ArgumentOutOfRangeException(nameof(value));
    }

    // Called once after the OpenGL context has been created.
    protected virtual void Initialize() { }

    // Called after Initialize and on every framebuffer resize (never with 0).
    protected virtual void FramebufferResized(int width, int height) { }

    // Runs with a fixed time step, independent of the frame rate. For physics and simulation.
    protected virtual void FixedUpdate(float fixedDeltaTime) { }

    // Runs once per frame. deltaTime is the time since the last frame in seconds.
    protected virtual void Update(float deltaTime, KeyboardState keyboardState) { }

    // Draws the current state. Does not change any state and therefore knows no time.
    protected abstract void Render();

    // Called before closing, while the OpenGL context still exists.
    protected virtual void Shutdown() { }

    protected sealed override void OnLoad()
    {
        base.OnLoad();
        Initialize();
        if (FramebufferSize.X > 0 && FramebufferSize.Y > 0)
            FramebufferResized(FramebufferSize.X, FramebufferSize.Y);
    }

    protected sealed override void OnFramebufferResize(FramebufferResizeEventArgs e)
    {
        base.OnFramebufferResize(e);
        if (e.Width > 0 && e.Height > 0)
            FramebufferResized(e.Width, e.Height);
    }

    protected sealed override void OnUpdateFrame(FrameEventArgs e)
    {
        base.OnUpdateFrame(e);

        _fixedTimeAccumulator += e.Time;
        int steps = 0;
        while (_fixedTimeAccumulator >= _fixedDeltaTime && steps < MaxFixedStepsPerFrame)
        {
            FixedUpdate((float)_fixedDeltaTime);
            _fixedTimeAccumulator -= _fixedDeltaTime;
            steps++;
        }
        // Whatever is left after the limit is discarded: the simulation then runs slower for a moment.
        if (_fixedTimeAccumulator >= _fixedDeltaTime)
            _fixedTimeAccumulator = 0;

        Update((float)e.Time, KeyboardState);
    }

    protected sealed override void OnRenderFrame(FrameEventArgs e)
    {
        base.OnRenderFrame(e);
        // A minimized window has no framebuffer that could be drawn into.
        if (FramebufferSize.X == 0 || FramebufferSize.Y == 0) return;

        Render();
        SwapBuffers();
    }

    protected sealed override void OnUnload()
    {
        Shutdown();
        base.OnUnload();
    }
}
