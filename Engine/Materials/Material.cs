using Engine.OpenGL;

namespace Engine.Materials;

// A material defines which shader is used for drawing and which surface values it receives.
// It owns no OpenGL resources: the renderer manages the compiled shader, and textures are
// only referenced; whoever created them has to dispose of them.
//
// The renderer sets uModel, uView, uProjection, uCameraPosition and the light uniforms
// (uLightDirection, uLightAmbientColor, uLightDiffuseColor, uLightSpecularColor) if the shader uses them.
public abstract class Material
{
    protected internal abstract ShaderSource ShaderSource { get; }

    // Opaque by default. With AlphaBlend or Additive the renderer enables blending for this material
    // and does not write the depth. With deferred rendering, transparent objects are drawn after the
    // light pass with a forward material (not with a GBufferMaterial).
    public BlendMode BlendMode { get; set; } = BlendMode.Opaque;

    public bool IsTransparent => BlendMode != BlendMode.Opaque;

    // Called while the shader is already active.
    protected internal abstract void ApplyUniforms(ShaderProgram shader);
}
