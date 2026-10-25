using Engine;
using OpenTK.Graphics.OpenGL4;
using OpenTK.Mathematics;
using OpenTK.Windowing.Common;
using OpenTK.Windowing.Desktop;
using OpenTK.Windowing.GraphicsLibraryFramework;
using RunnerGame.Gameplay;
using RunnerGame.Input;
using RunnerGame.Rendering;

namespace RunnerGame;

internal static class Program
{
    private static int Main(string[] args)
    {
        string? capture = null;
        string? mapFolder = null;
        bool overview = false;
        float? inspectionDistance = null;
        bool duckCapture = false;
        float advance = 0;
        for (int i = 0; i < args.Length; i++)
        {
            if (args[i] == "--capture" && i + 1 < args.Length) capture = Path.GetFullPath(args[++i]);
            else if (args[i] == "--map" && i + 1 < args.Length) mapFolder = Path.GetFullPath(args[++i]);
            else if (args[i] == "--overview") overview = true;
            else if (args[i] == "--inspect" && i + 1 < args.Length &&
                float.TryParse(args[++i], System.Globalization.NumberStyles.Float,
                    System.Globalization.CultureInfo.InvariantCulture, out float position) &&
                float.IsFinite(position) && position >= 0) inspectionDistance = position;
            else if (args[i] == "--duck") duckCapture = true;
            else if (args[i] == "--advance" && i + 1 < args.Length &&
                float.TryParse(args[++i], System.Globalization.NumberStyles.Float,
                    System.Globalization.CultureInfo.InvariantCulture, out float seconds) &&
                float.IsFinite(seconds) && seconds >= 0 && seconds <= 60) advance = seconds;
            else { Console.Error.WriteLine("Usage: RunnerGame [--map folder] [--overview] [--inspect metres] [--capture output.bmp] [--duck] [--advance seconds (0..60)]"); return 2; }
        }
        if (capture == null && (duckCapture || advance > 0))
        { Console.Error.WriteLine("--duck and --advance require --capture."); return 2; }
        if ((overview || inspectionDistance.HasValue) && mapFolder == null)
        { Console.Error.WriteLine("--overview and --inspect require --map."); return 2; }
        using var window = new RunnerGameWindow(capture, duckCapture, advance, mapFolder, overview, inspectionDistance, GameWindowSettings.Default,
            new NativeWindowSettings
            {
                ClientSize = new Vector2i(1280, 800), StartVisible = true, StartFocused = true,
                Title = "Hannover Rush Hour - loading street...",
                APIVersion = new Version(3, 3), Profile = ContextProfile.Core
            });
        window.Run();
        return 0;
    }
}

internal sealed class RunnerGameWindow(string? capturePath, bool duckCapture, float advanceSeconds,
    string? mapFolder, bool overview, float? inspectionDistance,
    GameWindowSettings settings, NativeWindowSettings native) : Application(settings, native)
{
    private readonly RunSimulation _run = new(pedestrian: mapFolder != null);
    private RunnerControls _controls = null!;
    private IRunnerScene? _scene;
    private bool _mapComplete;
    private int _frames;
    private float _titleTimer;
    private float _fps = 60;
    private Vector2 _lastInspectMouse;
    private bool _inspectLooking;

    protected override void Initialize()
    {
        VSync = VSyncMode.On;
        _controls = new RunnerControls(_run);
        string assets = Path.Combine(AppContext.BaseDirectory, "Assets");
        _scene = mapFolder == null ? new SceneRenderer(assets)
            : new PedestrianMapRenderer(assets, mapFolder) { Overview = overview, InspectionDistance = inspectionDistance };
        if (capturePath != null && (duckCapture || advanceSeconds > 0))
        {
            _controls.Update(new InputFrame(true, Start: true));
            for (int tick = 0; tick < (int)MathF.Round(advanceSeconds / .02f); tick++) _controls.Step(.02f, true);
            if (duckCapture)
            {
                _controls.Update(new InputFrame(true, Duck: true)); _controls.Step(.02f, true);
            }
            if (_run.Phase == RunPhase.Running) _run.TogglePause();
        }
        UpdateTitle();
        IsVisible = true;
        Focus();
        Console.WriteLine($"Game visible={IsVisible}, focused={IsFocused}, state={_run.Phase}; A/D lanes, Space jump, S duck, Esc pause, R restart.");
    }

    protected override void FramebufferResized(int width, int height) => _scene?.Resize(width, height);

    protected override void FixedUpdate(float dt)
    {
        if (capturePath != null) return;
        _controls.Step(dt, IsFocused);
        if (_scene is PedestrianMapRenderer map && _run.Phase == RunPhase.Running && _run.Distance >= map.RouteLength - 2)
        {
            _run.TogglePause(); _mapComplete = true; UpdateTitle();
        }
    }

    protected override void Update(float dt)
    {
        if (capturePath != null) return;
        var keys = KeyboardState;
        if (!IsFocused) _inspectLooking = false;
        bool restart = keys.IsKeyPressed(Keys.R);
        bool start = keys.IsKeyPressed(Keys.Enter);
        bool jump = keys.IsKeyPressed(Keys.Space) || keys.IsKeyPressed(Keys.W) || keys.IsKeyPressed(Keys.Up);
        if (IsFocused && _scene is PedestrianMapRenderer map)
        {
            var mouse = MouseState.Position;
            bool looking = MouseState.IsButtonDown(MouseButton.Right);
            if (_run.Phase != RunPhase.Running && map.InspectionDistance.HasValue && !map.Overview)
            {
                if (looking && _inspectLooking)
                {
                    var delta = mouse - _lastInspectMouse;
                    map.InspectionYawDegrees += delta.X * .35f;
                    map.InspectionPitchDegrees -= delta.Y * .2f;
                }
                map.InspectionZoom -= MouseState.ScrollDelta.Y * 1.5f;
            }
            _inspectLooking = looking; _lastInspectMouse = mouse;
            if (restart) { _mapComplete = false; map.InspectionDistance = null; }
            if (keys.IsKeyPressed(Keys.Tab))
            {
                if (_run.Phase == RunPhase.Running) _run.TogglePause();
                map.Overview = !map.Overview; UpdateTitle(); return;
            }
            if (_mapComplete && !restart) return;
            if (_run.Phase != RunPhase.Running && (keys.IsKeyPressed(Keys.PageDown) || keys.IsKeyPressed(Keys.PageUp)))
            {
                float shift = keys.IsKeyPressed(Keys.PageDown) ? 100 : -100;
                map.InspectionDistance = (map.InspectionDistance ?? _run.Distance) + shift;
                map.Overview = false; UpdateTitle(); return;
            }
            if ((_run.Phase == RunPhase.Ready && (start || jump)) || (_run.Phase == RunPhase.Paused && start))
            { map.Overview = false; map.InspectionDistance = null; }
        }
        _controls.Update(new InputFrame(IsFocused,
            Left: keys.IsKeyPressed(Keys.A) || keys.IsKeyPressed(Keys.Left),
            Right: keys.IsKeyPressed(Keys.D) || keys.IsKeyPressed(Keys.Right),
            Jump: jump,
            Duck: keys.IsKeyPressed(Keys.S) || keys.IsKeyPressed(Keys.Down),
            Start: start, Pause: keys.IsKeyPressed(Keys.Escape), Restart: restart));
        if (dt > 0 && dt < .5f) _fps += (1 / dt - _fps) * .05f;
        _titleTimer += dt;
        if (_titleTimer >= .15f) { _titleTimer = 0; UpdateTitle(); }
    }

    private void UpdateTitle()
    {
        string status = _run.Phase switch
        {
            RunPhase.Ready => "READY - Enter / Space to start",
            RunPhase.Paused => "PAUSED - Enter / Esc to resume",
            RunPhase.Caught => "CAUGHT! R to restart",
            _ => _run.PursuitRemaining > 0 ? "PURSUIT - avoid another hit!" : "RUNNING"
        };
        if (_mapComplete) status = "STEINTOR - preview complete; R restart";
        else if (_scene is PedestrianMapRenderer map)
            status = (map.Overview ? "MAP OVERVIEW - Enter to ride; Tab view" :
                map.InspectionDistance.HasValue ? $"INSPECT {map.InspectionDistance:0}m - PgUp/PgDn; Enter ride" : status + " - Tab map") + " [WORK IN PROGRESS]";
        Title = $"Hannover Rush Hour | {status} | {_run.Score} pts | {_run.Distance:0} m | {_run.CoinCount} coins | {_run.EffectiveSpeed:0} m/s | {_fps:0} FPS";
    }

    protected override void Render()
    {
        _scene!.Render(_run);
        if (capturePath == null || ++_frames < 5) return;
        CaptureBitmap(capturePath);
        Console.WriteLine($"Captured {capturePath}; {_scene.MeshCount} meshes, {_scene.TextureCount} textures, {_scene.DrawCount} draws");
        Close();
    }

    private void CaptureBitmap(string path)
    {
        // Bottom-up BGRA matches OpenGL readback; no image-writing dependency needed.
        int width = FramebufferSize.X, height = FramebufferSize.Y;
        var pixels = new byte[checked(width * height * 4)];
        GL.ReadPixels(0, 0, width, height, PixelFormat.Bgra, PixelType.UnsignedByte, pixels);
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        using var writer = new BinaryWriter(File.Create(path));
        writer.Write((ushort)0x4D42); writer.Write(54 + pixels.Length); writer.Write(0); writer.Write(54);
        writer.Write(40); writer.Write(width); writer.Write(height); writer.Write((ushort)1); writer.Write((ushort)32);
        writer.Write(0); writer.Write(pixels.Length); writer.Write(2835); writer.Write(2835); writer.Write(0); writer.Write(0);
        writer.Write(pixels);
    }

    protected override void Shutdown() => _scene?.Dispose();
}
