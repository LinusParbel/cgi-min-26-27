using OpenTK.Graphics.OpenGL4;
using StbImageSharp;

namespace Engine.OpenGL;

// 2D texture on the GPU. The pixel values are stored unchanged (RGBA, 8 bits per channel);
// there is no color space conversion (sRGB/gamma) for now.
public sealed class Texture : IDisposable
{
    private int _handle;

    public int Width { get; }
    public int Height { get; }

    internal int Handle
    {
        get
        {
            if (_handle == 0) throw new ObjectDisposedException(nameof(Texture));
            return _handle;
        }
    }

    private Texture(int width, int height, byte[] rgbaPixels)
    {
        Width = width;
        Height = height;
        _handle = GL.GenTexture();
        GL.BindTexture(TextureTarget.Texture2D, _handle);
        GL.TexImage2D(TextureTarget.Texture2D, 0, PixelInternalFormat.Rgba8, width, height, 0,
            PixelFormat.Rgba, PixelType.UnsignedByte, rgbaPixels);
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureWrapS, (int)TextureWrapMode.Repeat);
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureWrapT, (int)TextureWrapMode.Repeat);
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureMinFilter, (int)TextureMinFilter.LinearMipmapLinear);
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureMagFilter, (int)TextureMagFilter.Linear);
        GL.GenerateMipmap(GenerateMipmapTarget.Texture2D);
        GL.BindTexture(TextureTarget.Texture2D, 0);
    }

    // An empty texture that is rendered into (e.g. a G-buffer of the deferred rendering).
    // Nearest filtering: every pixel of the screen reads exactly its own texel.
    internal static Texture CreateRenderTarget(int width, int height, PixelInternalFormat internalFormat,
                                               PixelFormat format, PixelType type)
    {
        var texture = new Texture(width, height);
        GL.BindTexture(TextureTarget.Texture2D, texture._handle);
        GL.TexImage2D(TextureTarget.Texture2D, 0, internalFormat, width, height, 0, format, type, IntPtr.Zero);
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureMinFilter, (int)TextureMinFilter.Nearest);
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureMagFilter, (int)TextureMagFilter.Nearest);
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureWrapS, (int)TextureWrapMode.ClampToEdge);
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureWrapT, (int)TextureWrapMode.ClampToEdge);
        GL.BindTexture(TextureTarget.Texture2D, 0);
        return texture;
    }

    private Texture(int width, int height)
    {
        Width = width;
        Height = height;
        _handle = GL.GenTexture();
    }

    // Loads PNG, JPG, BMP, TGA and more. Image files start at the top left, OpenGL expects
    // the first row at the bottom – that is why the image is flipped vertically on load.
    public static Texture FromFile(string path)
    {
        StbImage.stbi_set_flip_vertically_on_load(1);
        using FileStream stream = File.OpenRead(path);
        ImageResult image = ImageResult.FromStream(stream, ColorComponents.RedGreenBlueAlpha);
        return new Texture(image.Width, image.Height, image.Data);
    }

    public void Dispose()
    {
        if (_handle == 0) return;
        GL.DeleteTexture(_handle);
        _handle = 0;
    }
}
