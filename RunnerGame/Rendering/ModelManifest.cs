using System.Text.Json;
using OpenTK.Mathematics;

namespace RunnerGame.Rendering;

/// <summary>Installed asset metadata. Reading and validation require no graphics context.</summary>
public sealed record ModelPart(string Name, string ObjPath, string TexturePath, Vector3 Pivot);

public static class ModelManifest
{
    public static string Resolve(string root, string relative)
    {
        if (string.IsNullOrWhiteSpace(relative) || Path.IsPathRooted(relative))
            throw new InvalidDataException("Asset references must be relative paths.");
        string directory = Path.GetFullPath(root);
        string path = Path.GetFullPath(Path.Combine(directory, relative));
        if (!path.StartsWith(Path.TrimEndingDirectorySeparator(directory) + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException("Asset reference escapes its directory.");
        if (!File.Exists(path)) throw new FileNotFoundException("Installed asset is missing.", path);
        return path;
    }

    public static Vector3 EnginePivot(JsonElement coordinates)
    {
        var values = coordinates.EnumerateArray().Select(x => x.GetSingle()).ToArray();
        if (values.Length != 3 || values.Any(x => !float.IsFinite(x)))
            throw new InvalidDataException("Pivot must contain three finite coordinates.");
        return new(values[0], values[2], -values[1]);
    }

    public static IReadOnlyList<ModelPart> Read(string manifest)
    {
        using var document = JsonDocument.Parse(File.ReadAllText(manifest));
        var root = document.RootElement;
        string directory = Path.GetDirectoryName(Path.GetFullPath(manifest))!;
        string texture = Resolve(directory, root.GetProperty("texture").GetString()!);
        return root.GetProperty("parts").EnumerateArray().Select(part => new ModelPart(
            part.GetProperty("name").GetString()!, Resolve(directory, part.GetProperty("obj").GetString()!),
            texture, EnginePivot(part.GetProperty("pivot")))).ToArray();
    }
}
