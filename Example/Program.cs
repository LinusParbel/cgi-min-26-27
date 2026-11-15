using Engine;
using Engine.Deferred;
using Engine.Geometry;
using Engine.Geometry.Loaders;
using Engine.Lighting;
using Engine.Materials;
using Engine.Materials.Deferred;
using Engine.Materials.TransparentLitTexture;
using Engine.Materials.TransparentTexture;
using Engine.OpenGL;
using Engine.Scenes;
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
            Title = "OpenTK — scene graph",
            APIVersion = new Version(3, 3),
            Profile = ContextProfile.Core
        };

        using var window = new ExampleWindow(GameWindowSettings.Default, windowSettings);
        window.Run();
    }
}

// Scene graph, octree and transparency with deferred rendering:
//  - a big wall with 1000 static objects in front of it, sorted into the octree of the scene,
//    some of them are transparent pyramids (with only a few objects an octree hardly pays off),
//  - a rotating "carousel" in front of it: a hierarchy of nodes that move with their parent,
//  - one directional light and 800 moving point lights.
// Keys: arrows = fly camera, W/S = up/down, 1 = final image, 2/3/4 = color/normal/position G-buffer,
// O = octree on/off (compare the number of visibility tests in the title), Escape = quit.
internal sealed class ExampleWindow : Application
{
    private const int NumberOfObjects = 1000;
    private const int NumberOfLights = 800;

    private OpenGlRenderer? _renderer;
    private DeferredRendering? _deferred;
    private MouseCamera? _mouseCamera;
    private FlyCamera? _flyCamera;      // alternative: keyboard only (see Update)

    // meshes
    private Mesh? _wall;
    private Mesh? _cube;
    private Mesh? _stone;
    private Mesh? _torus;
    private Mesh? _pyramid;

    // textures
    private Texture? _checkerTexture;
    private Texture? _marbleTexture;
    private Texture? _orangeTexture;
    private Texture? _brickNormalMap;
    private Texture? _stoneNormalMap;

    // the scene graph and the visible nodes of the current frame
    private readonly Scene _scene = new();
    private readonly RenderList _renderList = new();

    // nodes that are animated in Update
    private SceneNode? _carousel;
    private readonly List<SceneNode> _planets = new();

    // point lights (not part of the scene graph)
    private readonly List<Vector3> _lightBasePositions = new();
    private readonly List<PointLight> _pointLights = new();
    private readonly List<PointLight> _visibleLights = new();

    // 0 = final image, 1 = color buffer, 2 = normal buffer, 3 = position buffer
    private int _displayMode;
    private float _elapsedTime;

    // the camera used for culling and drawing
    private Camera ActiveCamera => _mouseCamera!.Camera;
    // private Camera ActiveCamera => _flyCamera!.Camera;

    public ExampleWindow(GameWindowSettings gameSettings, NativeWindowSettings windowSettings)
        : base(gameSettings, windowSettings) { }

    protected override void Initialize()
    {
        VSync = VSyncMode.On;
        _renderer = new OpenGlRenderer();
        _deferred = new DeferredRendering(_renderer, FramebufferSize.X, FramebufferSize.Y);
        _mouseCamera = new MouseCamera(new Vector3(0, 0, 6));
        _mouseCamera.Camera.FieldOfViewDegrees = 60.0f;
        _flyCamera = new FlyCamera(new Vector3(0, 0, 6));
        _flyCamera.Camera.FieldOfViewDegrees = 60.0f;

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
        _pyramid = new Mesh(ObjLoader.Load(Asset("pyramid.obj")));

        // textures
        _checkerTexture = Texture.FromFile(Asset("b_checker.png"));
        _marbleTexture = Texture.FromFile(Asset("marble_blue.png"));
        _orangeTexture = Texture.FromFile(Asset("orange.png"));
        _brickNormalMap = Texture.FromFile(Asset("brick_normal.png"));
        _stoneNormalMap = Texture.FromFile(Asset("stone_normal.png"));

        // materials: a material instance holds all its settings (textures, shininess, blending)
        var blueShinyStone = new GBufferMaterial(_marbleTexture, _stoneNormalMap) { Shininess = 80.0f };
        var checkerStone = new GBufferMaterial(_checkerTexture, _stoneNormalMap) { Shininess = 6.0f };
        var goldenBrick = new GBufferMaterial(_checkerTexture, _brickNormalMap) { Shininess = 40.0f };
        // transparent: drawn forward after the light pass, from back to front (lit by the directional light only)
        var orangeGlass = new TransparentLitTextureMaterial(_orangeTexture) { Alpha = 0.5f, Shininess = 60.0f };
        // alternative: transparent without lighting
        // var orangeGlass = new TransparentTextureMaterial(_orangeTexture) { Alpha = 0.5f };
        // alternative: additive blending (order does not matter), e.g. for glowing effects
        // var orangeGlass = new TransparentTextureMaterial(_orangeTexture) { Alpha = 1.0f, BlendMode = BlendMode.Additive };

        // --- static part of the scene: wall and objects, they never move ---
        _scene.Add(new SceneNode("Wall", _wall, blueShinyStone) { Scale = new Vector3(40.0f), IsStatic = true });

        var random = new Random();
        for (int i = 0; i < NumberOfObjects; i++)
        {
            var node = (i % 5) switch
            {
                0 => new SceneNode("Stone", _stone, blueShinyStone) { Scale = new Vector3(0.3f) },
                1 => new SceneNode("Cube", _cube, checkerStone) { Scale = new Vector3(0.8f) },
                2 => new SceneNode("Torus", _torus, goldenBrick) { Scale = new Vector3(0.8f) },
                3 => new SceneNode("Cube", _cube, goldenBrick) { Scale = new Vector3(0.8f) },
                _ => new SceneNode("Pyramid", _pyramid, orangeGlass) { Scale = new Vector3(0.8f) }
            };
            node.Position = new Vector3(random.Next(-400, 400) / 10.0f, random.Next(-400, 400) / 10.0f, 1.0f);
            node.IsStatic = true;
            _scene.Add(node);
        }

        // --- dynamic part: a carousel, every child moves with its parent ---
        //   Carousel (rotates)
        //   ├── Hub (cube)
        //   └── Planet pivot 0..3 (spins)      a node without mesh, only groups its children
        //       ├── Planet (torus)
        //       └── Moon (stone)              circles around the planet because the pivot spins
        _carousel = _scene.Add(new SceneNode("Carousel") { Position = new Vector3(0, 0, 2.5f) });
        _carousel.AddChild(new SceneNode("Hub", _cube, goldenBrick) { Scale = new Vector3(0.4f) });
        for (int i = 0; i < 4; i++)
        {
            float angle = i * MathF.PI / 2;
            SceneNode pivot = _carousel.AddChild(new SceneNode($"Planet pivot {i}")
            {
                Position = new Vector3(MathF.Cos(angle), MathF.Sin(angle), 0) * 1.6f
            });
            pivot.AddChild(new SceneNode("Planet", _torus, blueShinyStone) { Scale = new Vector3(0.4f) });
            pivot.AddChild(new SceneNode("Moon", _stone, checkerStone)
            {
                Position = new Vector3(0.7f, 0, 0),
                Scale = new Vector3(0.06f)
            });
            _planets.Add(pivot);
        }

        // the static nodes are sorted into the octree once (bounds cover the whole scene)
        _scene.BuildOctree(new Vector3(-48, -48, -48), new Vector3(48, 48, 48));

        // point lights with some predefined colors
        Vector3[] lightColors =
        [
            new(1, 0, 0), new(0, 1, 0), new(0, 0, 1),
            new(1, 1, 0), new(0, 1, 1), new(1, 0, 1)
        ];
        for (int i = 0; i < NumberOfLights; i++)
        {
            _lightBasePositions.Add(new Vector3(random.Next(-400, 400) / 10.0f, random.Next(-400, 400) / 10.0f, 1.0f));
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

    // Animation, scene update and visibility test change the state; Render only draws.
    protected override void Update(float deltaTime)
    {
        _elapsedTime += deltaTime;

        if (KeyboardState.IsKeyPressed(Keys.Escape)) Close();
        if (KeyboardState.IsKeyPressed(Keys.D1)) _displayMode = 0;
        if (KeyboardState.IsKeyPressed(Keys.D2)) _displayMode = 1;
        if (KeyboardState.IsKeyPressed(Keys.D3)) _displayMode = 2;
        if (KeyboardState.IsKeyPressed(Keys.D4)) _displayMode = 3;
        if (KeyboardState.IsKeyPressed(Keys.O)) _scene.UseOctree = !_scene.UseOctree;

        // right mouse button + mouse = look around, WASD = move, Q/E = down/up, Shift = faster
        _mouseCamera!.Update(KeyboardState, MouseState, deltaTime);
        // alternative: arrow keys = turn and move, W/S = up/down (also change ActiveCamera)
        // _flyCamera!.Update(KeyboardState, deltaTime);

        // 1. move nodes: only the local transformations are changed
        _carousel!.Rotation = Quaternion.FromAxisAngle(Vector3.UnitZ, _elapsedTime * 0.4f);
        foreach (SceneNode pivot in _planets)
            pivot.Rotation = Quaternion.FromAxisAngle(Vector3.UnitZ, _elapsedTime * 2.0f);

        // 2. world matrices of all nodes (parent * child)
        _scene.Update();

        // 3. visible nodes into the render list (static nodes via the octree)
        Frustum frustum = _renderer!.GetFrustum(ActiveCamera);
        _scene.CollectVisible(frustum, ActiveCamera.Position, _renderList);

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
        Title = $"Scene graph — {modes[_displayMode]} (keys 1-4) — " +
                $"visible: {_renderList.Count}/{_scene.DrawableNodeCount} (transparent: {_renderList.Transparent.Count}) — " +
                $"visibility tests: {_scene.VisibilityTests} (octree {(_scene.UseOctree ? "on" : "off")}, key O) — " +
                $"point lights: {_visibleLights.Count}";
    }

    protected override void Render()
    {
        Camera camera = ActiveCamera;

        // 1. geometry pass: all opaque objects into the G-buffer
        _deferred!.BeginGeometryPass();
        foreach (SceneNode node in _renderList.Opaque)
            _renderer!.Draw(node, camera);

        // 2. light pass, or one of the G-buffer textures as debug view
        switch (_displayMode)
        {
            case 0:
                _deferred.DrawDirectionalLight(camera);
                foreach (PointLight light in _visibleLights)
                    _deferred.DrawPointLight(light, camera);

                // 3. transparent objects: forward, sorted from back to front
                _deferred.BeginTransparentPass();
                foreach (SceneNode node in _renderList.Transparent)
                    _renderer!.Draw(node, camera);
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
        _pyramid?.Dispose();
        _checkerTexture?.Dispose();
        _marbleTexture?.Dispose();
        _orangeTexture?.Dispose();
        _brickNormalMap?.Dispose();
        _stoneNormalMap?.Dispose();
        _deferred?.Dispose();
        _renderer?.Dispose();
    }
}
