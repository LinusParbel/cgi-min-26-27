using Engine.Deferred;
using Engine.OpenGL;

namespace Engine.Materials.Deferred;

// Light pass for the directional light: drawn on a fullscreen quad, it reads the G-buffer at every
// pixel of the screen. The light itself comes from the renderer (OpenGlRenderer.DirectionalLight).
internal sealed class DirectionalLightPassMaterial : Material
{
    private static readonly ShaderSource Source =
        ShaderSource.FromEmbeddedResources(typeof(DirectionalLightPassMaterial),
            "fullscreen.vert.glsl", "directional_light_pass.frag.glsl");

    public GBuffer? GBuffer { get; set; }

    protected internal override ShaderSource ShaderSource => Source;

    protected internal override void ApplyUniforms(ShaderProgram shader)
    {
        GBuffer gBuffer = GBuffer ?? throw new InvalidOperationException("No G-buffer set.");
        // all G-buffer textures are passed to the shader
        shader.SetTexture("gColor", gBuffer.ColorTexture, 0);
        shader.SetTexture("gNormal", gBuffer.NormalShininessTexture, 1);
        shader.SetTexture("gPosition", gBuffer.PositionTexture, 2);
    }
}
