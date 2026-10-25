using Engine.Materials;
using Engine.OpenGL;
using OpenTK.Mathematics;

namespace RunnerGame.Materials.MapDepth;

public sealed class MapDepthMaterial : Material
{
    public Matrix4 LightSpace { get; set; }
    private static readonly ShaderSource Source = ShaderSource.FromEmbeddedResources(
        typeof(MapDepthMaterial), "map_depth.vert.glsl", "map_depth.frag.glsl");
    protected override ShaderSource ShaderSource => Source;
    protected override void ApplyUniforms(ShaderProgram shader)
    {
        shader.SetMatrix4("uLightSpace", LightSpace);
        // Keep the engine's required camera uniforms active; this pass uses the light projection.
        shader.SetFloat("uCameraProjectionWeight", 0);
    }
}
