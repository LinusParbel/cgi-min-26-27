using Engine.Materials;
using Engine.OpenGL;
using OpenTK.Mathematics;

namespace Engine.Scenes;

// A node of the scene graph. Every node has a transformation relative to its parent
// (position, rotation, scale) and can have children: when the parent moves, its children move with it
// (a wheel on a car, a weapon in a hand, a moon around a planet).
// A node can be drawn if it has a mesh and a material; nodes without them only group their children.
public class SceneNode
{
    private readonly List<SceneNode> _children = new();

    public SceneNode(string name = "Node", Mesh? mesh = null, Material? material = null)
    {
        Name = name;
        Mesh = mesh;
        Material = material;
    }

    public string Name { get; set; }

    // What is drawn (both optional)
    public Mesh? Mesh { get; set; }
    public Material? Material { get; set; }

    // Transformation relative to the parent
    public Vector3 Position { get; set; } = Vector3.Zero;
    public Quaternion Rotation { get; set; } = Quaternion.Identity;
    public Vector3 Scale { get; set; } = Vector3.One;

    // Static nodes never move after Scene.BuildOctree(); they are sorted into the octree of the scene.
    // Their parents must not move either.
    public bool IsStatic { get; set; }

    public SceneNode? Parent { get; private set; }
    public IReadOnlyList<SceneNode> Children => _children;

    // OpenTK row vectors: first scale, then rotate, then move.
    public Matrix4 LocalMatrix =>
        Matrix4.CreateScale(Scale) * Matrix4.CreateFromQuaternion(Rotation) * Matrix4.CreateTranslation(Position);

    // Local matrix * world matrix of the parent; calculated by Scene.Update().
    public Matrix4 WorldMatrix { get; private set; } = Matrix4.Identity;

    // Position in world space (last row of the world matrix)
    public Vector3 WorldPosition => WorldMatrix.Row3.Xyz;

    // Radius of the bounding sphere in world space: the mesh radius grows with the scale.
    public float WorldBoundingRadius
    {
        get
        {
            if (Mesh is null) return 0.0f;
            Matrix4 m = WorldMatrix;
            float scale = MathF.Max(m.Row0.Xyz.Length, MathF.Max(m.Row1.Xyz.Length, m.Row2.Xyz.Length));
            return Mesh.BoundingRadius * scale;
        }
    }

    public bool IsDrawable => Mesh is not null && Material is not null;

    public SceneNode AddChild(SceneNode child)
    {
        ArgumentNullException.ThrowIfNull(child);
        if (child.Parent is not null)
            throw new InvalidOperationException($"'{child.Name}' already has a parent.");
        for (SceneNode? n = this; n is not null; n = n.Parent)
            if (n == child) throw new InvalidOperationException("A node cannot be its own child.");

        child.Parent = this;
        _children.Add(child);
        return child;
    }

    public void RemoveChild(SceneNode child)
    {
        ArgumentNullException.ThrowIfNull(child);
        if (_children.Remove(child)) child.Parent = null;
    }

    // Calculates the world matrix of this node and all children (top to bottom).
    internal void UpdateWorldMatrix(Matrix4 parentWorldMatrix)
    {
        WorldMatrix = LocalMatrix * parentWorldMatrix;
        foreach (SceneNode child in _children)
            child.UpdateWorldMatrix(WorldMatrix);
    }
}
