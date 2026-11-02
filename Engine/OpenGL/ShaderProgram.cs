using OpenTK.Graphics.OpenGL4;
using OpenTK.Mathematics;

namespace Engine.OpenGL;

// Compiles two GLSL sources, links the program and provides uniform helpers.
public sealed class ShaderProgram : IDisposable
{
    private readonly Dictionary<string, int> _uniformLocations = new();
    private readonly string _name;
    private int _handle;

    private ShaderProgram(int handle, string name)
    {
        _handle = handle;
        _name = name;
    }

    internal static ShaderProgram FromSources(string vertexSource, string fragmentSource, string name)
    {
        int vertex = CompileShader(ShaderType.VertexShader, vertexSource, name);
        int fragment = 0;
        int program = 0;
        try
        {
            fragment = CompileShader(ShaderType.FragmentShader, fragmentSource, name);
            program = GL.CreateProgram();
            GL.AttachShader(program, vertex);
            GL.AttachShader(program, fragment);
            GL.LinkProgram(program);
            GL.GetProgram(program, GetProgramParameterName.LinkStatus, out int success);
            if (success == 0)
                throw new InvalidOperationException($"Shader linker ({name}): {GL.GetProgramInfoLog(program)}");

            return new ShaderProgram(program, name);
        }
        catch
        {
            if (program != 0) GL.DeleteProgram(program);
            throw;
        }
        finally
        {
            GL.DeleteShader(vertex);
            if (fragment != 0) GL.DeleteShader(fragment);
        }
    }

    internal void Use()
    {
        ThrowIfDisposed();
        GL.UseProgram(_handle);
    }

    public bool HasUniform(string name) => FindUniformLocation(name) >= 0;

    public void SetMatrix4(string name, Matrix4 value)
    {
        // OpenTK matrices and the multiplication order in the shaders use row vectors.
        GL.UniformMatrix4(GetUniformLocation(name), true, ref value);
    }

    public void SetVector3(string name, Vector3 value) =>
        GL.Uniform3(GetUniformLocation(name), value.X, value.Y, value.Z);

    public void SetFloat(string name, float value) =>
        GL.Uniform1(GetUniformLocation(name), value);

    // Binds the texture to a texture unit and passes the unit number to the sampler uniform.
    public void SetTexture(string name, Texture texture, int unit)
    {
        ArgumentNullException.ThrowIfNull(texture);
        ArgumentOutOfRangeException.ThrowIfNegative(unit);

        GL.ActiveTexture(TextureUnit.Texture0 + unit);
        GL.BindTexture(TextureTarget.Texture2D, texture.Handle);
        GL.Uniform1(GetUniformLocation(name), unit);
    }

    // Same for a cube map (samplerCube in GLSL).
    public void SetCubeTexture(string name, CubeTexture texture, int unit)
    {
        ArgumentNullException.ThrowIfNull(texture);
        ArgumentOutOfRangeException.ThrowIfNegative(unit);

        GL.ActiveTexture(TextureUnit.Texture0 + unit);
        GL.BindTexture(TextureTarget.TextureCubeMap, texture.Handle);
        GL.Uniform1(GetUniformLocation(name), unit);
    }

    private int GetUniformLocation(string name)
    {
        int location = FindUniformLocation(name);
        if (location < 0)
            throw new InvalidOperationException($"Uniform '{name}' is missing in {_name} or not used by the shader.");
        return location;
    }

    // Also caches missing uniforms (-1) so that HasUniform does not query OpenGL every time.
    private int FindUniformLocation(string name)
    {
        ThrowIfDisposed();
        if (_uniformLocations.TryGetValue(name, out int location)) return location;

        location = GL.GetUniformLocation(_handle, name);
        _uniformLocations.Add(name, location);
        return location;
    }

    private static int CompileShader(ShaderType type, string source, string name)
    {
        int shader = GL.CreateShader(type);
        GL.ShaderSource(shader, source);
        GL.CompileShader(shader);
        GL.GetShader(shader, ShaderParameter.CompileStatus, out int success);
        if (success != 0) return shader;

        string message = GL.GetShaderInfoLog(shader);
        GL.DeleteShader(shader);
        throw new InvalidOperationException($"{name} ({type}): {message}");
    }

    private void ThrowIfDisposed()
    {
        if (_handle == 0) throw new ObjectDisposedException(nameof(ShaderProgram));
    }

    public void Dispose()
    {
        if (_handle == 0) return;
        GL.DeleteProgram(_handle);
        _handle = 0;
    }
}
