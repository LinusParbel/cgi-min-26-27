using Engine;
using Engine.OpenGL;
using OpenTK.Graphics.OpenGL4;
using OpenTK.Mathematics;
using RunnerGame.Materials.MapDepth;

namespace RunnerGame.Rendering;

public sealed class MapShadowPass : IDisposable
{
    public const int Resolution = 2048;
    public static readonly Vector3 SunDirection = Vector3.Normalize(new Vector3(-.65f, 1, .45f));
    private int framebuffer, depthTexture;
    private readonly MapDepthMaterial material = new();
    public int DepthTexture => depthTexture;
    public Matrix4 LightSpace { get; private set; }
    public string Diagnostics => $"depth {Resolution}x{Resolution}, FBO complete, {DrawCount} shadow draws";
    public int DrawCount { get; private set; }

    public MapShadowPass()
    {
        int[] viewport = new int[4]; GL.GetInteger(GetPName.Viewport, viewport);
        try
        {
            depthTexture = GL.GenTexture();
            GL.BindTexture(TextureTarget.Texture2D, depthTexture);
            GL.TexImage2D(TextureTarget.Texture2D, 0, PixelInternalFormat.DepthComponent24,
                Resolution, Resolution, 0, PixelFormat.DepthComponent, PixelType.Float, IntPtr.Zero);
            GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureMinFilter, (int)TextureMinFilter.Nearest);
            GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureMagFilter, (int)TextureMagFilter.Nearest);
            GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureWrapS, (int)TextureWrapMode.ClampToBorder);
            GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureWrapT, (int)TextureWrapMode.ClampToBorder);
            GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureBorderColor, new float[] { 1, 1, 1, 1 });
            framebuffer = GL.GenFramebuffer();
            GL.BindFramebuffer(FramebufferTarget.Framebuffer, framebuffer);
            GL.FramebufferTexture2D(FramebufferTarget.Framebuffer, FramebufferAttachment.DepthAttachment,
                TextureTarget.Texture2D, depthTexture, 0);
            GL.DrawBuffer(DrawBufferMode.None); GL.ReadBuffer(ReadBufferMode.None);
            var status = GL.CheckFramebufferStatus(FramebufferTarget.Framebuffer);
            if (status != FramebufferErrorCode.FramebufferComplete)
                throw new InvalidOperationException($"Map shadow framebuffer incomplete: {status}");
        }
        catch { Dispose(); throw; }
        finally
        {
            GL.BindFramebuffer(FramebufferTarget.Framebuffer, 0);
            GL.BindTexture(TextureTarget.Texture2D, 0);
            GL.Viewport(viewport[0], viewport[1], viewport[2], viewport[3]);
        }
    }

    public static Matrix4 CreateLightSpace(Vector3 center) =>
        Matrix4.LookAt(center + SunDirection * 150, center, Vector3.UnitY) *
        Matrix4.CreateOrthographic(100, 125, 1, 330);

    public void Render(OpenGlRenderer renderer, Camera camera, Vector3 center,
        IEnumerable<(Mesh Mesh, Matrix4 Transform)> draws)
    {
        LightSpace = CreateLightSpace(center); material.LightSpace = LightSpace;
        int[] viewport = new int[4]; GL.GetInteger(GetPName.Viewport, viewport);
        bool culling = GL.IsEnabled(EnableCap.CullFace);
        DrawCount = 0;
        try
        {
            // Unit one may still reference this texture from the previous colour pass.
            GL.ActiveTexture(TextureUnit.Texture1); GL.BindTexture(TextureTarget.Texture2D, 0);
            GL.ActiveTexture(TextureUnit.Texture0);
            GL.BindFramebuffer(FramebufferTarget.Framebuffer, framebuffer);
            GL.Viewport(0, 0, Resolution, Resolution);
            GL.Clear(ClearBufferMask.DepthBufferBit);
            // Two-sided casters retain thin facade/foliage geometry.
            GL.Disable(EnableCap.CullFace);
            foreach (var draw in draws) { renderer.Draw(draw.Mesh, material, draw.Transform, camera); DrawCount++; }
        }
        finally
        {
            GL.BindFramebuffer(FramebufferTarget.Framebuffer, 0);
            GL.Viewport(viewport[0], viewport[1], viewport[2], viewport[3]);
            if (culling) GL.Enable(EnableCap.CullFace); else GL.Disable(EnableCap.CullFace);
            GL.CullFace(TriangleFace.Back);
            GL.ActiveTexture(TextureUnit.Texture0);
        }
    }

    public void Dispose()
    {
        if (framebuffer != 0) GL.DeleteFramebuffer(framebuffer);
        if (depthTexture != 0) GL.DeleteTexture(depthTexture);
        framebuffer = depthTexture = 0;
    }
}
