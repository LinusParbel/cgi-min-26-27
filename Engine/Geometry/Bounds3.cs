using OpenTK.Mathematics;

namespace Engine.Geometry;

/// <summary>Conservative axis-aligned bounds, independent of graphics state.</summary>
public readonly record struct Bounds3(Vector3 Min, Vector3 Max)
{
    public Vector3 Center => (Min + Max) * .5f;
    public Vector3 Extents => (Max - Min) * .5f;

    public static Bounds3 FromVertices(ReadOnlySpan<Vertex> vertices)
    {
        if (vertices.IsEmpty) throw new ArgumentException("Bounds require vertices.", nameof(vertices));
        Vector3 min = vertices[0].Position, max = min;
        foreach (ref readonly var vertex in vertices)
        {
            min = Vector3.ComponentMin(min, vertex.Position);
            max = Vector3.ComponentMax(max, vertex.Position);
        }
        return new(min, max);
    }

    public Bounds3 Transform(Matrix4 matrix)
    {
        var c = Vector3.TransformPosition(Center, matrix);
        var e = Extents;
        var transformed = new Vector3(
            Math.Abs(matrix.M11)*e.X + Math.Abs(matrix.M21)*e.Y + Math.Abs(matrix.M31)*e.Z,
            Math.Abs(matrix.M12)*e.X + Math.Abs(matrix.M22)*e.Y + Math.Abs(matrix.M32)*e.Z,
            Math.Abs(matrix.M13)*e.X + Math.Abs(matrix.M23)*e.Y + Math.Abs(matrix.M33)*e.Z);
        return new(c - transformed, c + transformed);
    }
}
