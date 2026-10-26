using Engine.OpenGL;

namespace Engine.Materials.NormalMapping;

// Like AmbientDiffuseSpecularMaterial, but the normal is read from a normal map for every pixel.
// The normal map stores the normal in tangent space; the TBN matrix (tangent, bitangent, normal)
// converts it into world space. The light is set on the renderer (OpenGlRenderer.DirectionalLight).
public sealed class NormalMappingMaterial : Material
{
    private static readonly ShaderSource Source =
        ShaderSource.FromEmbeddedResources(typeof(NormalMappingMaterial),
            "normal_mapping.vert.glsl", "normal_mapping.frag.glsl");

    private Texture _colorTexture;
    private Texture _normalMap;
    private float _shininess = 64.0f;

    public NormalMappingMaterial(Texture colorTexture, Texture normalMap)
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

    // Shininess exponent of the highlight (see AmbientDiffuseSpecularMaterial).
    public float Shininess
    {
        get => _shininess;
        set => _shininess = value > 0 ? value : throw new ArgumentOutOfRangeException(nameof(value));
    }

    protected internal override ShaderSource ShaderSource => Source;

    protected internal override void ApplyUniforms(ShaderProgram shader)
    {
        // two textures: the color texture on texture unit 0, the normal map on texture unit 1
        shader.SetTexture("uColorTexture", ColorTexture, 0);
        shader.SetTexture("uNormalMap", NormalMap, 1);
        shader.SetFloat("uShininess", Shininess);
    }
}
