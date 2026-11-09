using Engine.OpenGL;

namespace Engine.Materials.Deferred;

// Material for the geometry pass of the deferred rendering: instead of a lit color it writes the
// surface properties into the three G-buffer textures (color, world position, normal + shininess).
// The normal comes from a normal map, as in the NormalMappingMaterial. The light is added later.
public sealed class GBufferMaterial : Material
{
    private static readonly ShaderSource Source =
        ShaderSource.FromEmbeddedResources(typeof(GBufferMaterial), "gbuffer.vert.glsl", "gbuffer.frag.glsl");

    private Texture _colorTexture;
    private Texture _normalMap;
    private float _shininess = 64.0f;

    public GBufferMaterial(Texture colorTexture, Texture normalMap)
    {
        _colorTexture = colorTexture ?? throw new ArgumentNullException(nameof(colorTexture));
        _normalMap = normalMap ?? throw new ArgumentNullException(nameof(normalMap));
    }

    public Texture ColorTexture
    {
        get => _colorTexture;
        set => _colorTexture = value ?? throw new ArgumentNullException(nameof(value));
    }

    public Texture NormalMap
    {
        get => _normalMap;
        set => _normalMap = value ?? throw new ArgumentNullException(nameof(value));
    }

    // Shininess exponent; it is stored in the G-buffer and used by every light.
    public float Shininess
    {
        get => _shininess;
        set => _shininess = value > 0 ? value : throw new ArgumentOutOfRangeException(nameof(value));
    }

    protected internal override ShaderSource ShaderSource => Source;

    protected internal override void ApplyUniforms(ShaderProgram shader)
    {
        shader.SetTexture("uColorTexture", ColorTexture, 0);
        shader.SetTexture("uNormalMap", NormalMap, 1);
        shader.SetFloat("uShininess", Shininess);
    }
}
