using Engine.Materials;
using Engine.OpenGL;
using OpenTK.Mathematics;

namespace AssetViewer.GammaLit;

// Same uniforms as LitTextureMaterial, but lights in linear space (texture decoded with pow 2.2).
public sealed class GammaLitMaterial : Material
{
    private static readonly ShaderSource Source =
        ShaderSource.FromEmbeddedResources(typeof(GammaLitMaterial), "gamma_lit.vert.glsl", "gamma_lit.frag.glsl");

    public GammaLitMaterial(Texture texture)
    {
        Texture = texture ?? throw new ArgumentNullException(nameof(texture));
    }

    public Texture Texture { get; set; }
    public Vector3 Tint { get; set; } = Vector3.One;
    public float AmbientStrength { get; set; } = 0.14f;
    public float SpecularStrength { get; set; } = 0.75f;
    public float Shininess { get; set; } = 48.0f;

    protected override ShaderSource ShaderSource => Source;

    protected override void ApplyUniforms(ShaderProgram shader)
    {
        shader.SetTexture("uTexture", Texture, 0);
        shader.SetVector3("uTint", Tint);
        shader.SetFloat("uAmbientStrength", AmbientStrength);
        shader.SetFloat("uSpecularStrength", SpecularStrength);
        shader.SetFloat("uShininess", Shininess);
    }
}
