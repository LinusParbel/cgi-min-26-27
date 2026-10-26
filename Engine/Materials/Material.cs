using Engine.OpenGL;

namespace Engine.Materials;

// A material defines which shader is used for drawing and which surface values it receives.
// It owns no OpenGL resources: the renderer manages the compiled shader, and textures are
// only referenced; whoever created them has to dispose of them.
//
// Every material shader must use uModel, uView and uProjection.
// The renderer only sets uCameraPosition and the light uniforms (uLightDirection, uLightAmbientColor,
// uLightDiffuseColor, uLightSpecularColor) if the shader uses them.
public abstract class Material
{
    protected internal abstract ShaderSource ShaderSource { get; }

    // Called while the shader is already active.
    protected internal abstract void ApplyUniforms(ShaderProgram shader);
}
