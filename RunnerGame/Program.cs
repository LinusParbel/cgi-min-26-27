using Engine;
using Engine.Geometry;
using Engine.Geometry.Loaders;
using Engine.Materials;
using Engine.Materials.ReflectionMapping;
using Engine.Materials.UnlitTexture;
using Engine.Materials.WaveDistortion;
using Engine.Materials.AmbientDiffuseSpecular;
using Engine.OpenGL;
using Example.Materials.NormalColor;
using OpenTK.Mathematics;
using OpenTK.Windowing.Common;
using OpenTK.Windowing.Desktop;
using Engine.Lighting;

namespace Example;

internal static class Program
{
    private static void Main()
    {
        var windowSettings = new NativeWindowSettings
        {
            ClientSize = new Vector2i(960, 720),
            Title = "OpenTK — textured model",
            APIVersion = new Version(3, 3),
            Profile = ContextProfile.Core
        };

        using var window = new CubeWindow(GameWindowSettings.Default, windowSettings);
        window.Run();
    }
}

internal sealed class CubeWindow : Application
{
    private OpenGlRenderer? _renderer;
    private Camera? _camera;
    private Mesh? _mesh;
    private Texture? _texture;
    private Material? _material;
    private float _elapsedTime;
    private Matrix4 _model = Matrix4.Identity;

    public CubeWindow(GameWindowSettings gameSettings, NativeWindowSettings windowSettings)
        : base(gameSettings, windowSettings) { }

    protected override void Initialize()
    {
        VSync = VSyncMode.On;
        _renderer = new OpenGlRenderer();
        _camera = new Camera(new Vector3(0, 0, 8), Vector3.Zero);

        _renderer.DirectionalLight = new DirectionalLight
        {
            Direction = new Vector3(1.0f, 1.0f, 1.0f),
            AmbientColor = new Vector3(0.5f, 0.3f, 0.2f),
            DiffuseColor = new Vector3(0.8f, 0.8f, 0.8f),
            SpecularColor = new Vector3(1.0f, 1.0f, 1.0f)
        };

        // To switch, comment out the active line and uncomment another one.
        _texture = Texture.FromFile(Path.Combine(AppContext.BaseDirectory, "Assets", "wood_box.png"));
        // _texture = Texture.FromFile(Path.Combine(AppContext.BaseDirectory, "Assets", "environment.png"));

        // _material = new UnlitTextureMaterial(_texture);
        // _material = new WaveDistortionMaterial(_texture);
        // _material = new ReflectionMappingMaterial(_texture);
        // _material = new NormalColorMaterial();   // own material in this project, see Materials/NormalColor
        _material = new AmbientDiffuseSpecularMaterial(_texture);

        _mesh = new Mesh(Primitives.CreateCube());
        // _mesh = new Mesh(ObjLoader.Load(Path.Combine(AppContext.BaseDirectory, "Assets", "star.obj")));
        // _mesh = new Mesh(ObjLoader.Load(Path.Combine(AppContext.BaseDirectory, "Assets", "duck_flat.obj")));
        // _mesh = new Mesh(ObjLoader.Load(Path.Combine(AppContext.BaseDirectory, "Assets", "duck_smooth.obj")));
    }

    protected override void FramebufferResized(int width, int height) => _renderer!.Resize(width, height);

    // The animation only changes the state; drawing happens exclusively in Render.
    protected override void Update(float deltaTime)
    {
        _elapsedTime += deltaTime;
        _model = Matrix4.CreateRotationX(_elapsedTime * 0.43f)
               * Matrix4.CreateRotationY(_elapsedTime * 0.7f);
        if (_material is WaveDistortionMaterial wave)
            wave.Wobble = _elapsedTime * 5;
    }

    protected override void Render()
    {
        _renderer!.Clear();
        _renderer.Draw(_mesh!, _material!, _model, _camera!);
    }

    protected override void Shutdown()
    {
        _mesh?.Dispose();
        _texture?.Dispose();
        _renderer?.Dispose();
    }
}
