using Engine.OpenGL;
using OpenTK.Mathematics;

namespace Engine;

// The visible area of a camera: a frustum bounded by six clipping planes.
// Used for frustum culling: objects outside the frustum do not need to be drawn.
public sealed class Frustum
{
    private enum PlaneId
    {
        Near = 0,
        Far = 1,
        Left = 2,
        Right = 3,
        Top = 4,
        Bottom = 5
    }

    // A plane in Hessian normal form: all points p with dot(Normal, p) + D = 0.
    private struct Plane
    {
        public Vector3 Normal;
        public float D;
    }

    private readonly Plane[] _planes = new Plane[6];

    // The planes are calculated "back" from the combined view-projection matrix
    // (view * projection, OpenTK row vectors: M14 + M11 = 4th column + 1st column, …).
    public Frustum(Matrix4 viewProjection)
    {
        Matrix4 mat = viewProjection;

        // left
        Plane plane = new Plane();
        plane.Normal.X = mat.M14 + mat.M11;
        plane.Normal.Y = mat.M24 + mat.M21;
        plane.Normal.Z = mat.M34 + mat.M31;
        plane.D = mat.M44 + mat.M41;
        _planes[(int)PlaneId.Left] = plane;

        // right
        plane = new Plane();
        plane.Normal.X = mat.M14 - mat.M11;
        plane.Normal.Y = mat.M24 - mat.M21;
        plane.Normal.Z = mat.M34 - mat.M31;
        plane.D = mat.M44 - mat.M41;
        _planes[(int)PlaneId.Right] = plane;

        // bottom
        plane = new Plane();
        plane.Normal.X = mat.M14 + mat.M12;
        plane.Normal.Y = mat.M24 + mat.M22;
        plane.Normal.Z = mat.M34 + mat.M32;
        plane.D = mat.M44 + mat.M42;
        _planes[(int)PlaneId.Bottom] = plane;

        // top
        plane = new Plane();
        plane.Normal.X = mat.M14 - mat.M12;
        plane.Normal.Y = mat.M24 - mat.M22;
        plane.Normal.Z = mat.M34 - mat.M32;
        plane.D = mat.M44 - mat.M42;
        _planes[(int)PlaneId.Top] = plane;

        // near
        plane = new Plane();
        plane.Normal.X = mat.M14 + mat.M13;
        plane.Normal.Y = mat.M24 + mat.M23;
        plane.Normal.Z = mat.M34 + mat.M33;
        plane.D = mat.M44 + mat.M43;
        _planes[(int)PlaneId.Near] = plane;

        // far
        plane = new Plane();
        plane.Normal.X = mat.M14 - mat.M13;
        plane.Normal.Y = mat.M24 - mat.M23;
        plane.Normal.Z = mat.M34 - mat.M33;
        plane.D = mat.M44 - mat.M43;
        _planes[(int)PlaneId.Far] = plane;

        // normalize, so that SignedDistanceToPoint returns real distances
        for (int i = 0; i < _planes.Length; i++)
        {
            float length = _planes[i].Normal.Length;
            _planes[i].Normal /= length;
            _planes[i].D /= length;
        }
    }

    // Hessian normal form: the signed distance between a point and a plane (positive = inside).
    private float SignedDistanceToPoint(int planeId, Vector3 point) =>
        Vector3.Dot(_planes[planeId].Normal, point) + _planes[planeId].D;

    // Is the sphere completely or partly inside the frustum?
    public bool SphereInFrustum(Vector3 center, float radius)
    {
        for (int i = 0; i < _planes.Length; i++)
        {
            if (SignedDistanceToPoint(i, center) < -radius)
                return false;
        }
        return true;
    }

    // Sphere test for a mesh drawn with the given model matrix: the position is in the last row of the
    // matrix, the radius was calculated while loading and grows with the scale of the matrix.
    public bool IsVisible(Mesh mesh, Matrix4 modelMatrix)
    {
        ArgumentNullException.ThrowIfNull(mesh);
        Vector3 position = new(modelMatrix.M41, modelMatrix.M42, modelMatrix.M43);
        float scale = MathF.Max(modelMatrix.Row0.Xyz.Length,
                      MathF.Max(modelMatrix.Row1.Xyz.Length, modelMatrix.Row2.Xyz.Length));
        return SphereInFrustum(position, mesh.BoundingRadius * scale);
    }
}
