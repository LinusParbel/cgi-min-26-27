using OpenTK.Mathematics;

namespace Engine.Scenes;

// The visible nodes of one frame, collected by Scene.CollectVisible() in Update and drawn in Render:
// first all opaque nodes (order does not matter), then all transparent nodes from back to front.
public sealed class RenderList
{
    private readonly List<SceneNode> _opaque = new();
    private readonly List<SceneNode> _transparent = new();

    public IReadOnlyList<SceneNode> Opaque => _opaque;
    public IReadOnlyList<SceneNode> Transparent => _transparent;

    public int Count => _opaque.Count + _transparent.Count;

    public void Clear()
    {
        _opaque.Clear();
        _transparent.Clear();
    }

    public void Add(SceneNode node)
    {
        ArgumentNullException.ThrowIfNull(node);
        if (!node.IsDrawable) return;
        if (node.Material!.IsTransparent) _transparent.Add(node);
        else _opaque.Add(node);
    }

    // Transparent objects are blended with what is already on the screen, so the farthest one
    // is drawn first and the nearest one last. Has to be done every frame, the camera moves.
    public void SortTransparent(Vector3 cameraPosition)
    {
        _transparent.Sort((a, b) =>
            Vector3.DistanceSquared(b.WorldPosition, cameraPosition)
                .CompareTo(Vector3.DistanceSquared(a.WorldPosition, cameraPosition)));
    }
}
