using OpenTK.Mathematics;

namespace Engine.Lighting;

// A light that shines from the same direction everywhere in the scene, like the sun.
// It has no position; only its direction and its three colors are passed to the shader.
public sealed class DirectionalLight
{
    private Vector3 _direction = new Vector3(1.0f, 1.0f, 1.0f).Normalized();

    // Direction from the surface towards the light (it is normalized automatically).
    public Vector3 Direction
    {
        get => _direction;
        set => _direction = value.LengthSquared > 0
            ? value.Normalized()
            : throw new ArgumentException("The light direction must not be a zero vector.", nameof(value));
    }

    // Light that reaches every surface, also the ones facing away from the light.
    public Vector3 AmbientColor { get; set; } = new(0.2f, 0.2f, 0.2f);

    // Light that depends on the angle between the surface normal and the light direction.
    public Vector3 DiffuseColor { get; set; } = new(0.8f, 0.8f, 0.8f);

    // Color of the highlights; they also depend on the view direction.
    public Vector3 SpecularColor { get; set; } = new(1.0f, 1.0f, 1.0f);
}
