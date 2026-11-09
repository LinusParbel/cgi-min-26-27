using Engine.OpenGL;

namespace Engine.Materials.Deferred;

// Shows one texture of the G-buffer on a fullscreen quad (debug view).
internal sealed class GBufferDebugMaterial : Material
{
    private static readonly ShaderSource Source =
        ShaderSource.FromEmbeddedResources(typeof(GBufferDebugMaterial),
            "fullscreen.vert.glsl", "gbuffer_debug.frag.glsl");

    public Texture? Texture { get; set; }

    protected internal override ShaderSource ShaderSource => Source;

    protected internal override void ApplyUniforms(ShaderProgram shader)
    {
        shader.SetTexture("uTexture", Texture ?? throw new InvalidOperationException("No texture set."), 0);
    }
}
