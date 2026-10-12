using Engine;
using Engine.Geometry;
using Engine.Geometry.Loaders;
using Engine.Materials;
using Engine.Materials.LitTexture;
using Engine.Materials.ReflectionMapping;
using Engine.Materials.UnlitTexture;
using Engine.Materials.WaveDistortion;
using Engine.OpenGL;
using Example.Materials.NormalColor;
using OpenTK.Mathematics;
using OpenTK.Windowing.Common;
using OpenTK.Windowing.Desktop;
using OpenTK.Windowing.GraphicsLibraryFramework;


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
    private Vector3 _cameraPosition = new(0, 0, 8);
    private Vector3 _cameraTarget = new(0, 0, 0);

    public CubeWindow(GameWindowSettings gameSettings, NativeWindowSettings windowSettings)
        : base(gameSettings, windowSettings) { }

    protected override void Initialize()
    {
        VSync = VSyncMode.On;
        _renderer = new OpenGlRenderer();
        _camera = new Camera(new Vector3(0, 0, 8), _cameraTarget);

        // To switch, comment out the active line and uncomment another one.
        // _texture = Texture.FromFile(Path.Combine(AppContext.BaseDirectory, "Assets", "wood_box.png"));
        // _texture = Texture.FromFile(Path.Combine(AppContext.BaseDirectory, "Assets", "environment.png"));
        _texture = Texture.FromFile(Path.Combine(AppContext.BaseDirectory, "Assets", "monkey.png"));

        // _material = new ReflectionMappingMaterial(_texture);
        _material = new LitTextureMaterial(_texture);

        // _mesh = new Mesh(Primitives.CreateCube());
        _mesh = new Mesh(ObjLoader.Load(Path.Combine(AppContext.BaseDirectory, "Assets", "monkey-smooth.obj")));
    }

    protected override void FramebufferResized(int width, int height) => _renderer!.Resize(width, height);

    // The animation only changes the state; drawing happens exclusively in Render.
    protected override void Update(float deltaTime, KeyboardState keyboardState)
    {
        _elapsedTime += deltaTime;
        // _model = Matrix4.CreateRotationY(_elapsedTime * 0.1f);
        if (_material is WaveDistortionMaterial wave)
            wave.Wobble = _elapsedTime * 5;

        if (keyboardState.IsKeyDown(Keys.Up))
            _cameraPosition.Z -= deltaTime * 5;
            _cameraTarget.Z -=deltaTime *5;

        if (keyboardState.IsKeyDown(Keys.Down))
            _cameraPosition.Z += deltaTime * 5;
            _cameraTarget.Z += deltaTime * 5;

        if (keyboardState.IsKeyDown(Keys.Left))
            _cameraPosition.X -= deltaTime * 5;
            _cameraTarget.X -= deltaTime * 5;

        if (keyboardState.IsKeyDown(Keys.Right))
            _cameraPosition.X += deltaTime * 5;
            _cameraTarget.X += deltaTime * 5;

        if (keyboardState.IsKeyDown(Keys.Space))
            _cameraPosition.Y += deltaTime * 5;
            _cameraTarget.Y += deltaTime * 5;

        if (keyboardState.IsKeyDown(Keys.LeftShift))
            _cameraPosition.Y -= deltaTime * 5;
            _cameraTarget.Y -= deltaTime * 5;
            

        _camera!.LookAt(_cameraPosition, _cameraTarget);
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
