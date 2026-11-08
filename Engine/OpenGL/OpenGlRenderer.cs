using Engine.Materials;
using Engine.Geometry;
using OpenTK.Graphics.OpenGL4;
using OpenTK.Mathematics;

namespace Engine.OpenGL;

// Only here is it decided how mesh, material and camera are drawn together.
// The renderer compiles each material shader on first use and releases it in Dispose.
public sealed class OpenGlRenderer : IDisposable
{
    private readonly Dictionary<ShaderSource, ShaderProgram> _shaders = new();
    private float _aspectRatio = 1.0f;

    public Vector3 LightPosition { get; set; } = new(3.0f, 4.0f, 5.0f);

    public OpenGlRenderer()
    {
        GL.ClearColor(0.025f, 0.035f, 0.06f, 1.0f);
        GL.Enable(EnableCap.DepthTest);
        GL.Enable(EnableCap.CullFace);
        GL.CullFace(TriangleFace.Back);
        GL.FrontFace(FrontFaceDirection.Ccw);
    }

    public void Resize(int width, int height)
    {
        if (width <= 0 || height <= 0) return;
        GL.Viewport(0, 0, width, height);
        _aspectRatio = (float)width / height;
    }

    public void Clear() => GL.Clear(ClearBufferMask.ColorBufferBit | ClearBufferMask.DepthBufferBit);

    public bool IsVisible(Mesh mesh, Matrix4 modelMatrix, Camera camera) =>
        new ViewFrustum(camera.ViewMatrix * camera.GetProjectionMatrix(_aspectRatio))
            .Intersects(mesh.LocalBounds.Transform(modelMatrix));

    public void Draw(Mesh mesh, Material material, Matrix4 modelMatrix, Camera camera)
    {
        ArgumentNullException.ThrowIfNull(mesh);
        ArgumentNullException.ThrowIfNull(material);
        ArgumentNullException.ThrowIfNull(camera);

        ShaderProgram shader = GetShader(material.ShaderSource);
        shader.Use();
        material.ApplyUniforms(shader);
        shader.SetMatrix4("uModel", modelMatrix);
        shader.SetMatrix4("uView", camera.ViewMatrix);
        shader.SetMatrix4("uProjection", camera.GetProjectionMatrix(_aspectRatio));
        if (shader.HasUniform("uCameraPosition")) shader.SetVector3("uCameraPosition", camera.Position);
        if (shader.HasUniform("uLightPosition")) shader.SetVector3("uLightPosition", LightPosition);

        GL.BindVertexArray(mesh.VertexArray);
        GL.DrawElements(PrimitiveType.Triangles, mesh.IndexCount, DrawElementsType.UnsignedInt, 0);
        GL.BindVertexArray(0);
    }

    private ShaderProgram GetShader(ShaderSource source)
    {
        if (_shaders.TryGetValue(source, out ShaderProgram? shader)) return shader;

        shader = source.Compile();
        _shaders.Add(source, shader);
        return shader;
    }

    public void Dispose()
    {
        foreach (ShaderProgram shader in _shaders.Values) shader.Dispose();
        _shaders.Clear();
    }
}
