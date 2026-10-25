using Engine.Materials;
using Engine.OpenGL;
using OpenTK.Mathematics;
using OpenTK.Graphics.OpenGL4;

namespace RunnerGame.Materials.RunnerLit;

public sealed class RunnerLitMaterial(Texture texture) : Material
{
    public float FogStart { get; set; } = 45;
    public float FogEnd { get; set; } = 135;
    public bool ShadowsEnabled { get; set; }
    public int ShadowTexture { get; set; }
    public Matrix4 LightSpace { get; set; } = Matrix4.Identity;
    public Vector3 SunDirection { get; set; } = Vector3.UnitY;
    private static readonly ShaderSource Source = ShaderSource.FromEmbeddedResources(
        typeof(RunnerLitMaterial), "runner_lit.vert.glsl", "runner_lit.frag.glsl");
    protected override ShaderSource ShaderSource => Source;
    protected override void ApplyUniforms(ShaderProgram shader)
    {
        shader.SetTexture("uTexture", texture, 0);
        shader.SetVector3("uFogColor", new Vector3(.55f, .62f, .70f));
        shader.SetFloat("uFogStart", FogStart);
        shader.SetFloat("uFogEnd", FogEnd);
        shader.SetFloat("uShadowsEnabled", ShadowsEnabled ? 1 : 0);
        shader.SetMatrix4("uLightSpace", LightSpace);
        shader.SetVector3("uSunDirection", SunDirection);
        GL.ActiveTexture(TextureUnit.Texture1);
        GL.BindTexture(TextureTarget.Texture2D, ShadowsEnabled ? ShadowTexture : 0);
        GL.GetInteger(GetPName.CurrentProgram, out int program);
        GL.Uniform1(GL.GetUniformLocation(program, "uShadowMap"), 1);
        GL.ActiveTexture(TextureUnit.Texture0);
    }
}
