using OpenTK.Mathematics;

namespace Engine.Geometry;

// Creates simple primitive shapes as MeshData. Triangles are oriented counter-clockwise.
public static class Primitives
{
    // Cube around the origin; every side has its own vertices so that the normals stay hard.
    public static MeshData CreateCube(float size = 2.0f)
    {
        if (size <= 0) throw new ArgumentOutOfRangeException(nameof(size));

        float h = size * 0.5f;
        Vector3[] corners =
        [
            new(-h, -h, -h), new(h, -h, -h), new(h, h, -h), new(-h, h, -h),
            new(-h, -h, h), new(h, -h, h), new(h, h, h), new(-h, h, h)
        ];
        // Four corners per side, counter-clockwise when viewed from outside.
        (int[] Corners, Vector3 Normal)[] faces =
        [
            ([4, 5, 6, 7], Vector3.UnitZ),
            ([1, 0, 3, 2], -Vector3.UnitZ),
            ([5, 1, 2, 6], Vector3.UnitX),
            ([0, 4, 7, 3], -Vector3.UnitX),
            ([7, 6, 2, 3], Vector3.UnitY),
            ([0, 1, 5, 4], -Vector3.UnitY)
        ];
        Vector2[] texCoords = [new(0, 0), new(1, 0), new(1, 1), new(0, 1)];

        var vertices = new Vertex[faces.Length * 4];
        var indices = new uint[faces.Length * 6];
        for (int f = 0; f < faces.Length; f++)
        {
            for (int c = 0; c < 4; c++)
                vertices[f * 4 + c] = new Vertex(corners[faces[f].Corners[c]], faces[f].Normal, texCoords[c]);

            uint first = (uint)(f * 4);
            int offset = f * 6;
            indices[offset] = first;
            indices[offset + 1] = first + 1;
            indices[offset + 2] = first + 2;
            indices[offset + 3] = first;
            indices[offset + 4] = first + 2;
            indices[offset + 5] = first + 3;
        }

        return new MeshData(vertices, indices);
    }

    // Two triangles that fill the whole screen. The positions are already in the projected
    // coordinate range -1..1, so a shader can use them without any matrix (gl_Position = position).
    public static MeshData CreateFullscreenQuad()
    {
        Vertex[] vertices =
        [
            new(new Vector3(-1, -1, 0), Vector3.UnitZ, new Vector2(0, 0)),
            new(new Vector3(1, -1, 0), Vector3.UnitZ, new Vector2(1, 0)),
            new(new Vector3(1, 1, 0), Vector3.UnitZ, new Vector2(1, 1)),
            new(new Vector3(-1, 1, 0), Vector3.UnitZ, new Vector2(0, 1))
        ];
        uint[] indices = [0, 1, 2, 0, 2, 3];
        return new MeshData(vertices, indices);
    }

    // UV sphere around the origin, e.g. the light volume of a point light.
    // rings = divisions from pole to pole, segments = divisions around the Y axis.
    public static MeshData CreateSphere(float radius = 1.0f, int rings = 12, int segments = 24)
    {
        if (radius <= 0) throw new ArgumentOutOfRangeException(nameof(radius));
        if (rings < 2) throw new ArgumentOutOfRangeException(nameof(rings));
        if (segments < 3) throw new ArgumentOutOfRangeException(nameof(segments));

        var vertices = new List<Vertex>();
        for (int ring = 0; ring <= rings; ring++)
        {
            float v = (float)ring / rings;
            float theta = v * MathF.PI;                     // 0 at the top, PI at the bottom
            for (int segment = 0; segment <= segments; segment++)
            {
                float u = (float)segment / segments;
                float phi = u * 2.0f * MathF.PI;
                var normal = new Vector3(MathF.Sin(theta) * MathF.Sin(phi), MathF.Cos(theta), MathF.Sin(theta) * MathF.Cos(phi));
                vertices.Add(new Vertex(normal * radius, normal, new Vector2(u, 1.0f - v)));
            }
        }

        // two triangles per quad, counter-clockwise when viewed from outside
        var indices = new List<uint>();
        int columns = segments + 1;
        for (int ring = 0; ring < rings; ring++)
        {
            for (int segment = 0; segment < segments; segment++)
            {
                uint topLeft = (uint)(ring * columns + segment);
                uint bottomLeft = (uint)((ring + 1) * columns + segment);
                indices.AddRange([topLeft, bottomLeft, bottomLeft + 1]);
                indices.AddRange([topLeft, bottomLeft + 1, topLeft + 1]);
            }
        }

        return new MeshData(vertices.ToArray(), indices.ToArray());
    }
}
