using Engine;
using OpenTK.Graphics.OpenGL4;
using OpenTK.Mathematics;
using OpenTK.Windowing.Common;
using OpenTK.Windowing.Desktop;
using OpenTK.Windowing.GraphicsLibraryFramework;
using RunnerGame.Gameplay;
using RunnerGame.Input;
using RunnerGame.Rendering;
using RunnerGame.Animation;
using RunnerGame.Audio;

namespace RunnerGame;

internal static class Program
{
    private static int Main(string[] args)
    {
        RunnerOptions options;
        try { options = RunnerOptions.Parse(args); }
        catch (ArgumentException error) { Console.Error.WriteLine(error.Message); return 2; }
        string? capture = options.Capture, mapFolder = options.MapFolder;
        bool overview = options.Overview, duckCapture = options.Duck;
        float? inspectionDistance = options.Inspect;
        float advance = options.Advance;
        using var window = new RunnerGameWindow(capture, duckCapture, advance, mapFolder, overview, inspectionDistance, options, GameWindowSettings.Default,
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
    RunnerOptions options,
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
    private ConeIntroScene? _introScene;
    private OpeningSequence? _opening;
    private int _recordFrame;
    private VanCrashAudio? _crashAudio;
    private VanCrashAudio? _coneAudio;
    private int _filmFrame;

    protected override void Initialize()
    {
        VSync = VSyncMode.On;
        _controls = new RunnerControls(_run);
        string assets = Path.Combine(AppContext.BaseDirectory, "Assets");
        _scene = mapFolder == null ? new SceneRenderer(assets)
            : new PedestrianMapRenderer(assets, mapFolder) { Overview = overview, InspectionDistance = inspectionDistance };
        if (mapFolder == null && !options.VanCrashPreview && !options.ConeCrashPreview)
        {
        _introScene = ConeIntroScene.Load(Path.Combine(assets, "Animations/ConeHat"));
        if (capturePath == null || options.IntroTime.HasValue) _scene.PrepareIntro(_introScene);
        var audio = new IntroAudio(_introScene.Folder);
        audio.SetVolume(options.Mute || options.RecordIntro != null ? 0 : options.Volume);
        _opening = new OpeningSequence(_introScene.Cues, _run, audio);
        }
        if(mapFolder==null)
            _crashAudio=new VanCrashAudio(Path.Combine(assets,"Animations","VanCrash","crash.wav"),options.Mute || capturePath!=null || options.CrashFilm!=null,options.Volume);
        if(mapFolder==null)
            _coneAudio=new VanCrashAudio(Path.Combine(assets,"Animations","ConeCrash","crash.wav"),options.Mute || capturePath!=null || options.CrashFilm!=null,options.Volume,ConeCrashState.Duration);
        if(options.ConeCrashPreview)
        {
            _run.PrepareConeCrashPreview(options.CrashContact,options.CrashDistance);
            if(capturePath!=null || options.CrashFilm!=null)
            {
                for(int i=0;i<300 && _run.ConeCrash==null;i++)_run.Step(.02f);
                if(_run.ConeCrash==null)throw new InvalidOperationException("Preview failed to collide with cone");
                if(options.CrashTime>0)_run.Step(options.CrashTime);
            }
        }
        if(options.VanCrashPreview)
        {
            _run.PrepareVanCrashPreview(options.CrashContact,options.CrashDistance);
            if(capturePath!=null || options.CrashFilm!=null)
            {
                for(int i=0;i<300 && _run.VanCrash==null;i++)_run.Step(.02f);
                if(_run.VanCrash==null)throw new InvalidOperationException("Preview failed to collide with van");
                if(options.CrashTime>0)_run.Step(options.CrashTime);
            }
        }
        if (options.RecordIntro != null)
        {
            if (Directory.Exists(options.RecordIntro) && Directory.EnumerateFileSystemEntries(options.RecordIntro).Any())
                throw new IOException("Recording directory must be empty to avoid replacing existing evidence.");
            Directory.CreateDirectory(options.RecordIntro);
            _opening!.HandleInput(new(true, true, false, false));
            _opening.HandleInput(new(true, false, false, false));
        }
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
        if (capturePath != null || options.RecordIntro != null || options.CrashFilm != null) return;
        if (_opening != null && _opening.Controller.Phase != IntroPhase.Complete)
        { _opening.Advance(dt, IsFocused); return; }
        _opening?.Advance(0, IsFocused);
        // Live crash playback uses real frame time below, matching native audio
        // even when the engine discards fixed-step catch-up time after a stall.
        _controls.Step(_run.Phase is RunPhase.VanCrash or RunPhase.ConeCrash ? 0 : dt, IsFocused);
        _crashAudio?.Update(_run);
        _coneAudio?.UpdateCone(_run);
        if (_scene is PedestrianMapRenderer map && _run.Phase == RunPhase.Running && _run.Distance >= map.RouteLength - 2)
        {
            _run.TogglePause(); _mapComplete = true; UpdateTitle();
        }
    }

    protected override void Update(float dt)
    {
        if (capturePath != null || options.RecordIntro != null || options.CrashFilm != null) return;
        var keys = KeyboardState;
        if (!IsFocused) _inspectLooking = false;
        bool restart = keys.IsKeyPressed(Keys.R);
        bool start = keys.IsKeyPressed(Keys.Enter);
        bool jump = keys.IsKeyPressed(Keys.Space) || keys.IsKeyPressed(Keys.W) || keys.IsKeyPressed(Keys.Up);
        bool introOwnedInput = _opening != null && _opening.Controller.Phase != IntroPhase.Complete;
        _opening?.HandleInput(new IntroInput(IsFocused,
            keys.IsKeyDown(Keys.Enter) || keys.IsKeyDown(Keys.Space),
            keys.IsKeyPressed(Keys.Escape), restart));
        if (introOwnedInput || restart)
        {
            if (restart)
            {
                _mapComplete = false; _controls.Update(new InputFrame(true, Restart: true));
                _crashAudio?.Update(_run);
                _coneAudio?.UpdateCone(_run);
                if (_scene is PedestrianMapRenderer resetMap) resetMap.InspectionDistance = null;
            }
            if (_scene is PedestrianMapRenderer introMap && _opening != null && _opening.Controller.Phase != IntroPhase.Ready)
            { introMap.Overview = false; introMap.InspectionDistance = null; }
            // Ready still permits map inspection; playing/paused owns all input.
            if ((_opening != null && _opening.Controller.Phase != IntroPhase.Ready) || restart)
            { UpdateTitle(); return; }
        }
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
        if (_opening != null && _opening.Controller.Phase != IntroPhase.Complete) return;
        _controls.Update(new InputFrame(IsFocused,
            Left: keys.IsKeyPressed(Keys.A) || keys.IsKeyPressed(Keys.Left),
            Right: keys.IsKeyPressed(Keys.D) || keys.IsKeyPressed(Keys.Right),
            Jump: jump,
            Duck: keys.IsKeyPressed(Keys.S) || keys.IsKeyPressed(Keys.Down),
            Start: start, Pause: keys.IsKeyPressed(Keys.Escape), Restart: restart));
        if((_run.Phase is RunPhase.VanCrash or RunPhase.ConeCrash) && IsFocused)_run.Step(dt);
        _opening?.Advance(0,IsFocused);
        _crashAudio?.Update(_run);
        _coneAudio?.UpdateCone(_run);
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
            RunPhase.Caught => _run.ConeCrash!=null ? "SPECIAL DELIVERY! R to restart" : _run.VanCrash!=null ? "THE STREET GAVE UP! R to restart" : "CAUGHT! R to restart",
            RunPhase.ConeCrash => "SPECIAL DELIVERY... Esc pause / R restart",
            RunPhase.VanCrash => "THE STREET IS GIVING UP... Esc pause / R restart",
            _ => _run.PursuitRemaining > 0 ? "PURSUIT - avoid another hit!" : "RUNNING"
        };
        if (_mapComplete) status = "STEINTOR - preview complete; R restart";
        else if (_scene is PedestrianMapRenderer map)
            status = (map.Overview ? "MAP OVERVIEW - Enter to ride; Tab view" :
                map.InspectionDistance.HasValue ? $"INSPECT {map.InspectionDistance:0}m - PgUp/PgDn; Enter ride" : status + " - Tab map") + " [WORK IN PROGRESS]";
        if (_opening != null && _opening.Controller.Phase is IntroPhase.Playing or IntroPhase.Paused)
            status = $"CONE HAT {_opening.Controller.ShotId} {_opening.Controller.Time:0.0}/{ConeIntroController.Duration:0}s - " +
                (_opening.Controller.Phase == IntroPhase.Paused ? "PAUSED: Enter/Esc resume" : "Enter/Space skip; Esc pause");
        Title = $"Hannover Rush Hour | {status} | {_run.Score} pts | {_run.Distance:0} m | {_run.CoinCount} coins | {_run.EffectiveSpeed:0} m/s | {_fps:0} FPS";
    }

    protected override void Render()
    {
        IntroRenderState? intro = null;
        if (options.IntroTime.HasValue && _introScene != null) intro = new(_introScene, options.IntroTime.Value);
        else if (options.RecordIntro != null && _opening != null && _opening.Controller.Phase != IntroPhase.Complete) intro = new(_introScene!, Math.Min(ConeIntroController.Duration, _recordFrame / 24f));
        else if (_opening != null && _opening.Controller.Phase is IntroPhase.Playing or IntroPhase.Paused) intro = new(_introScene!, _opening.Controller.Time);
        _scene!.Render(_run, intro);
        if(options.CrashFilm!=null)
        {
            CaptureBitmap(Path.Combine(options.CrashFilm,$"frame-{_filmFrame:0000}.bmp"));
            if(++_filmFrame>=(int)((options.ConeCrashPreview?ConeCrashState.Duration:VanCrashState.Duration)*30)+1){Console.WriteLine($"Captured {_filmFrame} crash frames at 30fps to {options.CrashFilm}");Close();}
            else _run.Step(1f/30);
            return;
        }
        if (options.RecordIntro != null)
        {
            CaptureBitmap(Path.Combine(options.RecordIntro, $"frame{_recordFrame:0000}.bmp"));
            int totalFrames = (int)((ConeIntroController.Duration + 1) * 24);
            if (_recordFrame++ >= totalFrames - 1)
            {
                IntroAudioMix.Write(_introScene!.Folder, _introScene.Cues, Path.Combine(options.RecordIntro, "audio.wav"));
                File.WriteAllText(Path.Combine(options.RecordIntro, "cues.json"), System.Text.Json.JsonSerializer.Serialize(_introScene.Cues));
                Console.WriteLine($"Recorded {totalFrames} frames at 24fps: {ConeIntroController.Duration}s intro + 1s gameplay, WAV mix and cue log in {options.RecordIntro}");
                Close();
            }
            else if (_opening!.Controller.Phase != IntroPhase.Complete)
                _opening.Advance(Math.Max(0, Math.Min(ConeIntroController.Duration, _recordFrame / 24f) - _opening.Controller.Time), true);
            else _controls.Step(1f / 24, true);
            return;
        }
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

    protected override void Shutdown() { _coneAudio?.Dispose(); _crashAudio?.Dispose(); _opening?.Dispose(); _scene?.Dispose(); }
}
