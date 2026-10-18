// AssetViewer: renders a multi-part model (parts.json) gamma-correct.
// Screenshot:  AssetViewer <parts.json> <out_prefix> <views>   views = comma list of "game" and/or yaw degrees
// Interactive: AssetViewer <parts.json> --show   (left/right orbit, up/down tilt, W/S zoom, Esc quits)
// parts.json: {"texture":"X.png","parts":[{"name","obj","pivot":[x,y,z]}]}, pivots in Blender coordinates
// (Blender (x,y,z) -> engine (x,z,-y)); files are relative to the folder of the json.
using System.Globalization;
using System.Text.Json;
using AssetViewer.GammaLit;
using Engine;
using Engine.Geometry;
using Engine.Geometry.Loaders;
using Engine.OpenGL;
using OpenTK.Graphics.OpenGL4;
using OpenTK.Mathematics;
using OpenTK.Windowing.Common;
using OpenTK.Windowing.Desktop;
using OpenTK.Windowing.GraphicsLibraryFramework;
using StbImageWriteSharp;

if (args.Length < 2)
{
    Console.WriteLine("usage: AssetViewer <parts.json> <out_prefix> <views>  |  AssetViewer <parts.json> --show");
    return 1;
}
bool interactive = args[1] == "--show";
string[] views = interactive ? [] : (args.Length > 2 ? args[2] : "game").Split(',', StringSplitOptions.RemoveEmptyEntries);
var settings = new NativeWindowSettings
{
    ClientSize = new Vector2i(1280, 720),
    Title = "AssetViewer",
    APIVersion = new Version(3, 3),
    Profile = ContextProfile.Core
};
using var w = new Viewer(args[0], interactive ? null : args[1], views, GameWindowSettings.Default, settings);
w.Run();
return 0;

sealed class Viewer(string json, string? outPrefix, string[] views, GameWindowSettings g, NativeWindowSettings n)
    : Application(g, n)
{
    private OpenGlRenderer _r = null!;
    private readonly List<(Mesh Mesh, Matrix4 Model)> _parts = [];
    private Texture _tex = null!;
    private GammaLitMaterial _mat = null!;
    private Camera _cam = null!;
    private int _frame, _shot;
    private float _size, _yaw = 20, _pitch = 15, _zoom = 1;
    private Vector3 _focus;

    protected override void Initialize()
    {
        _r = new OpenGlRenderer();
        GL.ClearColor(0.55f, 0.62f, 0.7f, 1f);
        string dir = Path.GetDirectoryName(Path.GetFullPath(json))!;
        using var doc = JsonDocument.Parse(File.ReadAllText(json));
        _tex = Texture.FromFile(Path.Combine(dir, doc.RootElement.GetProperty("texture").GetString()!));
        _mat = new GammaLitMaterial(_tex) { SpecularStrength = 0.25f, Shininess = 24, AmbientStrength = 0.3f };
        Vector3 lo = new(float.MaxValue), hi = new(float.MinValue);
        foreach (var p in doc.RootElement.GetProperty("parts").EnumerateArray())
        {
            var pv = p.GetProperty("pivot").EnumerateArray().Select(e => e.GetSingle()).ToArray();
            var t = new Vector3(pv[0], pv[2], -pv[1]); // Blender (x,y,z) -> engine (x,z,-y)
            MeshData data = ObjLoader.Load(Path.Combine(dir, p.GetProperty("obj").GetString()!));
            foreach (var v in data.Vertices)
            {
                lo = Vector3.ComponentMin(lo, v.Position + t);
                hi = Vector3.ComponentMax(hi, v.Position + t);
            }
            _parts.Add((new Mesh(data), Matrix4.CreateTranslation(t)));
            Console.WriteLine($"{p.GetProperty("name").GetString()}: tris {data.Indices.Length / 3}");
        }
        _size = (hi - lo).Length;
        _focus = (lo + hi) / 2;
        // Clip planes follow the model size: a 130 m building at 1.1x its diagonal lies beyond a fixed 200 m.
        _cam = new Camera(Vector3.UnitZ, _focus) { NearPlane = MathF.Max(0.05f, _size * 0.002f), FarPlane = MathF.Max(200, _size * 6) };
        if (outPrefix != null) _pitch = 17;
    }

    protected override void FramebufferResized(int width, int height) => _r.Resize(width, height);

    protected override void Update(float dt)
    {
        if (outPrefix != null) return;
        var k = KeyboardState;
        if (k.IsKeyDown(Keys.Escape)) Close();
        if (k.IsKeyDown(Keys.Left)) _yaw -= 60 * dt;
        if (k.IsKeyDown(Keys.Right)) _yaw += 60 * dt;
        if (k.IsKeyDown(Keys.Up)) _pitch = MathF.Min(85, _pitch + 40 * dt);
        if (k.IsKeyDown(Keys.Down)) _pitch = MathF.Max(-10, _pitch - 40 * dt);
        if (k.IsKeyDown(Keys.W)) _zoom = MathF.Max(0.2f, _zoom - dt);
        if (k.IsKeyDown(Keys.S)) _zoom = MathF.Min(4f, _zoom + dt);
    }

    protected override void Render()
    {
        _r.Clear();
        string view = outPrefix != null ? views[Math.Min(_shot, views.Length - 1)] : "";
        if (view == "game")
        {
            Vector3 eye = new(0, 1.8f, 3.2f);
            _cam.LookAt(eye, new Vector3(0, 0.9f, -2.0f));
            _r.LightPosition = eye + new Vector3(3, 5, 0);
        }
        else
        {
            float yawDeg = view.Length > 0 ? float.Parse(view, CultureInfo.InvariantCulture) : _yaw;
            float yaw = MathHelper.DegreesToRadians(yawDeg), pitch = MathHelper.DegreesToRadians(_pitch);
            float dist = _size * 1.1f * _zoom;
            Vector3 eye = _focus + dist * new Vector3(MathF.Sin(yaw) * MathF.Cos(pitch), MathF.Sin(pitch), MathF.Cos(yaw) * MathF.Cos(pitch));
            _cam.LookAt(eye, _focus);
            _r.LightPosition = eye + new Vector3(_size, _size * 1.5f, 0);
        }
        foreach (var (mesh, model) in _parts) _r.Draw(mesh, _mat, model, _cam);
        if (outPrefix == null || ++_frame % 5 != 0) return;

        int wpx = FramebufferSize.X, hpx = FramebufferSize.Y;
        var px = new byte[wpx * hpx * 4];
        GL.ReadPixels(0, 0, wpx, hpx, PixelFormat.Rgba, PixelType.UnsignedByte, px);
        var flipped = new byte[px.Length];
        for (int y = 0; y < hpx; y++) Array.Copy(px, y * wpx * 4, flipped, (hpx - 1 - y) * wpx * 4, wpx * 4);
        string path = $"{outPrefix}_{view}.png";
        using (var fs = File.Create(path))
            new ImageWriter().WritePng(flipped, wpx, hpx, ColorComponents.RedGreenBlueAlpha, fs);
        Console.WriteLine("saved " + path);
        if (++_shot >= views.Length) Close();
    }

    protected override void Shutdown()
    {
        foreach (var (mesh, _) in _parts) mesh.Dispose();
        _tex.Dispose();
        _r.Dispose();
    }
}
