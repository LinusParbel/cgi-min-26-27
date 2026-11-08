using OpenTK.Mathematics;

namespace Engine.Geometry;

/// <summary>Six inward clip planes for OpenGL (-w..w), using row-vector matrices.</summary>
public readonly struct ViewFrustum
{
    readonly Vector4 left, right, bottom, top, near, far;

    public ViewFrustum(Matrix4 viewProjection)
    {
        var x = viewProjection.Column0;
        var y = viewProjection.Column1;
        var z = viewProjection.Column2;
        var w = viewProjection.Column3;
        left = w+x; right = w-x; bottom = w+y; top = w-y; near = w+z; far = w-z;
    }

    public bool Intersects(Bounds3 bounds) => Inside(left, bounds) && Inside(right, bounds)
        && Inside(bottom, bounds) && Inside(top, bounds) && Inside(near, bounds) && Inside(far, bounds);

    static bool Inside(Vector4 p, Bounds3 b)
    {
        // Positive support vertex: reject only when the entire box is outside.
        float maximum = p.X*(p.X>=0 ? b.Max.X : b.Min.X)
            + p.Y*(p.Y>=0 ? b.Max.Y : b.Min.Y)
            + p.Z*(p.Z>=0 ? b.Max.Z : b.Min.Z) + p.W;
        return maximum >= -1e-4f * (Math.Abs(p.X)+Math.Abs(p.Y)+Math.Abs(p.Z));
    }
}
