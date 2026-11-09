using OpenTK.Mathematics;

namespace Engine.Lighting;

// A local light that shines in all directions from one position. Its influence ends at Radius;
// in deferred rendering it is drawn as a sphere with this radius (the "light volume").
public sealed class PointLight
{
    private float _radius = 3.0f;

    public Vector3 Position { get; set; }

    public Vector3 AmbientColor { get; set; } = new(0.0f, 0.0f, 0.0f);
    public Vector3 DiffuseColor { get; set; } = new(1.0f, 1.0f, 1.0f);
    public Vector3 SpecularColor { get; set; } = new(1.0f, 1.0f, 1.0f);

    // Distance at which the light has faded out completely.
    public float Radius
    {
        get => _radius;
        set => _radius = value > 0 ? value : throw new ArgumentOutOfRangeException(nameof(value));
    }
}
