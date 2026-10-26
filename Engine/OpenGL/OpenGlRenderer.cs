using Engine.Lighting;
using Engine.Materials;
using OpenTK.Graphics.OpenGL4;
using OpenTK.Mathematics;

namespace Engine.OpenGL;

// Only here is it decided how mesh, material and camera are drawn together.
// The renderer compiles each material shader on first use and releases it in Dispose.
public sealed class OpenGlRenderer : IDisposable
{
    private readonly Dictionary<ShaderSource, ShaderProgram> _shaders = new();
    private float _aspectRatio = 1.0f;

    private DirectionalLight _directionalLight = new();

    // The light of the scene; it is passed to every shader that uses the uLight... uniforms.
    public DirectionalLight DirectionalLight
    {
        get => _directionalLight;
        set => _directionalLight = value ?? throw new ArgumentNullException(nameof(value));
    }

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
        SetLightUniforms(shader);

        GL.BindVertexArray(mesh.VertexArray);
        GL.DrawElements(PrimitiveType.Triangles, mesh.IndexCount, DrawElementsType.UnsignedInt, 0);
        GL.BindVertexArray(0);

        // Materials with several textures switch the active texture unit; reset it for the next draw call.
        GL.ActiveTexture(TextureUnit.Texture0);
    }

    // Only shaders that use lighting declare these uniforms; all others are left untouched.
    private void SetLightUniforms(ShaderProgram shader)
    {
        if (shader.HasUniform("uLightDirection")) shader.SetVector3("uLightDirection", DirectionalLight.Direction);
        if (shader.HasUniform("uLightAmbientColor")) shader.SetVector3("uLightAmbientColor", DirectionalLight.AmbientColor);
        if (shader.HasUniform("uLightDiffuseColor")) shader.SetVector3("uLightDiffuseColor", DirectionalLight.DiffuseColor);
        if (shader.HasUniform("uLightSpecularColor")) shader.SetVector3("uLightSpecularColor", DirectionalLight.SpecularColor);
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
