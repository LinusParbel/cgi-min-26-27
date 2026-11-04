using Engine;
using Engine.Geometry.Loaders;
using Engine.OpenGL;
using OpenTK.Graphics.OpenGL4;
using OpenTK.Mathematics;
using RunnerGame.Gameplay;
using RunnerGame.Animation;
using RunnerGame.Materials.RunnerLit;

namespace RunnerGame.Rendering;

/// <summary>Owns GPU resources; all scene animation is derived from the simulation snapshot.</summary>
public sealed class SceneRenderer : IRunnerScene
{
    private sealed record Part(string Name, Mesh Mesh, RunnerLitMaterial Material, Vector3 Pivot);
    private readonly Dictionary<string, Mesh> _meshes = new(StringComparer.OrdinalIgnoreCase);
    private readonly Dictionary<string, (Texture Texture, RunnerLitMaterial Material)> _textures = new(StringComparer.OrdinalIgnoreCase);
    private readonly Dictionary<string, Part[]> _models = new();
    private readonly OpenGlRenderer _renderer;
    private readonly Camera _camera = new(new Vector3(0, 2.8f, 5.5f), new Vector3(0, 1, -10))
        { NearPlane = .08f, FarPlane = 300, FieldOfViewDegrees = 58 };
    private bool _disposed;
    private readonly string _assetsRoot;
    private ConeIntroRenderer? _intro;
    private readonly VanCrashRenderer _vanCrash;
    private bool _crashDrawing;
    private MapShadowPass? _shadows;
    private readonly List<IntroDraw> _frameDraws = [];
    public string ShadowDiagnostics => _shadows?.Diagnostics ?? "Road shadows not prepared";
    public int MeshCount => _meshes.Count + (_intro?.MeshCount ?? 0) + _vanCrash.MeshCount;
    public int TextureCount => _textures.Count + (_intro?.TextureCount ?? 0) + _vanCrash.TextureCount;
    public int DrawCount { get; private set; }

    /// <param name="assetsRoot">The installed Assets directory containing Models.</param>
    public SceneRenderer(string assetsRoot)
    {
        _assetsRoot = assetsRoot;
        _renderer = new OpenGlRenderer { LightPosition = new Vector3(-20, 45, 15) };
        _vanCrash = new VanCrashRenderer(assetsRoot);
        GL.ClearColor(.55f, .62f, .70f, 1);
        try
        {
            string root = Path.Combine(Path.GetFullPath(assetsRoot), "Models");
            void Manifest(string key, string relative, params string[] selected)
            {
                var parts = ModelManifest.Read(ModelManifest.Resolve(root, relative));
                _models.Add(key, parts.Where(p => selected.Length == 0 || selected.Contains(p.Name))
                    .Select(p => Load(p.Name, p.ObjPath, p.TexturePath, p.Pivot)).ToArray());
                if (_models[key].Length == 0) throw new InvalidDataException($"No selected parts in {relative}");
            }
            void Single(string key, string directory, string basename)
            {
                _models.Add(key, [Load(key, ModelManifest.Resolve(root, $"{directory}/{basename}.obj"),
                    ModelManifest.Resolve(root, $"{directory}/{basename}.png"), Vector3.Zero)]);
            }
            Manifest("street", "Umgebung/StreetKit/ST_Street_parts.json");
            Manifest("plaza", "Umgebung/StreetKit/ST_Street_parts.json", "pavement_right");
            Manifest("shop", "Gebaeude/ShopfrontKit/AR_Shopfront_parts.json", "shop_ground");
            Manifest("sandstone", "Gebaeude/ShopfrontKit/AR_Shopfront_parts.json", "sandstone_upper");
            Manifest("brick", "Gebaeude/ShopfrontKit/AR_Shopfront_parts.json", "brick_upper");
            Manifest("scooter", "Fahrzeug/ScooterVoi/VEH_ScooterVoi_parts.json");
            Manifest("ride", "Charakter/ScooterRider/CHR_ScooterRider_ride_parts.json");
            Manifest("duck", "Charakter/ScooterRider/CHR_ScooterRider_duck_parts.json");
            Manifest("Car", "Fahrzeug/CityCar/VEH_CityCar_parts.json");
            Manifest("Van", "Fahrzeug/DeliveryVan/VEH_DeliveryVan_parts.json");
            Manifest("Coin", "Pickup/CityToken/PROP_CityToken_parts.json");
            Manifest("HighBarrier", "Baustelle/DuckBarrier/PROP_DuckBarrier_parts.json");
            Manifest("Pothole", "Umgebung/Pothole/PROP_Pothole_parts.json");
            Manifest("tree", "Umgebung/StreetTree/ENV_StreetTree_parts.json");
            Manifest("clock", "Wahrzeichen/KroepckeUhr/PRP_KroepckeUhr_parts.json");
            Manifest("rathaus", "Wahrzeichen/NeuesRathaus/BLD_NeuesRathaus_parts.json");
            Manifest("bench", "Umgebung/StreetFurniture/PROP_StreetFurniture_bench_parts.json");
            Manifest("planter", "Umgebung/StreetFurniture/PROP_StreetFurniture_planter_parts.json");
            Manifest("lamp", "Umgebung/StreetFurniture/PROP_StreetFurniture_lamp_parts.json");
            Manifest("table", "Umgebung/PavementProps/PROP_Pavement_parts.json", "table");
            Manifest("chair", "Umgebung/PavementProps/PROP_Pavement_parts.json", "chair");
            Single("Cone", "Baustelle/Leitkegel", "PROP_Leitkegel_75");
            Single("Bin", "Mull/Tonne", "PROP_WheelieBin_120L_restmuell");
            string officerDirectory = Path.Combine(root, "Charakter/Ordnungsamt");
            // Four uniformly sampled frames retain the gait without loading forty dense meshes.
            for (int i = 0; i < 4; i++)
                _models.Add($"officer{i}", [Load("officer", ModelManifest.Resolve(officerDirectory, $"CHR_Ordnungsamt_run_{1 + i * 10:00}.obj"),
                    ModelManifest.Resolve(officerDirectory, "CHR_Ordnungsamt.png"), Vector3.Zero)]);
        }
        catch { Dispose(); throw; }
    }

    private Part Load(string name, string obj, string png, Vector3 pivot)
    {
        if (!_meshes.TryGetValue(obj, out var mesh))
        {
            mesh = new Mesh(ObjLoader.Load(obj));
            _meshes.Add(obj, mesh);
        }
        if (!_textures.TryGetValue(png, out var surface))
        {
            var texture = Texture.FromFile(png);
            surface = (texture, new RunnerLitMaterial(texture));
            _textures.Add(png, surface);
        }
        return new Part(name, mesh, surface.Material, pivot);
    }

    public void Resize(int w, int h) => _renderer.Resize(w, h);
    public void PrepareIntro(ConeIntroScene scene) => _intro ??= new ConeIntroRenderer(_assetsRoot, scene);

    private void SquareFacade(Vector3 position, float yaw, bool brick = false, float width = 6)
    {
        var dimensions = new Vector3(width / 6, 1, 1);
        Draw("shop", position, yaw, dimensions: dimensions);
        Draw(brick ? "brick" : "sandstone", position + new Vector3(0, 3.2f, 0), yaw,
            dimensions: dimensions);
    }

    private void Draw(string key, Vector3 position, float yaw = 0, float wheelAngle = 0, float scale = 1,
        Vector3? dimensions = null)
    {
        var transform = Matrix4.CreateScale(dimensions ?? new Vector3(scale)) * Matrix4.CreateRotationY(yaw) * Matrix4.CreateTranslation(position);
        DrawTransform(key,transform,wheelAngle);
    }

    private void DrawTransform(string key,Matrix4 transform,float wheelAngle=0,bool immediate=false)
    {
        foreach (var part in _models[key])
        {
            if(_crashDrawing && key=="street" && part.Name=="road")continue;
            var rotation = part.Name.StartsWith("wheel", StringComparison.Ordinal)
                ? Matrix4.CreateRotationX(wheelAngle) : Matrix4.Identity;
            var model=rotation * Matrix4.CreateTranslation(part.Pivot) * transform;
            if(immediate)_renderer.Draw(part.Mesh,part.Material,model,_camera);
            else _frameDraws.Add(new(part.Mesh,part.Material,model));
            DrawCount++;
        }
    }

    public void Render(RunSimulation state, IntroRenderState? intro = null)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        DrawCount = 0;
        _frameDraws.Clear();
        _crashDrawing=intro==null && state.VanCrash!=null;
        ConeIntroSample? introSample = intro?.Scene.Sample(intro.Time);
        var stageOffset = intro?.Scene.StageOffset("street") ?? Vector3.Zero;
        if (introSample != null) _camera.LookAt(introSample.CameraPosition + stageOffset, introSample.CameraTarget + stageOffset);
        else if(state.VanCrash is {} crash)_vanCrash.SetCamera(crash,_camera);
        else _camera.LookAt(new(0, 2.8f, 5.5f), new(0, 1, -10));
        float distance = (float)state.Distance;
        float time = (float)state.ElapsedTime;
        float streetOffset = distance % 20;
        // One landmark district per long block; all scenery shares the road's travel distance.
        // This is an intentionally compressed Hannover setting, not a geographic reconstruction.
        float districtOffset = distance % 420;
        float clockZ = districtOffset + 18;
        if (clockZ > 70) clockZ -= 420;
        float rathausZ = districtOffset - 6;
        if (rathausZ > 115) rathausZ -= 420;
        for (int i = intro != null ? -2 : 0; i < 10; i++)
        {
            float z = 20 - i * 20 + streetOffset;
            if (z <= (intro != null ? 60 : 20)) Draw("street", new Vector3(0, 0, z));
        }
        // A facade bay is exactly six metres wide. Rotate it onto each pavement edge.
        int firstBay = (int)MathF.Floor((distance - (intro != null ? 60 : 0)) / 6);
        for (int i = 0; i < (intro != null ? 35 : 25); i++)
        {
            int bay = firstBay + i;
            float z = distance - bay * 6;
            if (z > (intro != null ? 60 : 5) || z < -140) continue;
            foreach (int side in new[] { -1, 1 })
            {
                // Open the shopfront rows around both landmark squares.
                if ((side == 1 && MathF.Abs(z - clockZ) < 18) ||
                    (side == -1 && MathF.Abs(z - rathausZ) < 48)) continue;
                float yaw = -side * MathF.PI / 2;
                Draw("shop", new Vector3(side * 6.15f, .16f, z), yaw);
                Draw((bay + (side == 1 ? 1 : 0)) % 3 == 0 ? "brick" : "sandstone",
                    new Vector3(side * 6.15f, 3.36f, z), yaw);
            }
        }
        int firstProp = (int)MathF.Floor((distance - (intro != null ? 60 : 0)) / 24);
        for (int i = 0; i < (intro != null ? 10 : 7); i++)
        {
            int index = firstProp + i;
            float z = distance - index * 24 - 10;
            if (z > (intro != null ? 60 : 4) || z < -135) continue;
            Draw("lamp", new Vector3(-4.6f, .16f, z));
            if (MathF.Abs(z - 7 - clockZ) > 9 && MathF.Abs(z - 7 - rathausZ) > 42)
                Draw("tree", new Vector3(4.65f, .16f, z - 7), scale: .60f);
            if (index % 2 == 0 && MathF.Abs(z - 8 - rathausZ) > 43)
            {
                Draw("table", new Vector3(-5.1f, .16f, z - 8));
                Draw("chair", new Vector3(-5.1f, .16f, z - 9));
            }
        }
        // Broad paved forecourt exposes the Rathaus front instead of hiding it behind shops.
        // At 55% scale its rotated footprint is x=-104.7..-29.3, z=centre +/-35.4.
        if (rathausZ > -260 && rathausZ < 115)
        {
            Draw("plaza", new Vector3(230, 0, rathausZ), MathF.PI, dimensions: new Vector3(60, 1, 4.5f));
            Draw("rathaus", new Vector3(-70, .16f, rathausZ), MathF.PI / 2, scale: .55f);
            // Enclose the forecourt: the street opening must reveal a city block,
            // rather than the clear colour beyond the edge of the paving.
            for (int bay = 0; bay < 18; bay++)
            {
                // Butt against the street row; recess the far ends into the rear
                // corner by 0.4 m so the model's recessed wall panels also meet.
                const float width = (114.5f - 6.55f) / 18;
                float x = -6.55f - (bay + .5f) * width;
                SquareFacade(new Vector3(x, .16f, rathausZ - 45), 0, bay % 3 == 0, width);
                SquareFacade(new Vector3(x, .16f, rathausZ + 45), MathF.PI, bay % 3 == 1, width);
            }
            for (int bay = -7; bay <= 7; bay++)
                SquareFacade(new Vector3(-114.5f, .16f, rathausZ + bay * 6), MathF.PI / 2,
                    bay % 3 == 0);
            foreach (int end in new[] { -1, 1 })
            {
                Draw("bench", new Vector3(-9, .16f, rathausZ + end * 29), -MathF.PI / 2);
                Draw("planter", new Vector3(-10, .16f, rathausZ + end * 35));
                Draw("tree", new Vector3(-12, .16f, rathausZ + end * 39), scale: .8f);
            }
        }
        // Kröpcke clock has its own square beside the opening action.
        if (clockZ > -160 && clockZ < 70)
        {
            Draw("plaza", new Vector3(-21.89f, 0, clockZ), dimensions: new Vector3(7, 1, 1.54f));
            Draw("clock", new Vector3(8.2f, .16f, clockZ));
            Draw("bench", new Vector3(11, .16f, clockZ + 5), -MathF.PI / 2);
            Draw("planter", new Vector3(11, .16f, clockZ - 5));
            // Butt wings against the street row and recess the far ends into
            // the rear corners by half the wall depth, sealing recessed panels.
            for (int bay = -2; bay <= 2; bay++)
                SquareFacade(new Vector3(18.15f, .16f, clockZ + bay * 6), -MathF.PI / 2,
                    bay % 3 == 0);
            for (int bay = 0; bay < 2; bay++)
            {
                float x = 9.45f + bay * 5.8f;
                SquareFacade(new Vector3(x, .16f, clockZ - 15), 0, width: 5.8f);
                SquareFacade(new Vector3(x, .16f, clockZ + 15), MathF.PI, width: 5.8f);
            }
        }
        if (intro != null && introSample != null)
        {
            _intro ??= new ConeIntroRenderer(_assetsRoot, intro.Scene);
            foreach (var draw in _intro.Build(introSample, Matrix4.CreateTranslation(stageOffset)))
            { _frameDraws.Add(draw); DrawCount++; }
            Flush();
            return;
        }
        foreach (var item in state.WorldObjects)
        {
            if (!item.Active || item.Z > 4 || item.Z < -140) continue;
            bool coin = item.Kind == ObjectKind.Coin;
            Draw(item.Kind.ToString(), new Vector3(item.X, coin ? 1.0f : 0, item.Z), coin ? time * 2.7f : 0);
        }
        var player = new Vector3(state.PlayerX, state.PlayerY, 0);
        if(state.VanCrash is {} activeCrash)
        {
            // Flush the existing shadowed city/van before adding the road opening;
            // Flush clears the framebuffer, so scene geometry must follow it.
            Flush();
            _vanCrash.RenderGround(activeCrash,_renderer,_camera);
            _vanCrash.RenderActors(activeCrash,_renderer,_camera,(key,matrix)=>DrawTransform(key,matrix,immediate:true));
            DrawCount+=_vanCrash.DrawCount;
            return;
        }
        Draw("scooter", player, wheelAngle: -distance / .127f);
        Draw(state.IsDucking ? "duck" : "ride", player);
        if (state.Phase != RunPhase.Ready)
        {
            if (_intro != null)
            {
                var draw = _intro.Pursuer(time, distance, state.PlayerX, state.PursuitRemaining > 0 || state.Phase == RunPhase.Caught);
                _frameDraws.Add(draw); DrawCount++;
            }
            else
            {
                int frame = (int)(time * 5) % 4;
                Draw($"officer{frame}", new Vector3(state.PlayerX + .75f, 0, 14), MathF.PI);
            }
        }
        if (_intro != null && state.Phase != RunPhase.Ready && distance < 10)
        {
            var cone = _intro.SettledCone(Matrix4.CreateTranslation(0, 0, distance));
            _frameDraws.Add(cone); DrawCount++;
        }
        Flush();
    }

    private void Flush()
    {
        _shadows ??= new MapShadowPass();
        var focus = new Vector3(0, 0, _camera.Target.Z + 10);
        _shadows.Render(_renderer, _camera, focus, _frameDraws.Select(d => (d.Mesh, d.Transform)));
        foreach (var material in _frameDraws.Select(d => d.Material).Distinct())
        {
            material.ShadowsEnabled = true;
            material.ShadowTexture = _shadows.DepthTexture;
            material.LightSpace = _shadows.LightSpace;
            material.SunDirection = MapShadowPass.SunDirection;
        }
        _renderer.Clear();
        var opaque=_frameDraws.Where(d=>d.Material.Opacity>=.999f).ToArray();
        foreach (var draw in opaque) _renderer.Draw(draw.Mesh, draw.Material, draw.Transform, _camera);
        var transparent=_frameDraws.Where(d=>d.Material.Opacity<.999f)
            .OrderByDescending(d=>Vector3.DistanceSquared(d.Transform.ExtractTranslation(),_camera.Position)).ToArray();
        if(transparent.Length>0)
        {
            GL.Enable(EnableCap.Blend);
            GL.BlendFunc(BlendingFactor.SrcAlpha,BlendingFactor.OneMinusSrcAlpha);
            GL.DepthMask(false);
            foreach(var draw in transparent)_renderer.Draw(draw.Mesh,draw.Material,draw.Transform,_camera);
            GL.DepthMask(true);
            GL.Disable(EnableCap.Blend);
        }
    }

    public void Dispose()
    {
        if (_disposed) return;
        _disposed = true;
        _vanCrash.Dispose();
        _intro?.Dispose();
        _shadows?.Dispose();
        foreach (var mesh in _meshes.Values) mesh.Dispose();
        foreach (var surface in _textures.Values) surface.Texture.Dispose();
        _renderer.Dispose();
        _meshes.Clear();
        _textures.Clear();
        _models.Clear();
    }
}
