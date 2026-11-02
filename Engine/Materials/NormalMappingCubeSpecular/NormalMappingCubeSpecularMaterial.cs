using Engine.OpenGL;

namespace Engine.Materials.NormalMappingCubeSpecular;

// Normal mapping with ambient and diffuse light from the directional light; instead of a computed
// highlight, the specular part is the reflection of the environment from a cube map.
public sealed class NormalMappingCubeSpecularMaterial : Material
{
    private static readonly ShaderSource Source =
        ShaderSource.FromEmbeddedResources(typeof(NormalMappingCubeSpecularMaterial),
            "normal_mapping_cube_specular.vert.glsl", "normal_mapping_cube_specular.frag.glsl");

    private Texture _colorTexture;
    private Texture _normalMap;
    private CubeTexture _cubeTexture;

    public NormalMappingCubeSpecularMaterial(Texture colorTexture, Texture normalMap, CubeTexture cubeTexture)
    {
        _colorTexture = colorTexture ?? throw new ArgumentNullException(nameof(colorTexture));
        _normalMap = normalMap ?? throw new ArgumentNullException(nameof(normalMap));
        _cubeTexture = cubeTexture ?? throw new ArgumentNullException(nameof(cubeTexture));
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

    public CubeTexture CubeTexture
    {
        get => _cubeTexture;
        set => _cubeTexture = value ?? throw new ArgumentNullException(nameof(value));
    }

    protected internal override ShaderSource ShaderSource => Source;

    protected internal override void ApplyUniforms(ShaderProgram shader)
    {
        // color texture on unit 0, normal map on unit 1, cube map on unit 2
        shader.SetTexture("uColorTexture", ColorTexture, 0);
        shader.SetTexture("uNormalMap", NormalMap, 1);
        shader.SetCubeTexture("uCubeTexture", CubeTexture, 2);
    }
}
