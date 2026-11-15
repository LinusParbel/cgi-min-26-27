using Engine.OpenGL;

namespace Engine.Materials.TransparentLitTexture;

// Like TransparentTextureMaterial, but lit by the directional light of the renderer (ambient, diffuse and
// specular, Blinn-Phong as in AmbientDiffuseSpecularMaterial). Uses AlphaBlend by default.
// With deferred rendering it is drawn forward after the light pass, so it only receives the
// directional light, not the point lights.
public sealed class TransparentLitTextureMaterial : Material
{
    private static readonly ShaderSource Source =
        ShaderSource.FromEmbeddedResources(typeof(TransparentLitTextureMaterial),
            "transparent_lit_texture.vert.glsl", "transparent_lit_texture.frag.glsl");

    private Texture _texture;
    private float _alpha = 0.5f;
    private float _shininess = 64.0f;

    public TransparentLitTextureMaterial(Texture texture)
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

    // Shininess exponent of the highlight (see AmbientDiffuseSpecularMaterial).
    public float Shininess
    {
        get => _shininess;
        set => _shininess = value > 0 ? value : throw new ArgumentOutOfRangeException(nameof(value));
    }

    protected internal override ShaderSource ShaderSource => Source;

    protected internal override void ApplyUniforms(ShaderProgram shader)
    {
        shader.SetTexture("uTexture", Texture, 0);
        shader.SetFloat("uAlpha", Alpha);
        shader.SetFloat("uShininess", Shininess);
    }
}
