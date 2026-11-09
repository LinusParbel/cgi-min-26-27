using Engine.Geometry;
using Engine.Lighting;
using Engine.Materials.Deferred;
using Engine.OpenGL;
using OpenTK.Graphics.OpenGL4;
using OpenTK.Mathematics;

namespace Engine.Deferred;

// Deferred rendering in two passes:
//  1. Geometry pass: BeginGeometryPass(), then draw all objects with a GBufferMaterial.
//     Nothing is lit yet; color, position and normal of every pixel end up in the G-buffer.
//  2. Light pass: DrawDirectionalLight() draws a fullscreen quad that lights every pixel,
//     then DrawPointLight() adds each point light (a sphere as light volume, additive blending).
// Effort: number of objects + number of lights (instead of objects * lights in forward rendering).
// The draw calls go through the OpenGlRenderer, so the camera and the directional light are taken from there.
public sealed class DeferredRendering : IDisposable
{
    private readonly OpenGlRenderer _renderer;
    private readonly Mesh _fullscreenQuad;
    private readonly Mesh _lightVolume;

    private readonly DirectionalLightPassMaterial _directionalLightMaterial = new();
    private readonly PointLightPassMaterial _pointLightMaterial = new();
    private readonly GBufferDebugMaterial _debugMaterial = new();

    public DeferredRendering(OpenGlRenderer renderer, int width, int height)
    {
        _renderer = renderer ?? throw new ArgumentNullException(nameof(renderer));
        _fullscreenQuad = new Mesh(Primitives.CreateFullscreenQuad());
        _lightVolume = new Mesh(Primitives.CreateSphere(1.0f));
        GBuffer = new GBuffer(width, height);
    }

    public GBuffer GBuffer { get; private set; }

    // Color of the screen where no object is drawn.
    public Vector3 BackgroundColor { get; set; } = new(0.025f, 0.035f, 0.06f);

    // The G-buffer must have the size of the screen; call this whenever the window size changes.
    public void Resize(int width, int height)
    {
        if (width <= 0 || height <= 0) return;
        GBuffer.Dispose();
        GBuffer = new GBuffer(width, height);
    }

    // 1. Geometry pass: all following draw calls render into the G-buffer.
    public void BeginGeometryPass()
    {
        GBuffer.Bind();
        GL.ClearColor(0, 0, 0, 0);
        GL.Clear(ClearBufferMask.ColorBufferBit | ClearBufferMask.DepthBufferBit);

        GL.Disable(EnableCap.Blend);
        GL.Enable(EnableCap.DepthTest);
        GL.DepthMask(true);
        GL.Enable(EnableCap.CullFace);
        GL.CullFace(TriangleFace.Back);
    }

    // 2a. Light pass, directional light: a fullscreen quad on the screen (default framebuffer).
    public void DrawDirectionalLight(Camera camera)
    {
        BeginScreenPass();
        _directionalLightMaterial.GBuffer = GBuffer;
        _renderer.Draw(_fullscreenQuad, _directionalLightMaterial, Matrix4.Identity, camera);
    }

    // 2b. Light pass, point light: the sphere around the light is drawn with additive blending,
    // so every light adds its part (BlendingFactor.One, BlendingFactor.One).
    public void DrawPointLight(PointLight light, Camera camera)
    {
        ArgumentNullException.ThrowIfNull(light);

        GL.Enable(EnableCap.Blend);
        GL.BlendFunc(BlendingFactor.One, BlendingFactor.One);
        // the back faces of the sphere are drawn, so the light also works when the camera is inside the sphere
        GL.Enable(EnableCap.CullFace);
        GL.CullFace(TriangleFace.Front);

        _pointLightMaterial.GBuffer = GBuffer;
        _pointLightMaterial.Light = light;
        Matrix4 model = Matrix4.CreateScale(light.Radius) * Matrix4.CreateTranslation(light.Position);
        _renderer.Draw(_lightVolume, _pointLightMaterial, model, camera);
    }

    // Debug view: shows one G-buffer texture instead of the lit image.
    public void ShowGBufferTexture(Texture texture, Camera camera)
    {
        BeginScreenPass();
        _debugMaterial.Texture = texture;
        _renderer.Draw(_fullscreenQuad, _debugMaterial, Matrix4.Identity, camera);
    }

    // Back to the screen: clear it and draw without depth test and culling (the G-buffer already has the depth).
    private void BeginScreenPass()
    {
        GL.BindFramebuffer(FramebufferTarget.Framebuffer, 0);
        GL.ClearColor(BackgroundColor.X, BackgroundColor.Y, BackgroundColor.Z, 1.0f);
        GL.Clear(ClearBufferMask.ColorBufferBit | ClearBufferMask.DepthBufferBit);

        GL.Disable(EnableCap.Blend);
        GL.Disable(EnableCap.DepthTest);
        GL.Disable(EnableCap.CullFace);
    }

    public void Dispose()
    {
        GBuffer.Dispose();
        _fullscreenQuad.Dispose();
        _lightVolume.Dispose();
    }
}
