using OpenTK.Graphics.OpenGL4;
using StbImageSharp;

namespace Engine.OpenGL;

// Cube map texture: six square images that form the inside of a cube. A 3D direction instead of
// a 2D UV coordinate picks the color (samplerCube in GLSL), e.g. for reflections of the environment.
public sealed class CubeTexture : IDisposable
{
    private int _handle;

    internal int Handle
    {
        get
        {
            if (_handle == 0) throw new ObjectDisposedException(nameof(CubeTexture));
            return _handle;
        }
    }

    private CubeTexture(int handle) => _handle = handle;

    // The six images in the order of the OpenGL cube map sides: +X, -X, +Y, -Y, +Z, -Z.
    public static CubeTexture FromFiles(string positiveX, string negativeX, string positiveY,
                                        string negativeY, string positiveZ, string negativeZ)
    {
        string[] files = [positiveX, negativeX, positiveY, negativeY, positiveZ, negativeZ];

        int handle = GL.GenTexture();
        GL.BindTexture(TextureTarget.TextureCubeMap, handle);

        // Unlike 2D textures, the sides of a cube map are NOT flipped: OpenGL expects the first row at the top.
        StbImage.stbi_set_flip_vertically_on_load(0);
        for (int i = 0; i < files.Length; i++)
        {
            using FileStream stream = File.OpenRead(files[i]);
            ImageResult image = ImageResult.FromStream(stream, ColorComponents.RedGreenBlueAlpha);
            GL.TexImage2D(TextureTarget.TextureCubeMapPositiveX + i, 0, PixelInternalFormat.Rgba8,
                image.Width, image.Height, 0, PixelFormat.Rgba, PixelType.UnsignedByte, image.Data);
        }

        GL.TexParameter(TextureTarget.TextureCubeMap, TextureParameterName.TextureMinFilter, (int)TextureMinFilter.Linear);
        GL.TexParameter(TextureTarget.TextureCubeMap, TextureParameterName.TextureMagFilter, (int)TextureMagFilter.Linear);
        GL.TexParameter(TextureTarget.TextureCubeMap, TextureParameterName.TextureWrapS, (int)TextureWrapMode.ClampToEdge);
        GL.TexParameter(TextureTarget.TextureCubeMap, TextureParameterName.TextureWrapT, (int)TextureWrapMode.ClampToEdge);
        GL.TexParameter(TextureTarget.TextureCubeMap, TextureParameterName.TextureWrapR, (int)TextureWrapMode.ClampToEdge);
        GL.BindTexture(TextureTarget.TextureCubeMap, 0);

        return new CubeTexture(handle);
    }

    public void Dispose()
    {
        if (_handle == 0) return;
        GL.DeleteTexture(_handle);
        _handle = 0;
    }
}
