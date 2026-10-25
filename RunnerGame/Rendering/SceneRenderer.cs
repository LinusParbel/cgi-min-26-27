using Engine;
using Engine.Geometry.Loaders;
using Engine.OpenGL;
using OpenTK.Graphics.OpenGL4;
using OpenTK.Mathematics;
using RunnerGame.Gameplay;
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
        { NearPlane = .08f, FarPlane = 150, FieldOfViewDegrees = 58 };
    private bool _disposed;
    public int MeshCount => _meshes.Count;
    public int TextureCount => _textures.Count;
    public int DrawCount { get; private set; }

    /// <param name="assetsRoot">The installed Assets directory containing Models.</param>
    public SceneRenderer(string assetsRoot)
    {
        _renderer = new OpenGlRenderer { LightPosition = new Vector3(-20, 45, 15) };
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

    private void Draw(string key, Vector3 position, float yaw = 0, float wheelAngle = 0, float scale = 1)
    {
        var transform = Matrix4.CreateScale(scale) * Matrix4.CreateRotationY(yaw) * Matrix4.CreateTranslation(position);
        foreach (var part in _models[key])
        {
            var rotation = part.Name.StartsWith("wheel", StringComparison.Ordinal)
                ? Matrix4.CreateRotationX(wheelAngle) : Matrix4.Identity;
            _renderer.Draw(part.Mesh, part.Material,
                rotation * Matrix4.CreateTranslation(part.Pivot) * transform, _camera);
            DrawCount++;
        }
    }

    public void Render(RunSimulation state)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        DrawCount = 0;
        _renderer.Clear();
        float distance = (float)state.Distance;
        float time = (float)state.ElapsedTime;
        float streetOffset = distance % 20;
        float clockZ = distance % 120 - 110;
        for (int i = 0; i < 10; i++)
        {
            float z = 20 - i * 20 + streetOffset;
            if (z <= 20) Draw("street", new Vector3(0, 0, z));
        }
        // A facade bay is exactly six metres wide. Rotate it onto each pavement edge.
        int firstBay = (int)MathF.Floor(distance / 6);
        for (int i = 0; i < 25; i++)
        {
            int bay = firstBay + i;
            float z = distance - bay * 6;
            if (z > 5 || z < -140) continue;
            foreach (int side in new[] { -1, 1 })
            {
                // Reserve a small paved square around the wider clock pedestal.
                if (side == 1 && MathF.Abs(z - clockZ) < 9) continue;
                float yaw = -side * MathF.PI / 2;
                Draw("shop", new Vector3(side * 6.15f, .16f, z), yaw);
                Draw((bay + (side == 1 ? 1 : 0)) % 3 == 0 ? "brick" : "sandstone",
                    new Vector3(side * 6.15f, 3.36f, z), yaw);
            }
        }
        int firstProp = (int)MathF.Floor(distance / 24);
        for (int i = 0; i < 7; i++)
        {
            int index = firstProp + i;
            float z = distance - index * 24 - 10;
            if (z > 4 || z < -135) continue;
            Draw("lamp", new Vector3(-4.6f, .16f, z));
            if (MathF.Abs(z - 7 - clockZ) > 5)
                Draw("tree", new Vector3(4.65f, .16f, z - 7), scale: .60f);
            if (index % 2 == 0)
            {
                Draw("table", new Vector3(-5.1f, .16f, z - 8));
                Draw("chair", new Vector3(-5.1f, .16f, z - 9));
            }
        }
        // Clock occupies a pavement bay and recycles with a long city block.
        if (clockZ < 4)
        {
            Draw("plaza", new Vector3(2.0f, 0, clockZ));
            Draw("clock", new Vector3(5.05f, .16f, clockZ));
        }
        foreach (var item in state.WorldObjects)
        {
            if (!item.Active || item.Z > 4 || item.Z < -140) continue;
            bool coin = item.Kind == ObjectKind.Coin;
            Draw(item.Kind.ToString(), new Vector3(item.X, coin ? 1.0f : 0, item.Z), coin ? time * 2.7f : 0);
        }
        var player = new Vector3(state.PlayerX, state.PlayerY, 0);
        Draw("scooter", player, wheelAngle: -distance / .127f);
        Draw(state.IsDucking ? "duck" : "ride", player);
        if (state.PursuitRemaining > 0 || state.Phase == RunPhase.Caught)
        {
            int frame = (int)(time * 5) % 4;
            Draw($"officer{frame}", new Vector3(state.PlayerX + .75f, 0, 2.0f), MathF.PI);
        }
    }

    public void Dispose()
    {
        if (_disposed) return;
        _disposed = true;
        foreach (var mesh in _meshes.Values) mesh.Dispose();
        foreach (var surface in _textures.Values) surface.Texture.Dispose();
        _renderer.Dispose();
        _meshes.Clear();
        _textures.Clear();
        _models.Clear();
    }
}
