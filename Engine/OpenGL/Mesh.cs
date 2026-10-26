using System.Runtime.InteropServices;
using Engine.Geometry;
using OpenTK.Graphics.OpenGL4;

namespace Engine.OpenGL;

// GPU copy of a MeshData: vertex buffer, index buffer and the matching vertex array object.
// Attribute locations: 0 = position, 1 = normal, 2 = texture coordinate, 3 = tangent, 4 = bitangent.
public sealed class Mesh : IDisposable
{
    private int _vertexArray;
    private int _vertexBuffer;
    private int _indexBuffer;

    internal int VertexArray => _vertexArray;
    public int IndexCount { get; }

    public Mesh(MeshData data)
    {
        ArgumentNullException.ThrowIfNull(data);

        IndexCount = data.Indices.Length;
        _vertexArray = GL.GenVertexArray();
        _vertexBuffer = GL.GenBuffer();
        _indexBuffer = GL.GenBuffer();

        GL.BindVertexArray(_vertexArray);
        GL.BindBuffer(BufferTarget.ArrayBuffer, _vertexBuffer);
        GL.BufferData(BufferTarget.ArrayBuffer, data.Vertices.Length * Marshal.SizeOf<Vertex>(), data.Vertices, BufferUsageHint.StaticDraw);
        // The index buffer is stored in the VAO and therefore must not be unbound before the VAO.
        GL.BindBuffer(BufferTarget.ElementArrayBuffer, _indexBuffer);
        GL.BufferData(BufferTarget.ElementArrayBuffer, data.Indices.Length * sizeof(uint), data.Indices, BufferUsageHint.StaticDraw);

        SetAttribute(0, 3, nameof(Vertex.Position));
        SetAttribute(1, 3, nameof(Vertex.Normal));
        SetAttribute(2, 2, nameof(Vertex.TexCoord));
        SetAttribute(3, 3, nameof(Vertex.Tangent));
        SetAttribute(4, 3, nameof(Vertex.Bitangent));

        GL.BindVertexArray(0);
        GL.BindBuffer(BufferTarget.ArrayBuffer, 0);
    }

    private static void SetAttribute(int location, int components, string field)
    {
        int stride = Marshal.SizeOf<Vertex>();
        int offset = (int)Marshal.OffsetOf<Vertex>(field);
        GL.VertexAttribPointer(location, components, VertexAttribPointerType.Float, false, stride, offset);
        GL.EnableVertexAttribArray(location);
    }

    public void Dispose()
    {
        if (_indexBuffer != 0) GL.DeleteBuffer(_indexBuffer);
        if (_vertexBuffer != 0) GL.DeleteBuffer(_vertexBuffer);
        if (_vertexArray != 0) GL.DeleteVertexArray(_vertexArray);
        _indexBuffer = 0;
        _vertexBuffer = 0;
        _vertexArray = 0;
    }
}
