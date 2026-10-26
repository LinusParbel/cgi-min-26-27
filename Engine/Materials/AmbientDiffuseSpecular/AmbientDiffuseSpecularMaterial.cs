using Engine.OpenGL;

namespace Engine.Materials.AmbientDiffuseSpecular;

// Lighting with ambient, diffuse and specular components (Blinn-Phong) from one directional light.
// The surface color comes from the texture; the light is set on the renderer (OpenGlRenderer.DirectionalLight).
public sealed class AmbientDiffuseSpecularMaterial : Material
{
    private static readonly ShaderSource Source =
        ShaderSource.FromEmbeddedResources(typeof(AmbientDiffuseSpecularMaterial),
            "ambient_diffuse_specular.vert.glsl", "ambient_diffuse_specular.frag.glsl");

    private Texture _texture;
    private float _shininess = 64.0f;

    public AmbientDiffuseSpecularMaterial(Texture texture)
    {
        _texture = texture ?? throw new ArgumentNullException(nameof(texture));
    }

    public Texture Texture
    {
        get => _texture;
        set => _texture = value ?? throw new ArgumentNullException(nameof(value));
    }

    // Shininess exponent: small values give large, soft highlights, large values small, sharp ones.
    // With the halfway vector (Blinn) it has to be about 4 times larger than with Phong for the same look.
    public float Shininess
    {
        get => _shininess;
        set => _shininess = value > 0 ? value : throw new ArgumentOutOfRangeException(nameof(value));
    }

    protected internal override ShaderSource ShaderSource => Source;

    protected internal override void ApplyUniforms(ShaderProgram shader)
    {
        shader.SetTexture("uTexture", Texture, 0);
        shader.SetFloat("uShininess", Shininess);
    }
}
