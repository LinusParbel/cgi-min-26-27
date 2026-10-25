// Read-only art review scene: existing engine/materials, multiple exported assets.
using System.Text.Json;
using AssetViewer.GammaLit;
using Engine;
using Engine.Geometry.Loaders;
using Engine.OpenGL;
using OpenTK.Graphics.OpenGL4;
using OpenTK.Mathematics;
using OpenTK.Windowing.Common;
using OpenTK.Windowing.Desktop;
using OpenTK.Windowing.GraphicsLibraryFramework;
using StbImageWriteSharp;

if (args.Length != 2)
{
    Console.WriteLine("usage: EssentialScene <scene.json> <output.png|--show>");
    return 1;
}
bool interactive = args[1] == "--show";
using var window = new ReviewWindow(Path.GetFullPath(args[0]), interactive ? null : Path.GetFullPath(args[1]),
    GameWindowSettings.Default, new NativeWindowSettings
    {
        ClientSize = interactive ? new Vector2i(1280, 800) : new Vector2i(1600, 1000),
        StartVisible = true,
        StartFocused = interactive,
        Title = interactive
            ? "Hannover Rush Hour - 3D Viewer | WASD move | Q/E down/up | Right mouse / arrows look | Shift fast | R reset | Esc close"
            : "Essential asset review",
        APIVersion = new Version(3, 3), Profile = ContextProfile.Core
    });
window.Run();
return 0;

sealed class ReviewWindow(string scenePath, string? outputPath,
    GameWindowSettings settings, NativeWindowSettings native) : Application(settings, native)
{
    private OpenGlRenderer _renderer = null!;
    private Camera _camera = null!;
    private readonly Dictionary<string, Mesh> _meshes = new(StringComparer.OrdinalIgnoreCase);
    private readonly Dictionary<string, (Texture Texture, GammaLitMaterial Material)> _textures = new(StringComparer.OrdinalIgnoreCase);
    private readonly List<(Mesh Mesh, GammaLitMaterial Material, Matrix4 Transform)> _draws = [];
    private int _frames;
    private Vector3 _position, _homePosition, _homeTarget;
    private float _yaw, _pitch;
    private Vector2 _lastMouse;
    private bool _looking;
    private string Resolve(string relative) => Path.GetFullPath(Path.Combine(Path.GetDirectoryName(scenePath)!, relative));
    private static Vector3 Vector(JsonElement array)
    {
        var values = array.EnumerateArray().Select(v => v.GetSingle()).ToArray();
        if (values.Length != 3 || values.Any(v => !float.IsFinite(v)))
            throw new InvalidDataException("Expected three finite coordinates.");
        return new Vector3(values[0], values[1], values[2]);
    }
    protected override void Initialize()
    {
        _renderer = new OpenGlRenderer();
        GL.ClearColor(.55f, .62f, .7f, 1);
        using var scene = JsonDocument.Parse(File.ReadAllText(scenePath));
        var root = scene.RootElement;
        _camera = new Camera(Vector(root.GetProperty("camera")), Vector(root.GetProperty("target")))
        {
            NearPlane = .08f, FarPlane = 250,
            FieldOfViewDegrees = root.TryGetProperty("fov", out var fov) ? fov.GetSingle() : 50
        };
        _homePosition = _camera.Position;
        _homeTarget = _camera.Target;
        ResetCamera();
        if (outputPath == null) VSync = VSyncMode.On;
        _renderer.LightPosition = root.TryGetProperty("light", out var light) ? Vector(light) : new Vector3(-10, 25, 15);
        foreach (var item in root.GetProperty("models").EnumerateArray())
        {
            var offset = item.TryGetProperty("offset", out var off) ? Vector(off) : Vector3.Zero;
            var yaw = item.TryGetProperty("yaw", out var angle) ? angle.GetSingle() : 0;
            var scale = item.TryGetProperty("scale", out var size) ? size.GetSingle() : 1;
            if (!float.IsFinite(scale) || scale <= 0 || !float.IsFinite(yaw))
                throw new InvalidDataException("Invalid model scale/yaw.");
            var transform = Matrix4.CreateScale(scale) * Matrix4.CreateRotationY(MathHelper.DegreesToRadians(yaw)) * Matrix4.CreateTranslation(offset);
            if (item.TryGetProperty("manifest", out var path))
            {
                var manifest = Resolve(path.GetString()!);
                var dir = Path.GetDirectoryName(manifest)!;
                using var doc = JsonDocument.Parse(File.ReadAllText(manifest));
                var texture = Path.GetFullPath(Path.Combine(dir, doc.RootElement.GetProperty("texture").GetString()!));
                var selected = item.TryGetProperty("parts", out var names)
                    ? names.EnumerateArray().Select(v => v.GetString()!).ToHashSet() : null;
                foreach (var part in doc.RootElement.GetProperty("parts").EnumerateArray())
                {
                    var name = part.GetProperty("name").GetString()!;
                    if (selected != null && !selected.Contains(name)) continue;
                    var pivot = Vector(part.GetProperty("pivot"));
                    var enginePivot = new Vector3(pivot.X, pivot.Z, -pivot.Y);
                    Add(Path.GetFullPath(Path.Combine(dir, part.GetProperty("obj").GetString()!)), texture,
                        Matrix4.CreateTranslation(enginePivot) * transform);
                }
            }
            else Add(Resolve(item.GetProperty("obj").GetString()!), Resolve(item.GetProperty("texture").GetString()!), transform);
        }
        Console.WriteLine($"Review: {_draws.Count} instances, {_meshes.Count} meshes, {_textures.Count} textures");
        if (outputPath == null)
        {
            IsVisible = true;
            Focus();
            Console.WriteLine($"Interactive viewer visible={IsVisible}, focused={IsFocused}, window={WindowState}");
        }
    }
    private void Add(string obj, string texture, Matrix4 transform)
    {
        if (!_meshes.TryGetValue(obj, out var mesh))
        {
            var data = ObjLoader.Load(obj);
            mesh = new Mesh(data);
            _meshes.Add(obj, mesh);
            Console.WriteLine($"{Path.GetFileName(obj)}: {data.Indices.Length / 3} triangles");
        }
        if (!_textures.TryGetValue(texture, out var surface))
        {
            var tex = Texture.FromFile(texture);
            surface = (tex, new GammaLitMaterial(tex) { AmbientStrength = .35f, SpecularStrength = .12f, Shininess = 24 });
            _textures.Add(texture, surface);
        }
        _draws.Add((mesh, surface.Material, transform));
    }
    protected override void FramebufferResized(int width, int height) => _renderer.Resize(width, height);
    private void ResetCamera()
    {
        _position = _homePosition;
        var forward = Vector3.Normalize(_homeTarget - _homePosition);
        _yaw = MathF.Atan2(forward.Z, forward.X);
        _pitch = MathF.Asin(Math.Clamp(forward.Y, -1, 1));
        _camera.LookAt(_homePosition, _homeTarget);
    }
    protected override void Update(float deltaTime)
    {
        if (outputPath != null) return;
        if (!IsFocused) { _looking = false; return; }
        var keys = KeyboardState;
        if (keys.IsKeyDown(Keys.Escape)) { Close(); return; }
        if (keys.IsKeyDown(Keys.R)) { ResetCamera(); return; }
        float dt = Math.Clamp(deltaTime, 0, .05f);
        var mouse = MouseState.Position;
        bool looking = MouseState.IsButtonDown(MouseButton.Right);
        if (looking && _looking)
        {
            var delta = mouse - _lastMouse;
            _yaw += delta.X * .0035f;
            _pitch -= delta.Y * .0035f;
        }
        _looking = looking;
        _lastMouse = mouse;
        if (keys.IsKeyDown(Keys.Left)) _yaw -= dt * 1.4f;
        if (keys.IsKeyDown(Keys.Right)) _yaw += dt * 1.4f;
        if (keys.IsKeyDown(Keys.Up)) _pitch += dt;
        if (keys.IsKeyDown(Keys.Down)) _pitch -= dt;
        _pitch = Math.Clamp(_pitch, MathHelper.DegreesToRadians(-85), MathHelper.DegreesToRadians(85));
        var forward = new Vector3(MathF.Cos(_pitch) * MathF.Cos(_yaw), MathF.Sin(_pitch), MathF.Cos(_pitch) * MathF.Sin(_yaw));
        var right = Vector3.Normalize(Vector3.Cross(forward, Vector3.UnitY));
        var movement = Vector3.Zero;
        if (keys.IsKeyDown(Keys.W)) movement += forward;
        if (keys.IsKeyDown(Keys.S)) movement -= forward;
        if (keys.IsKeyDown(Keys.D)) movement += right;
        if (keys.IsKeyDown(Keys.A)) movement -= right;
        if (keys.IsKeyDown(Keys.E)) movement += Vector3.UnitY;
        if (keys.IsKeyDown(Keys.Q)) movement -= Vector3.UnitY;
        float speed = keys.IsKeyDown(Keys.LeftShift) || keys.IsKeyDown(Keys.RightShift) ? 15 : 5;
        if (movement.LengthSquared > 0) _position += Vector3.Normalize(movement) * speed * dt;
        _camera.LookAt(_position, _position + forward);
    }
    protected override void Render()
    {
        _renderer.Clear();
        foreach (var draw in _draws) _renderer.Draw(draw.Mesh, draw.Material, draw.Transform, _camera);
        if (outputPath == null) return;
        if (++_frames < 5) return;
        var width = FramebufferSize.X; var height = FramebufferSize.Y;
        var pixels = new byte[width * height * 4]; var flipped = new byte[pixels.Length];
        GL.ReadPixels(0, 0, width, height, PixelFormat.Rgba, PixelType.UnsignedByte, pixels);
        for (var y = 0; y < height; y++)
            Array.Copy(pixels, y * width * 4, flipped, (height - y - 1) * width * 4, width * 4);
        Directory.CreateDirectory(Path.GetDirectoryName(outputPath)!);
        using (var stream = File.Create(outputPath))
            new ImageWriter().WritePng(flipped, width, height, ColorComponents.RedGreenBlueAlpha, stream);
        Console.WriteLine("Saved " + outputPath);
        Close();
    }
    protected override void Shutdown()
    {
        foreach (var mesh in _meshes.Values) mesh.Dispose();
        foreach (var surface in _textures.Values) surface.Texture.Dispose();
        _renderer?.Dispose();
    }
}
