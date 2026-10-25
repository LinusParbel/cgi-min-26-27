using System.Text.Json;

namespace RunnerGame.Rendering;

public sealed record SceneProp(string Kind, float X, float Z, float Y, float YawDegrees, float Scale);
public sealed record ExtraSceneManifest(string Key, string Manifest);

/// <summary>Optional map decoration metadata; parsing needs no graphics context.</summary>
public static class ScenePropMetadata
{
    public static IReadOnlyList<SceneProp> ReadProps(JsonElement map)
    {
        if (!map.TryGetProperty("sceneProps", out var props)) return [];
        var result = new List<SceneProp>();
        foreach (var prop in props.EnumerateArray())
        {
            string? kind = prop.GetProperty("kind").GetString();
            if (kind is not ("tree" or "bench" or "planter" or "lamp" or "rack"))
                throw new InvalidDataException($"Unknown scene prop kind: {kind}");
            float scale = Optional(prop, "scale", 1);
            if (scale <= 0) throw new InvalidDataException("Scene prop scale must be positive.");
            result.Add(new(kind, Number(prop.GetProperty("x")), Number(prop.GetProperty("z")),
                Optional(prop, "y", 0), Optional(prop, "yaw", 0), scale));
        }
        return result;
    }

    public static IReadOnlyList<ExtraSceneManifest> ReadExtras(JsonElement map)
    {
        if (!map.TryGetProperty("extraManifests", out var extras)) return [];
        var result = new List<ExtraSceneManifest>();
        var names = new HashSet<string>(StringComparer.Ordinal);
        foreach (var extra in extras.EnumerateArray())
        {
            string? key = extra.GetProperty("key").GetString();
            string? manifest = extra.GetProperty("manifest").GetString();
            if (string.IsNullOrWhiteSpace(key) || !names.Add(key) || string.IsNullOrWhiteSpace(manifest))
                throw new InvalidDataException("Extra manifests require unique nonempty keys and manifest references.");
            result.Add(new(key, manifest));
        }
        return result;
    }

    private static float Optional(JsonElement element, string name, float fallback) =>
        element.TryGetProperty(name, out var value) ? Number(value) : fallback;
    private static float Number(JsonElement element)
    {
        if (element.ValueKind != JsonValueKind.Number || !element.TryGetSingle(out float number) || !float.IsFinite(number))
            throw new InvalidDataException("Scene prop coordinates, yaw and scale must be finite numbers.");
        return number;
    }
}
