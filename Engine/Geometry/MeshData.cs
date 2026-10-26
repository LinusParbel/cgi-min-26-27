using OpenTK.Mathematics;

namespace Engine.Geometry;

// Indexed triangle geometry in main memory, without OpenGL state.
// Primitives and model loaders create MeshData; only Mesh uploads it to the GPU.
// The tangents and bitangents of all vertices are calculated here from the positions and UVs.
public sealed class MeshData
{
    public Vertex[] Vertices { get; }
    public uint[] Indices { get; }

    public MeshData(Vertex[] vertices, uint[] indices)
    {
        ArgumentNullException.ThrowIfNull(vertices);
        ArgumentNullException.ThrowIfNull(indices);
        if (vertices.Length == 0)
            throw new ArgumentException("At least one vertex is required.", nameof(vertices));
        if (indices.Length == 0 || indices.Length % 3 != 0)
            throw new ArgumentException("Each triangle requires three indices.", nameof(indices));
        foreach (uint index in indices)
        {
            if (index >= vertices.Length)
                throw new ArgumentOutOfRangeException(nameof(indices), $"Index {index} does not refer to any of the {vertices.Length} vertices.");
        }

        Vertices = WithTangents(vertices, indices);
        Indices = indices;
    }

    // Calculates tangent and bitangent for each triangle from its edges and UV differences:
    //   deltaPos1 = deltaUV1.x * T + deltaUV1.y * B
    //   deltaPos2 = deltaUV2.x * T + deltaUV2.y * B   (solved for T and B)
    // A vertex that is shared by several triangles gets the sum of their tangents, i.e. the
    // tangents are averaged ("average tangents"). Vertices are only shared if position, normal
    // and UV are equal (see ObjLoader), so hard edges and UV seams keep separate tangents.
    private static Vertex[] WithTangents(Vertex[] vertices, uint[] indices)
    {
        var tangents = new Vector3[vertices.Length];
        var bitangents = new Vector3[vertices.Length];

        for (int i = 0; i < indices.Length; i += 3)
        {
            uint i1 = indices[i], i2 = indices[i + 1], i3 = indices[i + 2];
            Vertex v1 = vertices[i1], v2 = vertices[i2], v3 = vertices[i3];

            Vector3 deltaPos1 = v2.Position - v1.Position;
            Vector3 deltaPos2 = v3.Position - v1.Position;
            Vector2 deltaUV1 = v2.TexCoord - v1.TexCoord;
            Vector2 deltaUV2 = v3.TexCoord - v1.TexCoord;

            // Without usable UVs (e.g. all zero) the determinant is 0; f = 1 avoids a division by zero.
            float determinant = deltaUV1.X * deltaUV2.Y - deltaUV2.X * deltaUV1.Y;
            float f = MathF.Abs(determinant) < 0.0001f ? 1.0f : 1.0f / determinant;

            Vector3 tangent = SafeNormalize(f * (deltaUV2.Y * deltaPos1 - deltaUV1.Y * deltaPos2));
            Vector3 bitangent = SafeNormalize(f * (-deltaUV2.X * deltaPos1 + deltaUV1.X * deltaPos2));

            foreach (uint index in new[] { i1, i2, i3 })
            {
                tangents[index] += tangent;
                bitangents[index] += bitangent;
            }
        }

        var result = new Vertex[vertices.Length];
        for (int i = 0; i < vertices.Length; i++)
        {
            Vertex v = vertices[i];
            result[i] = new Vertex(v.Position, v.Normal, v.TexCoord, SafeNormalize(tangents[i]), SafeNormalize(bitangents[i]));
        }
        return result;
    }

    // A zero vector (no usable UVs) has no direction and stays zero instead of NaN.
    private static Vector3 SafeNormalize(Vector3 v) =>
        v.LengthSquared > 0 ? v.Normalized() : Vector3.Zero;
}
