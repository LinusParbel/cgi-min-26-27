// Showcase: Voi scooter and Neues Rathaus side by side, scooter rotating, Rathaus stationary (front view). Esc quits, Left/Right/Space change the spin.
// Usage: dotnet run --project tools/showcase/Showcase.csproj
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

string root = AppContext.BaseDirectory;
while (root != null && !Directory.Exists(Path.Combine(root, "RunnerGame"))) root = Path.GetDirectoryName(root)!;
if (root == null) { Console.WriteLine("repo root not found"); return 1; }
string art = Path.Combine(root, "RunnerGame", "Art", "assets");
var settings = new NativeWindowSettings
{
    ClientSize = new Vector2i(1280, 720),
    Title = "Showcase",
    APIVersion = new Version(3, 3),
    Profile = ContextProfile.Core
};
using var w = new ShowcaseWindow(
    [Path.Combine(art, "scooter_voi", "out", "VEH_ScooterVoi_parts.json"),
     Path.Combine(art, "rathaus_hannover", "out", "BLD_NeuesRathaus_parts.json")],
    GameWindowSettings.Default, settings);
w.Run();
return 0;

sealed class ShowcaseWindow(string[] jsons, GameWindowSettings g, NativeWindowSettings n) : Application(g, n)
{
    private sealed class Part { public Mesh Mesh = null!; public Vector3 Pivot; public bool Wheel; }
    private sealed class Model
    {
        public List<Part> Parts = [];
        public Texture Tex = null!;
        public GammaLitMaterial Mat = null!;
        public Vector3 Focus;
        public float Scale;
        public bool Spin;
        public float X, Zoom = 1;
    }

    private OpenGlRenderer _r = null!;
    private Camera _cam = null!;
    private readonly List<Model> _models = [];
    private float _time, _speed = 40;
    private const float Diagonal = 3f;

    protected override void Initialize()
    {
        _r = new OpenGlRenderer();
        GL.ClearColor(0.55f, 0.62f, 0.7f, 1f);
        foreach (string json in jsons)
        {
            string dir = Path.GetDirectoryName(json)!;
            using var doc = JsonDocument.Parse(File.ReadAllText(json));
            var m = new Model { Tex = Texture.FromFile(Path.Combine(dir, doc.RootElement.GetProperty("texture").GetString()!)) };
            m.Mat = new GammaLitMaterial(m.Tex) { SpecularStrength = 0.25f, Shininess = 24, AmbientStrength = 0.3f };
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
                m.Parts.Add(new Part { Mesh = new Mesh(data), Pivot = t, Wheel = p.GetProperty("name").GetString()!.StartsWith("wheel") });
            }
            m.Focus = (lo + hi) / 2;
            m.Scale = Diagonal / (hi - lo).Length;
            m.Spin = _models.Count == 0;                 // only the scooter rotates
            m.X = m.Spin ? -2.2f : 1.8f;
            m.Zoom = m.Spin ? 1f : 1.7f;                 // Rathaus stays put, facing the camera, zoomed in
            _models.Add(m);
        }
        _cam = new Camera(Vector3.UnitZ, Vector3.Zero) { NearPlane = 0.05f, FarPlane = 100 };
    }

    protected override void FramebufferResized(int width, int height) => _r.Resize(width, height);

    protected override void Update(float dt)
    {
        var k = KeyboardState;
        if (k.IsKeyDown(Keys.Escape)) Close();
        if (k.IsKeyDown(Keys.Left)) _speed -= 80 * dt;
        if (k.IsKeyDown(Keys.Right)) _speed += 80 * dt;
        if (k.IsKeyPressed(Keys.Space)) _speed = _speed == 0 ? 40 : 0;
        _time += dt;
    }

    protected override void Render()
    {
        _r.Clear();
        Vector3 eye = new(0, 1.2f, 8.5f);
        _cam.LookAt(eye, new Vector3(0, 0f, 0));
        _r.LightPosition = eye + new Vector3(3, 4, 2);
        float yaw = MathHelper.DegreesToRadians(_time * _speed);
        float wheelSpin = _time * 8;
        for (int i = 0; i < _models.Count; i++)
        {
            var m = _models[i];
            var place = Matrix4.CreateTranslation(-m.Focus) * Matrix4.CreateScale(m.Scale * m.Zoom)
                      * Matrix4.CreateRotationY(m.Spin ? yaw : 0) * Matrix4.CreateTranslation(m.X, 0, 0);
            foreach (var p in m.Parts)
            {
                var local = p.Wheel ? Matrix4.CreateRotationX(wheelSpin) * Matrix4.CreateTranslation(p.Pivot) : Matrix4.CreateTranslation(p.Pivot);
                _r.Draw(p.Mesh, m.Mat, local * place, _cam);
            }
        }
    }

    protected override void Shutdown()
    {
        foreach (var m in _models)
        {
            foreach (var p in m.Parts) p.Mesh.Dispose();
            m.Tex.Dispose();
        }
        _r.Dispose();
    }
}
