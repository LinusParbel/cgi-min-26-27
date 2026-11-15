using OpenTK.Mathematics;

namespace Engine.Scenes;

// The scene graph: all nodes hang (directly or indirectly) below Root.
// Per frame in Update:
//   1. move nodes (Position, Rotation, Scale),
//   2. scene.Update()                      calculates the world matrices from top to bottom,
//   3. scene.CollectVisible(frustum, ...)  fills a RenderList with the visible nodes.
// Render then only draws the RenderList.
//
// Static nodes (IsStatic) can be sorted into an octree once with BuildOctree(); after that they are
// found by the octree query instead of testing each of them against the frustum.
public sealed class Scene
{
    private readonly List<SceneNode> _octreeResults = new();
    private Octree<SceneNode>? _octree;

    public SceneNode Root { get; } = new("Root");

    // Use the octree for the static nodes (if built); false = test every node, for comparison.
    public bool UseOctree { get; set; } = true;

    // Statistics of the last CollectVisible call
    public int VisibilityTests { get; private set; }
    public int DrawableNodeCount { get; private set; }

    public SceneNode Add(SceneNode node) => Root.AddChild(node);

    // Calculates the world matrices of all nodes.
    public void Update() => Root.UpdateWorldMatrix(Matrix4.Identity);

    // Sorts all static, drawable nodes into an octree with the given bounds.
    // Static nodes must not move afterwards (call BuildOctree again if they do).
    public void BuildOctree(Vector3 min, Vector3 max, int maxDepth = 5)
    {
        Update();
        _octree = new Octree<SceneNode>(min, max, maxDepth);
        foreach (SceneNode node in AllNodes())
        {
            if (node.IsStatic && node.IsDrawable)
                _octree.Insert(node, node.WorldPosition, node.WorldBoundingRadius);
        }
    }

    // Fills the render list with all visible, drawable nodes; transparent ones are sorted back to front.
    public void CollectVisible(Frustum frustum, Vector3 cameraPosition, RenderList renderList)
    {
        ArgumentNullException.ThrowIfNull(frustum);
        ArgumentNullException.ThrowIfNull(renderList);

        renderList.Clear();
        int tests = 0;
        int drawable = 0;
        bool octree = UseOctree && _octree is not null;

        // nodes that are not in the octree: one sphere test each
        foreach (SceneNode node in AllNodes())
        {
            if (!node.IsDrawable) continue;
            drawable++;
            if (octree && node.IsStatic) continue;   // found by the octree query below

            tests++;
            if (frustum.SphereInFrustum(node.WorldPosition, node.WorldBoundingRadius))
                renderList.Add(node);
        }

        // static nodes: the octree only tests the areas that are in view
        if (octree)
        {
            _octreeResults.Clear();
            tests += _octree!.Query(frustum, _octreeResults);
            foreach (SceneNode node in _octreeResults) renderList.Add(node);
        }

        renderList.SortTransparent(cameraPosition);
        VisibilityTests = tests;
        DrawableNodeCount = drawable;
    }

    // All nodes below Root, depth first.
    public IEnumerable<SceneNode> AllNodes()
    {
        var stack = new Stack<SceneNode>();
        stack.Push(Root);
        while (stack.Count > 0)
        {
            SceneNode node = stack.Pop();
            if (node != Root) yield return node;
            for (int i = node.Children.Count - 1; i >= 0; i--) stack.Push(node.Children[i]);
        }
    }
}
