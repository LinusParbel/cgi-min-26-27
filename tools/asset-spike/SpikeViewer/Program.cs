// Throwaway spike viewer for the course engine.
// Screenshot mode: SpikeViewer <model.obj> <texture.png> <out_prefix> [angles=35,215]
// Interactive mode: SpikeViewer --show <a.obj> <a.png> [<b.obj> <b.png> ...]
//   ←/→ orbit, ↑/↓ tilt, W/S zoom, Space toggles turntable, Esc quits.
using Engine;
using Engine.Geometry;
using Engine.Geometry.Loaders;
using Engine.Materials.LitTexture;
using Engine.OpenGL;
using OpenTK.Graphics.OpenGL4;
using OpenTK.Mathematics;
using OpenTK.Windowing.Common;
using OpenTK.Windowing.Desktop;
using OpenTK.Windowing.GraphicsLibraryFramework;
using StbImageWriteSharp;

bool interactive = args[0] == "--show";
var settings = new NativeWindowSettings
{
    ClientSize = interactive ? new Vector2i(1280, 720) : new Vector2i(800, 800),
    Title = "SpikeViewer — ←/→ orbit, ↑/↓ tilt, W/S zoom, Space turntable",
    APIVersion = new Version(3, 3), Profile = ContextProfile.Core
};
if (interactive)
{
    // "model.obj@x,y,z" places a model at an explicit engine position (Y up) — scene mode, the whole
    // scene spins on the turntable. Without '@' models are laid out in a row.
    var pairs = new List<(string, string)>();
    for (int i = 1; i + 1 < args.Length; i += 2) pairs.Add((args[i], args[i + 1]));
    using var w = new Viewer(pairs, null, [], GameWindowSettings.Default, settings);
    w.Run();
}
else
{
    float[] angles = args.Length > 3 ? args[3].Split(',').Select(float.Parse).ToArray() : [35f, 215f];
    using var w = new Viewer([(args[0], args[1])], args[2], angles, GameWindowSettings.Default, settings);
    w.Run();
}

sealed class Viewer(List<(string Obj, string Png)> models, string? outPrefix, float[] angles,
    GameWindowSettings g, NativeWindowSettings n) : Application(g, n)
{
    private const float Spacing = 1.0f;
    private OpenGlRenderer _r = null!;
    private readonly List<(Mesh Mesh, Texture Tex, LitTextureMaterial Mat, Vector3 Center, Vector3? Pos)> _items = [];
    private Camera _cam = null!;
    private int _frame, _shot;
    private float _size, _yaw = 20, _pitch = 15, _zoom = 1, _turntable;
    private bool _spin = true;
    private Vector3 _focus;

    protected override void Initialize()
    {
        _r = new OpenGlRenderer();
        GL.ClearColor(0.55f, 0.62f, 0.7f, 1f);
        for (int i = 0; i < models.Count; i++)
        {
            string[] parts = models[i].Obj.Split('@');
            Vector3? pos = null;
            if (parts.Length == 2)
            {
                float[] xyz = parts[1].Split(',').Select(s => float.Parse(s, System.Globalization.CultureInfo.InvariantCulture)).ToArray();
                pos = new Vector3(xyz[0], xyz[1], xyz[2]);
            }
            MeshData data = ObjLoader.Load(parts[0]);
            Vector3 min = new(float.MaxValue), max = new(float.MinValue);
            foreach (var v in data.Vertices) { min = Vector3.ComponentMin(min, v.Position); max = Vector3.ComponentMax(max, v.Position); }
            _size = MathF.Max(_size, (max - min).Length);
            Console.WriteLine($"{Path.GetFileName(parts[0])}: tris {data.Indices.Length / 3}, size {max - min}");
            var tex = Texture.FromFile(models[i].Png);
            _items.Add((new Mesh(data), tex,
                new LitTextureMaterial(tex) { SpecularStrength = 0.25f, Shininess = 24, AmbientStrength = 0.3f },
                (min + max) / 2, pos));
        }
        if (_items.Any(it => it.Pos.HasValue))
        {
            Vector3 lo = new(float.MaxValue), hi = new(float.MinValue);
            foreach (var it in _items) { var p = it.Pos ?? Vector3.Zero; lo = Vector3.ComponentMin(lo, p); hi = Vector3.ComponentMax(hi, p); }
            _size = MathF.Max(_size, (hi - lo).Length + _size * 0.5f) * 0.7f;
            _focus = new Vector3((lo.X + hi.X) / 2, 0.6f, (lo.Z + hi.Z) / 2);
            _cam = new Camera(Vector3.UnitZ, _focus) { NearPlane = 0.05f, FarPlane = 200 };
            if (outPrefix != null) { _yaw = 0; _pitch = 17; _spin = false; }
            return;
        }
        float rowWidth = (models.Count - 1) * Spacing;
        _focus = new Vector3(0, _items[0].Center.Y, 0);
        _size = MathF.Max(_size, rowWidth + _size * 0.5f);
        _cam = new Camera(Vector3.UnitZ, _focus) { NearPlane = 0.01f, FarPlane = 100 };
        if (outPrefix != null) { _yaw = 0; _pitch = 17; _spin = false; }
    }

    protected override void FramebufferResized(int width, int height) => _r.Resize(width, height);

    protected override void Update(float dt)
    {
        if (outPrefix != null) return;
        var k = KeyboardState;
        if (k.IsKeyDown(Keys.Escape)) Close();
        if (k.IsKeyPressed(Keys.Space)) _spin = !_spin;
        if (k.IsKeyDown(Keys.Left)) _yaw -= 60 * dt;
        if (k.IsKeyDown(Keys.Right)) _yaw += 60 * dt;
        if (k.IsKeyDown(Keys.Up)) _pitch = MathF.Min(85, _pitch + 40 * dt);
        if (k.IsKeyDown(Keys.Down)) _pitch = MathF.Max(-10, _pitch - 40 * dt);
        if (k.IsKeyDown(Keys.W)) _zoom = MathF.Max(0.2f, _zoom - dt);
        if (k.IsKeyDown(Keys.S)) _zoom = MathF.Min(4f, _zoom + dt);
        if (_spin) _turntable += 30 * dt;
    }

    protected override void Render()
    {
        _r.Clear();
        float yaw = MathHelper.DegreesToRadians(_yaw), pitch = MathHelper.DegreesToRadians(_pitch);
        float dist = _size * 1.1f * _zoom;
        Vector3 eye = _focus + dist * new Vector3(MathF.Sin(yaw) * MathF.Cos(pitch), MathF.Sin(pitch), MathF.Cos(yaw) * MathF.Cos(pitch));
        _cam.LookAt(eye, _focus);
        _r.LightPosition = eye + new Vector3(_size, _size * 1.5f, 0);

        float spinDeg = outPrefix != null ? angles[Math.Min(_shot, angles.Length - 1)] : _turntable;
        float start = -(_items.Count - 1) * Spacing / 2;
        for (int i = 0; i < _items.Count; i++)
        {
            var it = _items[i];
            if (it.Pos is Vector3 p)
            {
                Matrix4 placed = Matrix4.CreateTranslation(p - _focus * new Vector3(1, 0, 1))
                               * Matrix4.CreateRotationY(MathHelper.DegreesToRadians(spinDeg))
                               * Matrix4.CreateTranslation(_focus * new Vector3(1, 0, 1));
                _r.Draw(it.Mesh, it.Mat, placed, _cam);
                continue;
            }
            Vector3 c = new(it.Center.X, 0, it.Center.Z);
            Matrix4 model = Matrix4.CreateTranslation(-c) * Matrix4.CreateRotationY(MathHelper.DegreesToRadians(spinDeg))
                          * Matrix4.CreateTranslation(start + i * Spacing, 0, 0);
            _r.Draw(it.Mesh, it.Mat, model, _cam);
        }
        if (outPrefix == null || ++_frame % 5 != 0) return;

        int wpx = FramebufferSize.X, hpx = FramebufferSize.Y;
        var px = new byte[wpx * hpx * 4];
        GL.ReadPixels(0, 0, wpx, hpx, PixelFormat.Rgba, PixelType.UnsignedByte, px);
        var flipped = new byte[px.Length];
        for (int y = 0; y < hpx; y++) Array.Copy(px, y * wpx * 4, flipped, (hpx - 1 - y) * wpx * 4, wpx * 4);
        string path = $"{outPrefix}_{angles[_shot]:0}.png";
        using (var fs = File.Create(path))
            new ImageWriter().WritePng(flipped, wpx, hpx, ColorComponents.RedGreenBlueAlpha, fs);
        Console.WriteLine("saved " + path);
        if (++_shot >= angles.Length) Close();
    }

    protected override void Shutdown()
    {
        foreach (var it in _items) { it.Mesh.Dispose(); it.Tex.Dispose(); }
        _r.Dispose();
    }
}
