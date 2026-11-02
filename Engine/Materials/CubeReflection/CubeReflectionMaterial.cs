using Engine.OpenGL;

namespace Engine.Materials.CubeReflection;

// Mirror-like surface: the view direction is reflected at the surface normal, and the
// reflected direction picks the color from a cube map (the environment). The normal
// comes from a normal map, so the reflection follows the bumps of the surface.
public sealed class CubeReflectionMaterial : Material
{
    private static readonly ShaderSource Source =
        ShaderSource.FromEmbeddedResources(typeof(CubeReflectionMaterial),
            "cube_reflection.vert.glsl", "cube_reflection.frag.glsl");

    private Texture _normalMap;
    private CubeTexture _cubeTexture;

    public CubeReflectionMaterial(Texture normalMap, CubeTexture cubeTexture)
    {
        _normalMap = normalMap ?? throw new ArgumentNullException(nameof(normalMap));
        _cubeTexture = cubeTexture ?? throw new ArgumentNullException(nameof(cubeTexture));
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
        // the cube map on texture unit 0, the normal map on texture unit 1
        shader.SetCubeTexture("uCubeTexture", CubeTexture, 0);
        shader.SetTexture("uNormalMap", NormalMap, 1);
    }
}
