using Engine;
using Engine.Geometry;
using Engine.Geometry.Loaders;
using Engine.Lighting;
using Engine.Materials;
using Engine.Materials.CubeReflection;
using Engine.Materials.NormalMapping;
using Engine.Materials.NormalMappingCubeSpecular;
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
            Title = "OpenTK — frustum culling and cube mapping",
            APIVersion = new Version(3, 3),
            Profile = ContextProfile.Core
        };

        using var window = new ExampleWindow(GameWindowSettings.Default, windowSettings);
        window.Run();
    }
}

// 200 rotating objects, randomly placed. Only the objects inside the view frustum are drawn.
// Keys: arrows = fly camera, W/S = up/down, 1/2/3 = switch material, Escape = quit.
internal sealed class ExampleWindow : Application
{
    private const int NumberOfObjects = 200;

    private OpenGlRenderer? _renderer;
    private FlyCamera? _flyCamera;

    // three meshes; they are drawn with different scales
    private Mesh? _cube;
    private Mesh? _stone;
    private Mesh? _torus;

    // color textures, normal maps and cube maps
    private Texture? _checkerTexture;
    private Texture? _marbleTexture;
    private Texture? _brickNormalMap;
    private Texture? _stoneNormalMap;
    private CubeTexture? _environmentCubeTexture;
    private CubeTexture? _darkerEnvironmentCubeTexture;

    // the materials that can be switched with the keys 1, 2 and 3
    private Material[] _materials = [];
    private int _materialIndex;

    // random positions of the objects, and the objects found visible in Update
    private readonly List<Vector3> _positions = new();
    private readonly List<(Mesh Mesh, Matrix4 Model)> _visibleObjects = new();

    private float _elapsedTime;

    public ExampleWindow(GameWindowSettings gameSettings, NativeWindowSettings windowSettings)
        : base(gameSettings, windowSettings) { }

    protected override void Initialize()
    {
        VSync = VSyncMode.On;
        _renderer = new OpenGlRenderer();
        _flyCamera = new FlyCamera(new Vector3(0, 0, 3));
        _flyCamera.Camera.FieldOfViewDegrees = 60.0f;

        _renderer.DirectionalLight = new DirectionalLight
        {
            Direction = new Vector3(1.0f, -1.0f, 2.0f),
            AmbientColor = new Vector3(0.3f, 0.3f, 0.3f),
            DiffuseColor = new Vector3(0.8f, 0.8f, 0.8f),
            SpecularColor = new Vector3(1.0f, 1.0f, 1.0f)
        };

        // meshes
        _cube = new Mesh(Primitives.CreateCube());
        _stone = new Mesh(ObjLoader.Load(Asset("round_stone.obj")));
        _torus = new Mesh(ObjLoader.Load(Asset("torus_smooth.obj")));

        // textures
        _checkerTexture = Texture.FromFile(Asset("b_checker.png"));
        _marbleTexture = Texture.FromFile(Asset("marble_blue.png"));
        _brickNormalMap = Texture.FromFile(Asset("brick_normal.png"));
        _stoneNormalMap = Texture.FromFile(Asset("stone_normal.png"));

        // cube maps: the six sides in the order +X, -X, +Y, -Y, +Z, -Z
        _environmentCubeTexture = CubeTexture.FromFiles(
            Asset("cube/env_reflect_left.png"), Asset("cube/env_reflect_right.png"),
            Asset("cube/env_reflect_top.png"), Asset("cube/env_reflect_bottom.png"),
            Asset("cube/env_reflect_back.png"), Asset("cube/env_reflect_front.png"));
        _darkerEnvironmentCubeTexture = CubeTexture.FromFiles(
            Asset("cube/cmap2_left.png"), Asset("cube/cmap2_right.png"),
            Asset("cube/cmap2_top.png"), Asset("cube/cmap2_bottom.png"),
            Asset("cube/cmap2_back.png"), Asset("cube/cmap2_front.png"));

        _materials =
        [
            new NormalMappingMaterial(_checkerTexture, _brickNormalMap) { Shininess = 15.0f },
            new CubeReflectionMaterial(_brickNormalMap, _environmentCubeTexture),
            new NormalMappingCubeSpecularMaterial(_marbleTexture, _stoneNormalMap, _darkerEnvironmentCubeTexture)
        ];

        // random positions between -10 and 10 on every axis
        var random = new Random();
        for (int i = 0; i < NumberOfObjects; i++)
            _positions.Add(new Vector3(random.Next(-100, 100) / 10.0f, random.Next(-100, 100) / 10.0f, random.Next(-100, 100) / 10.0f));
    }

    private static string Asset(string fileName) => Path.Combine(AppContext.BaseDirectory, "Assets", fileName);

    protected override void FramebufferResized(int width, int height) => _renderer!.Resize(width, height);

    // The animation, the camera and the visibility test change the state; Render only draws.
    protected override void Update(float deltaTime)
    {
        _elapsedTime += deltaTime;

        if (KeyboardState.IsKeyPressed(Keys.Escape)) Close();
        if (KeyboardState.IsKeyPressed(Keys.D1)) _materialIndex = 0;
        if (KeyboardState.IsKeyPressed(Keys.D2)) _materialIndex = 1;
        if (KeyboardState.IsKeyPressed(Keys.D3)) _materialIndex = 2;

        _flyCamera!.Update(KeyboardState, deltaTime);

        // the frustum has to be recalculated after every camera movement
        Frustum frustum = _renderer!.GetFrustum(_flyCamera.Camera);

        _visibleObjects.Clear();
        for (int i = 0; i < NumberOfObjects; i++)
        {
            (Mesh mesh, float scale) = (i % 3) switch
            {
                0 => (_cube!, 0.8f),
                1 => (_stone!, 0.3f),
                _ => (_torus!, 0.8f)
            };

            Matrix4 model = Matrix4.CreateScale(scale)
                          * Matrix4.CreateRotationX(_elapsedTime * 0.5f)
                          * Matrix4.CreateRotationY(_elapsedTime * 0.25f)
                          * Matrix4.CreateRotationZ(_elapsedTime * 0.25f)
                          * Matrix4.CreateTranslation(_positions[i]);

            // frustum culling: only objects whose sphere lies (partly) inside the frustum are drawn
            if (frustum.IsVisible(mesh, model))
                _visibleObjects.Add((mesh, model));
        }

        Title = $"Frustum culling — visible objects: {_visibleObjects.Count} / {NumberOfObjects} — material {_materialIndex + 1} (keys 1-3)";
    }

    protected override void Render()
    {
        _renderer!.Clear();
        foreach ((Mesh mesh, Matrix4 model) in _visibleObjects)
            _renderer.Draw(mesh, _materials[_materialIndex], model, _flyCamera!.Camera);
    }

    protected override void Shutdown()
    {
        _cube?.Dispose();
        _stone?.Dispose();
        _torus?.Dispose();
        _checkerTexture?.Dispose();
        _marbleTexture?.Dispose();
        _brickNormalMap?.Dispose();
        _stoneNormalMap?.Dispose();
        _environmentCubeTexture?.Dispose();
        _darkerEnvironmentCubeTexture?.Dispose();
        _renderer?.Dispose();
    }
}
