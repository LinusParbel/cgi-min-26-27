using Engine.OpenGL;

namespace Engine.Materials.TransparentTexture;

// A texture without lighting that can be transparent: the alpha of the texture is multiplied by Alpha.
// Alpha can be used to smoothly blend objects in and out. Uses AlphaBlend by default.
public sealed class TransparentTextureMaterial : Material
{
    private static readonly ShaderSource Source =
        ShaderSource.FromEmbeddedResources(typeof(TransparentTextureMaterial),
            "transparent_texture.vert.glsl", "transparent_texture.frag.glsl");

    private Texture _texture;
    private float _alpha = 0.5f;

    public TransparentTextureMaterial(Texture texture)
    {
        _texture = texture ?? throw new ArgumentNullException(nameof(texture));
        BlendMode = BlendMode.AlphaBlend;
    }

    public Texture Texture
    {
        get => _texture;
        set => _texture = value ?? throw new ArgumentNullException(nameof(value));
    }

    // 0 = invisible, 1 = only the alpha of the texture
    public float Alpha
    {
        get => _alpha;
        set => _alpha = Math.Clamp(value, 0.0f, 1.0f);
    }

    protected internal override ShaderSource ShaderSource => Source;

    protected internal override void ApplyUniforms(ShaderProgram shader)
    {
        shader.SetTexture("uTexture", Texture, 0);
        shader.SetFloat("uAlpha", Alpha);
    }
}
