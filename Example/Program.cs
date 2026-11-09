using Engine;
using Engine.Deferred;
using Engine.Geometry;
using Engine.Geometry.Loaders;
using Engine.Lighting;
using Engine.Materials.Deferred;
using Engine.OpenGL;
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
            ClientSize = new Vector2i(1280, 720),
            Title = "OpenTK — deferred rendering",
            APIVersion = new Version(3, 3),
            Profile = ContextProfile.Core
        };

        using var window = new ExampleWindow(GameWindowSettings.Default, windowSettings);
        window.Run();
    }
}

// Deferred rendering: a wall with 200 objects in front of it, lit by one directional light
// and 200 moving point lights. Frustum culling is used for the objects and for the lights.
// Keys: arrows = fly camera, W/S = up/down, 1 = final image, 2/3/4 = color/normal/position G-buffer,
// Escape = quit.
internal sealed class ExampleWindow : Application
{
    private const int NumberOfObjects = 200;
    private const int NumberOfLights = 200;

    private OpenGlRenderer? _renderer;
    private DeferredRendering? _deferred;
    private FlyCamera? _flyCamera;

    // meshes
    private Mesh? _wall;
    private Mesh? _cube;
    private Mesh? _stone;
    private Mesh? _torus;

    // textures
    private Texture? _checkerTexture;
    private Texture? _marbleTexture;
    private Texture? _brickNormalMap;
    private Texture? _stoneNormalMap;

    // G-buffer materials: color texture, normal map and shininess
    private GBufferMaterial? _wallMaterial;
    private GBufferMaterial? _cubeMaterial;
    private GBufferMaterial? _stoneMaterial;
    private GBufferMaterial? _torusMaterial;

    // the scene: object positions and point lights
    private readonly List<Vector3> _positions = new();
    private readonly List<Vector3> _lightBasePositions = new();
    private readonly List<PointLight> _pointLights = new();

    // filled in Update by the frustum culling, drawn in Render
    private readonly List<(Mesh Mesh, GBufferMaterial Material, Matrix4 Model)> _visibleObjects = new();
    private readonly List<PointLight> _visibleLights = new();

    // 0 = final image, 1 = color buffer, 2 = normal buffer, 3 = position buffer
    private int _displayMode;
    private float _elapsedTime;

    public ExampleWindow(GameWindowSettings gameSettings, NativeWindowSettings windowSettings)
        : base(gameSettings, windowSettings) { }

    protected override void Initialize()
    {
        VSync = VSyncMode.On;
        _renderer = new OpenGlRenderer();
        _deferred = new DeferredRendering(_renderer, FramebufferSize.X, FramebufferSize.Y);
        _flyCamera = new FlyCamera(new Vector3(0, 0, 3));
        _flyCamera.Camera.FieldOfViewDegrees = 60.0f;

        // the directional light is drawn in the light pass on a fullscreen quad
        _renderer.DirectionalLight = new DirectionalLight
        {
            Direction = new Vector3(1.0f, -1.0f, 0.2f),
            AmbientColor = new Vector3(0.3f, 0.3f, 0.3f),
            DiffuseColor = new Vector3(0.8f, 0.8f, 0.8f),
            SpecularColor = new Vector3(1.0f, 1.0f, 1.0f)
        };

        // meshes
        _wall = new Mesh(ObjLoader.Load(Asset("thin_wall.obj")));
        _cube = new Mesh(Primitives.CreateCube());
        _stone = new Mesh(ObjLoader.Load(Asset("round_stone.obj")));
        _torus = new Mesh(ObjLoader.Load(Asset("torus_smooth.obj")));

        // textures
        _checkerTexture = Texture.FromFile(Asset("b_checker.png"));
        _marbleTexture = Texture.FromFile(Asset("marble_blue.png"));
        _brickNormalMap = Texture.FromFile(Asset("brick_normal.png"));
        _stoneNormalMap = Texture.FromFile(Asset("stone_normal.png"));

        // materials for the geometry pass
        _wallMaterial = new GBufferMaterial(_marbleTexture, _stoneNormalMap) { Shininess = 6.0f };
        _cubeMaterial = new GBufferMaterial(_checkerTexture, _brickNormalMap) { Shininess = 126.0f };
        _stoneMaterial = new GBufferMaterial(_marbleTexture, _stoneNormalMap) { Shininess = 120.0f };
        _torusMaterial = new GBufferMaterial(_checkerTexture, _brickNormalMap) { Shininess = 120.0f };

        // random object positions in front of the wall
        var random = new Random();
        for (int i = 0; i < NumberOfObjects; i++)
            _positions.Add(new Vector3(random.Next(-200, 200) / 10.0f, random.Next(-200, 200) / 10.0f, 1.0f));

        // point lights with some predefined colors
        Vector3[] lightColors =
        [
            new(1, 0, 0), new(0, 1, 0), new(0, 0, 1),
            new(1, 1, 0), new(0, 1, 1), new(1, 0, 1)
        ];
        for (int i = 0; i < NumberOfLights; i++)
        {
            _lightBasePositions.Add(new Vector3(random.Next(-200, 200) / 10.0f, random.Next(-200, 200) / 10.0f, 1.0f));
            Vector3 color = lightColors[i % lightColors.Length];
            _pointLights.Add(new PointLight { AmbientColor = color, DiffuseColor = color, SpecularColor = Vector3.One, Radius = 3.0f });
        }
    }

    private static string Asset(string fileName) => Path.Combine(AppContext.BaseDirectory, "Assets", fileName);

    protected override void FramebufferResized(int width, int height)
    {
        _renderer!.Resize(width, height);
        _deferred!.Resize(width, height);
    }

    // Camera, lights and the visibility test change the state; Render only draws.
    protected override void Update(float deltaTime)
    {
        _elapsedTime += deltaTime;

        if (KeyboardState.IsKeyPressed(Keys.Escape)) Close();
        if (KeyboardState.IsKeyPressed(Keys.D1)) _displayMode = 0;
        if (KeyboardState.IsKeyPressed(Keys.D2)) _displayMode = 1;
        if (KeyboardState.IsKeyPressed(Keys.D3)) _displayMode = 2;
        if (KeyboardState.IsKeyPressed(Keys.D4)) _displayMode = 3;

        _flyCamera!.Update(KeyboardState, deltaTime);
        Frustum frustum = _renderer!.GetFrustum(_flyCamera.Camera);

        // objects: the wall plus the objects in front of it, only the visible ones
        _visibleObjects.Clear();
        Matrix4 wallModel = Matrix4.CreateScale(20.0f);
        if (frustum.IsVisible(_wall!, wallModel))
            _visibleObjects.Add((_wall!, _wallMaterial!, wallModel));

        for (int i = 0; i < NumberOfObjects; i++)
        {
            (Mesh mesh, GBufferMaterial material, float scale) = (i % 3) switch
            {
                0 => (_cube!, _cubeMaterial!, 0.8f),
                1 => (_stone!, _stoneMaterial!, 0.3f),
                _ => (_torus!, _torusMaterial!, 0.8f)
            };
            Matrix4 model = Matrix4.CreateScale(scale) * Matrix4.CreateTranslation(_positions[i]);
            if (frustum.IsVisible(mesh, model))
                _visibleObjects.Add((mesh, material, model));
        }

        // point lights move around their base position; lights outside the frustum are not drawn
        _visibleLights.Clear();
        for (int i = 0; i < NumberOfLights; i++)
        {
            float t = _elapsedTime;
            var offset = new Vector3(
                (MathF.Sin(t * 1.2f + i * 20) + MathF.Cos(t * 3.12f + i * 31)) * 2.0f,
                (MathF.Sin(t * 2.04f + i * 20) + MathF.Cos(t * 2.76f + i * 30)) * 2.0f,
                0.0f);
            PointLight light = _pointLights[i];
            light.Position = _lightBasePositions[i] + offset;
            if (frustum.SphereInFrustum(light.Position, light.Radius))
                _visibleLights.Add(light);
        }

        string[] modes = ["final image", "color buffer", "normal buffer", "position buffer"];
        Title = $"Deferred rendering — {modes[_displayMode]} (keys 1-4) — objects: {_visibleObjects.Count}, point lights: {_visibleLights.Count}";
    }

    protected override void Render()
    {
        Camera camera = _flyCamera!.Camera;

        // 1. geometry pass: all objects into the G-buffer
        _deferred!.BeginGeometryPass();
        foreach ((Mesh mesh, GBufferMaterial material, Matrix4 model) in _visibleObjects)
            _renderer!.Draw(mesh, material, model, camera);

        // 2. light pass, or one of the G-buffer textures as debug view
        switch (_displayMode)
        {
            case 0:
                _deferred.DrawDirectionalLight(camera);
                foreach (PointLight light in _visibleLights)
                    _deferred.DrawPointLight(light, camera);
                break;
            case 1:
                _deferred.ShowGBufferTexture(_deferred.GBuffer.ColorTexture, camera);
                break;
            case 2:
                _deferred.ShowGBufferTexture(_deferred.GBuffer.NormalShininessTexture, camera);
                break;
            default:
                _deferred.ShowGBufferTexture(_deferred.GBuffer.PositionTexture, camera);
                break;
        }
    }

    protected override void Shutdown()
    {
        _wall?.Dispose();
        _cube?.Dispose();
        _stone?.Dispose();
        _torus?.Dispose();
        _checkerTexture?.Dispose();
        _marbleTexture?.Dispose();
        _brickNormalMap?.Dispose();
        _stoneNormalMap?.Dispose();
        _deferred?.Dispose();
        _renderer?.Dispose();
    }
}
