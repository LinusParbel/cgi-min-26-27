using System.Runtime.InteropServices;
using OpenTK.Mathematics;

namespace Engine.Geometry;

// Vertex format of all meshes: position (xyz), normal (xyz), texture coordinate (uv),
// tangent (xyz) and bitangent (xyz). The field order defines the memory layout in the vertex buffer.
// Tangent and bitangent are calculated by MeshData from the positions and UVs (needed for normal mapping).
[StructLayout(LayoutKind.Sequential)]
public readonly struct Vertex
{
    public readonly Vector3 Position;
    public readonly Vector3 Normal;
    public readonly Vector2 TexCoord;
    public readonly Vector3 Tangent;
    public readonly Vector3 Bitangent;

    public Vertex(Vector3 position, Vector3 normal, Vector2 texCoord)
        : this(position, normal, texCoord, Vector3.Zero, Vector3.Zero) { }

    public Vertex(Vector3 position, Vector3 normal, Vector2 texCoord, Vector3 tangent, Vector3 bitangent)
    {
        Position = position;
        Normal = normal;
        TexCoord = texCoord;
        Tangent = tangent;
        Bitangent = bitangent;
    }
}
