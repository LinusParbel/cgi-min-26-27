using Engine.OpenGL;
using OpenTK.Graphics.OpenGL4;

namespace Engine.Deferred;

// The G-buffer of the deferred rendering: an offscreen framebuffer with three textures
// ("color attachments") and a depth buffer. The geometry pass writes into all three textures
// at the same time; the light pass reads them.
//   ColorAttachment0: ColorTexture             surface color (RGBA, 8 bits per channel)
//   ColorAttachment1: PositionTexture          position in world space (RGB, 32-bit float)
//   ColorAttachment2: NormalShininessTexture   normal in world space + shininess in alpha (RGBA, 32-bit float)
public sealed class GBuffer : IDisposable
{
    private static readonly DrawBuffersEnum[] DrawBuffers =
        [DrawBuffersEnum.ColorAttachment0, DrawBuffersEnum.ColorAttachment1, DrawBuffersEnum.ColorAttachment2];

    private int _framebuffer;
    private int _depthBuffer;

    public int Width { get; }
    public int Height { get; }

    public Texture ColorTexture { get; }
    public Texture PositionTexture { get; }
    public Texture NormalShininessTexture { get; }

    public GBuffer(int width, int height)
    {
        if (width <= 0 || height <= 0) throw new ArgumentOutOfRangeException(nameof(width));
        Width = width;
        Height = height;

        // creating the framebuffer
        _framebuffer = GL.GenFramebuffer();
        GL.BindFramebuffer(FramebufferTarget.Framebuffer, _framebuffer);

        // create the textures ... and bind them to the framebuffer as color attachments 0, 1 and 2
        ColorTexture = Texture.CreateRenderTarget(width, height, PixelInternalFormat.Rgba8, PixelFormat.Rgba, PixelType.UnsignedByte);
        PositionTexture = Texture.CreateRenderTarget(width, height, PixelInternalFormat.Rgb32f, PixelFormat.Rgb, PixelType.Float);
        NormalShininessTexture = Texture.CreateRenderTarget(width, height, PixelInternalFormat.Rgba32f, PixelFormat.Rgba, PixelType.Float);
        GL.FramebufferTexture(FramebufferTarget.Framebuffer, FramebufferAttachment.ColorAttachment0, ColorTexture.Handle, 0);
        GL.FramebufferTexture(FramebufferTarget.Framebuffer, FramebufferAttachment.ColorAttachment1, PositionTexture.Handle, 0);
        GL.FramebufferTexture(FramebufferTarget.Framebuffer, FramebufferAttachment.ColorAttachment2, NormalShininessTexture.Handle, 0);

        // the fragment shader writes into these three attachments (layout(location = 0/1/2) out ...)
        GL.DrawBuffers(DrawBuffers.Length, DrawBuffers);

        // depth buffer, so that near objects cover far ones also in the G-buffer
        _depthBuffer = GL.GenRenderbuffer();
        GL.BindRenderbuffer(RenderbufferTarget.Renderbuffer, _depthBuffer);
        GL.RenderbufferStorage(RenderbufferTarget.Renderbuffer, RenderbufferStorage.DepthComponent24, width, height);
        GL.FramebufferRenderbuffer(FramebufferTarget.Framebuffer, FramebufferAttachment.DepthAttachment, RenderbufferTarget.Renderbuffer, _depthBuffer);

        FramebufferErrorCode status = GL.CheckFramebufferStatus(FramebufferTarget.Framebuffer);
        GL.BindFramebuffer(FramebufferTarget.Framebuffer, 0);
        if (status != FramebufferErrorCode.FramebufferComplete)
            throw new InvalidOperationException($"The G-buffer could not be created: {status}");
    }

    // All following draw calls render into the G-buffer instead of the screen.
    internal void Bind()
    {
        GL.BindFramebuffer(FramebufferTarget.Framebuffer, _framebuffer);
        GL.DrawBuffers(DrawBuffers.Length, DrawBuffers);
    }

    public void Dispose()
    {
        ColorTexture.Dispose();
        PositionTexture.Dispose();
        NormalShininessTexture.Dispose();
        if (_depthBuffer != 0) GL.DeleteRenderbuffer(_depthBuffer);
        if (_framebuffer != 0) GL.DeleteFramebuffer(_framebuffer);
        _depthBuffer = 0;
        _framebuffer = 0;
    }
}
