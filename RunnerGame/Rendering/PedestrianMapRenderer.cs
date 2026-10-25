using System.Text.Json;
using Engine;
using Engine.Geometry.Loaders;
using Engine.OpenGL;
using OpenTK.Graphics.OpenGL4;
using OpenTK.Mathematics;
using RunnerGame.Gameplay;
using RunnerGame.Materials.RunnerLit;

namespace RunnerGame.Rendering;

/// <summary>Geographic LoD2 blockout and provisional pedestrian route in one fixed world frame.</summary>
public sealed class PedestrianMapRenderer : IRunnerScene
{
    private sealed record Part(string Name, Mesh Mesh, RunnerLitMaterial Material, Vector3 Pivot);
    private readonly Dictionary<string, Mesh> meshes = new(StringComparer.OrdinalIgnoreCase);
    private readonly Dictionary<string, (Texture Texture, RunnerLitMaterial Material)> surfaces = new(StringComparer.OrdinalIgnoreCase);
    private readonly Dictionary<string, Part[]> models = new(StringComparer.Ordinal);
    private readonly OpenGlRenderer renderer;
    private MapShadowPass? shadows;
    private readonly List<(Part Part, Matrix4 Transform)> frameDraws = [];
    public string ShadowDiagnostics => shadows?.Diagnostics ?? "shadows unavailable";
    private readonly Camera camera = new(new(0, 3, 6), new(0, 1, -12))
        { NearPlane = .08f, FarPlane = 800, FieldOfViewDegrees = 62 };
    private readonly RoutePath route;
    private readonly float groundY;
    private readonly Vector3 clock;
    private readonly IReadOnlyList<SceneProp> sceneProps;
    private readonly IReadOnlyList<ExtraSceneManifest> extraManifests;
    private float? inspectionDistance;
    private bool disposed;
    public int MeshCount => meshes.Count;
    public int TextureCount => surfaces.Count;
    public int DrawCount { get; private set; }
    public string Title { get; }
    public float RouteLength => route.Length;
    public bool Overview { get; set; }
    private float inspectionYaw, inspectionPitch = 20, inspectionZoom = 14;
    public float InspectionYawDegrees
    {
        get => inspectionYaw;
        set => inspectionYaw = float.IsFinite(value) ? value : throw new ArgumentOutOfRangeException(nameof(value));
    }
    public float InspectionPitchDegrees
    {
        get => inspectionPitch;
        set => inspectionPitch = float.IsFinite(value) ? Math.Clamp(value, -10, 75) : throw new ArgumentOutOfRangeException(nameof(value));
    }
    public float InspectionZoom
    {
        get => inspectionZoom;
        set => inspectionZoom = float.IsFinite(value) ? Math.Clamp(value, 3, 80) : throw new ArgumentOutOfRangeException(nameof(value));
    }
    public bool EnableShadows { get; set; } = true;
    public float? InspectionDistance
    {
        get => inspectionDistance;
        set
        {
            if (value is float distance && !float.IsFinite(distance))
                throw new ArgumentOutOfRangeException(nameof(value), "Inspection distance must be finite.");
            inspectionDistance = value is float finite ? Math.Clamp(finite, 0, RouteLength) : null;
        }
    }

    public PedestrianMapRenderer(string assetsRoot, string mapFolder)
    {
        renderer = new OpenGlRenderer { LightPosition = new(-20, 145, 15) };
        try
        {
            using var metadata = JsonDocument.Parse(File.ReadAllText(ModelManifest.Resolve(mapFolder, "map.json")));
            var map = metadata.RootElement;
            if (map.TryGetProperty("shadows", out var shadowSetting))
            {
                if (shadowSetting.ValueKind is not (JsonValueKind.True or JsonValueKind.False))
                    throw new InvalidDataException("Map shadows must be a boolean.");
                EnableShadows = shadowSetting.GetBoolean();
            }
            string Reference(string property) => ModelManifest.Resolve(mapFolder, map.GetProperty(property).GetString()!);
            groundY = Finite(map.GetProperty("groundY"));
            var location = map.GetProperty("clock");
            clock = new(Finite(location.GetProperty("x")), groundY, Finite(location.GetProperty("z")));
            Title = map.GetProperty("title").GetString() ?? "Hannover pedestrian blockout";
            route = RoutePath.Load(Reference("route"));
            sceneProps = ScenePropMetadata.ReadProps(map);
            extraManifests = ScenePropMetadata.ReadExtras(map);
            Manifest("city", Reference("cityManifest"));
            Manifest("ground", Reference("groundManifest"));
            foreach (var extra in extraManifests)
                Manifest("extra:" + extra.Key, ModelManifest.Resolve(mapFolder, extra.Manifest));
            string root = Path.Combine(Path.GetFullPath(assetsRoot), "Models");
            void Asset(string key, string file) => Manifest(key, ModelManifest.Resolve(root, file));
            Asset("scooter", "Fahrzeug/ScooterVoi/VEH_ScooterVoi_parts.json");
            Asset("ride", "Charakter/ScooterRider/CHR_ScooterRider_ride_parts.json");
            Asset("duck", "Charakter/ScooterRider/CHR_ScooterRider_duck_parts.json");
            Asset("Coin", "Pickup/CityToken/PROP_CityToken_parts.json");
            Asset("HighBarrier", "Baustelle/DuckBarrier/PROP_DuckBarrier_parts.json");
            Asset("Planter", "Umgebung/StreetFurniture/PROP_StreetFurniture_planter_parts.json");
            Asset("clock", "Wahrzeichen/KroepckeUhr/PRP_KroepckeUhr_parts.json");
            foreach (string kind in sceneProps.Select(p => p.Kind).Distinct())
            {
                string file = kind switch
                {
                    "tree" => "Umgebung/StreetTree/ENV_StreetTree_parts.json",
                    "rack" => "Umgebung/PavementProps/PROP_Pavement_parts.json",
                    _ => $"Umgebung/StreetFurniture/PROP_StreetFurniture_{kind}_parts.json"
                };
                Manifest("prop:" + kind, ModelManifest.Resolve(root, file), kind == "rack" ? "rack" : null);
            }
            Single("Cone", root, "Baustelle/Leitkegel/PROP_Leitkegel_75");
            Single("Bin", root, "Mull/Tonne/PROP_WheelieBin_120L_restmuell");
            string officers = Path.Combine(root, "Charakter/Ordnungsamt");
            for (int i = 0; i < 4; i++)
                models.Add($"officer{i}", [Load(new("officer",
                    ModelManifest.Resolve(officers, $"CHR_Ordnungsamt_run_{1 + i * 10:00}.obj"),
                    ModelManifest.Resolve(officers, "CHR_Ordnungsamt.png"), Vector3.Zero))]);
            GL.ClearColor(.55f, .62f, .70f, 1);
            shadows = new MapShadowPass();
        }
        catch { Dispose(); throw; }
    }

    private static float Finite(JsonElement value)
    {
        float number = value.GetSingle();
        return float.IsFinite(number) ? number : throw new InvalidDataException("Map coordinates must be finite.");
    }

    private void Manifest(string key, string path, string? selected = null)
    {
        var parts = ModelManifest.Read(path);
        if (parts.Count == 0) throw new InvalidDataException($"Empty model manifest: {path}");
        var chosen = parts.Where(p => selected == null || p.Name == selected).ToArray();
        if (chosen.Length == 0) throw new InvalidDataException($"Missing model part {selected}: {path}");
        models.Add(key, chosen.Select(Load).ToArray());
    }

    private void Single(string key, string root, string basename) => models.Add(key,
        [Load(new(key, ModelManifest.Resolve(root, basename + ".obj"),
            ModelManifest.Resolve(root, basename + ".png"), Vector3.Zero))]);

    private Part Load(ModelPart part)
    {
        if (!meshes.TryGetValue(part.ObjPath, out var mesh))
        {
            mesh = new Mesh(ObjLoader.Load(part.ObjPath));
            meshes.Add(part.ObjPath, mesh);
        }
        if (!surfaces.TryGetValue(part.TexturePath, out var surface))
        {
            var texture = Texture.FromFile(part.TexturePath);
            surface = (texture, new RunnerLitMaterial(texture));
            surfaces.Add(part.TexturePath, surface);
        }
        return new(part.Name, mesh, surface.Material, part.Pivot);
    }

    public void Resize(int width, int height) => renderer.Resize(width, height);

    private void Draw(string key, Vector3 position, float yaw = 0, float wheelAngle = 0, float scale = 1)
    {
        var transform = Matrix4.CreateScale(scale) * Matrix4.CreateRotationY(yaw) * Matrix4.CreateTranslation(position);
        foreach (var part in models[key])
        {
            var animation = part.Name.StartsWith("wheel", StringComparison.Ordinal)
                ? Matrix4.CreateRotationX(wheelAngle) : Matrix4.Identity;
            frameDraws.Add((part, animation * Matrix4.CreateTranslation(part.Pivot) * transform));
        }
    }

    private Vector3 Position(RouteSample sample, float lateral = 0, float elevation = 0) =>
        new(sample.X + sample.RightX * lateral, groundY + elevation, sample.Z + sample.RightZ * lateral);
    private static float Yaw(RouteSample sample) => MathF.Atan2(-sample.ForwardX, -sample.ForwardZ);

    public void Render(RunSimulation state)
    {
        ObjectDisposedException.ThrowIf(disposed, this);
        DrawCount = 0;
        frameDraws.Clear();
        bool inspecting = InspectionDistance.HasValue && state.Phase is RunPhase.Ready or RunPhase.Paused;
        float distance = inspecting ? InspectionDistance!.Value : state.Distance;
        var sample = route.Sample(distance);
        var behind = route.Sample(distance - 6);
        var ahead = route.Sample(distance + 12);
        // A stable chase camera keeps steering readable through the geographic bends.
        if (Overview)
        {
            float minX = float.PositiveInfinity, maxX = float.NegativeInfinity;
            float minZ = float.PositiveInfinity, maxZ = float.NegativeInfinity;
            for (int i = 0; i <= 64; i++)
            {
                var point = route.Sample(route.Length * i / 64);
                minX = Math.Min(minX, point.X); maxX = Math.Max(maxX, point.X);
                minZ = Math.Min(minZ, point.Z); maxZ = Math.Max(maxZ, point.Z);
            }
            var center = new Vector3((minX + maxX) / 2, groundY, (minZ + maxZ) / 2);
            float span = Math.Max(120, Math.Max(maxX - minX, maxZ - minZ));
            camera.FarPlane = 3000;
            camera.LookAt(center + new Vector3(0, span * 1.15f, span * .65f), center);
        }
        else if (inspecting)
        {
            camera.FarPlane = 800;
            float yaw = MathHelper.DegreesToRadians(InspectionYawDegrees);
            float pitch = MathHelper.DegreesToRadians(InspectionPitchDegrees);
            float backX = -sample.ForwardX, backZ = -sample.ForwardZ;
            var backward = new Vector3(backX * MathF.Cos(yaw) + backZ * MathF.Sin(yaw), 0,
                -backX * MathF.Sin(yaw) + backZ * MathF.Cos(yaw));
            var target = Position(sample, elevation: 1.2f);
            camera.LookAt(target + backward * (InspectionZoom * MathF.Cos(pitch)) +
                Vector3.UnitY * (InspectionZoom * MathF.Sin(pitch)), target);
        }
        else
        {
            camera.FarPlane = 800;
            camera.LookAt(Position(behind, elevation: 3), Position(ahead, elevation: 1.2f));
        }
        foreach (var surface in surfaces.Values)
        {
            surface.Material.FogStart = Overview ? 2000 : 80;
            surface.Material.FogEnd = Overview ? 3000 : 350;
        }
        Draw("city", Vector3.Zero);
        // Ground vertices already contain the authored flat blockout datum; not survey terrain.
        Draw("ground", Vector3.Zero);
        foreach (var extra in extraManifests) Draw("extra:" + extra.Key, Vector3.Zero);
        foreach (var prop in sceneProps)
            Draw("prop:" + prop.Kind, new Vector3(prop.X, groundY + prop.Y, prop.Z),
                MathHelper.DegreesToRadians(prop.YawDegrees), scale: prop.Scale);
        Draw("clock", clock);
        foreach (var item in state.WorldObjects)
        {
            if (inspecting || !item.Active || item.Z > 8 || item.Z < -160) continue;
            string key = item.Kind.ToString();
            if (!models.ContainsKey(key)) continue;
            var placement = route.Sample(state.Distance - item.Z);
            bool coin = item.Kind == ObjectKind.Coin;
            Draw(key, Position(placement, item.X, coin ? 1 : 0),
                coin ? state.ElapsedTime * 2.7f : Yaw(placement));
        }
        var player = Position(sample, inspecting ? 0 : state.PlayerX, inspecting ? 0 : state.PlayerY);
        Draw("scooter", player, Yaw(sample), -distance / .127f);
        Draw(!inspecting && state.IsDucking ? "duck" : "ride", player, Yaw(sample));
        if (!inspecting && (state.PursuitRemaining > 0 || state.Phase == RunPhase.Caught))
        {
            var officer = route.Sample(state.Distance - 2);
            Draw($"officer{(int)(state.ElapsedTime * 5) % 4}",
                Position(officer, state.PlayerX + .75f), Yaw(officer) + MathF.PI);
        }
        if (!Overview && EnableShadows)
        {
            var focus = route.Sample(distance + 24);
            shadows!.Render(renderer, camera, Position(focus), frameDraws.Select(d => (d.Part.Mesh, d.Transform)));
        }
        foreach (var surface in surfaces.Values)
        {
            surface.Material.ShadowsEnabled = !Overview && EnableShadows;
            surface.Material.ShadowTexture = shadows!.DepthTexture;
            surface.Material.LightSpace = shadows.LightSpace;
            surface.Material.SunDirection = MapShadowPass.SunDirection;
        }
        renderer.Clear();
        foreach (var draw in frameDraws)
        {
            renderer.Draw(draw.Part.Mesh, draw.Part.Material, draw.Transform, camera);
            DrawCount++;
        }
    }

    public void Dispose()
    {
        if (disposed) return;
        disposed = true;
        shadows?.Dispose();
        foreach (var mesh in meshes.Values) mesh.Dispose();
        foreach (var surface in surfaces.Values) surface.Texture.Dispose();
        renderer.Dispose();
        meshes.Clear(); surfaces.Clear(); models.Clear(); frameDraws.Clear();
    }
}
