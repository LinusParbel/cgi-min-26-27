using Engine.Deferred;
using Engine.Lighting;
using Engine.OpenGL;
using OpenTK.Mathematics;

namespace Engine.Materials.Deferred;

// Light pass for one point light: drawn on a sphere (the light volume), it only runs on the pixels
// the light can reach. The texture coordinate for the G-buffer comes from gl_FragCoord / screen size.
internal sealed class PointLightPassMaterial : Material
{
    private static readonly ShaderSource Source =
        ShaderSource.FromEmbeddedResources(typeof(PointLightPassMaterial),
            "point_light_pass.vert.glsl", "point_light_pass.frag.glsl");

    public GBuffer? GBuffer { get; set; }
    public PointLight? Light { get; set; }

    protected internal override ShaderSource ShaderSource => Source;

    protected internal override void ApplyUniforms(ShaderProgram shader)
    {
        GBuffer gBuffer = GBuffer ?? throw new InvalidOperationException("No G-buffer set.");
        PointLight light = Light ?? throw new InvalidOperationException("No point light set.");

        shader.SetTexture("gColor", gBuffer.ColorTexture, 0);
        shader.SetTexture("gNormal", gBuffer.NormalShininessTexture, 1);
        shader.SetTexture("gPosition", gBuffer.PositionTexture, 2);
        shader.SetVector2("uScreenSize", new Vector2(gBuffer.Width, gBuffer.Height));

        shader.SetVector3("uPointLightPosition", light.Position);
        shader.SetFloat("uPointLightRadius", light.Radius);
        shader.SetVector3("uPointLightAmbientColor", light.AmbientColor);
        shader.SetVector3("uPointLightDiffuseColor", light.DiffuseColor);
        shader.SetVector3("uPointLightSpecularColor", light.SpecularColor);
    }
}
