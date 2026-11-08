using Engine.Geometry;
using OpenTK.Mathematics;

namespace RunnerGame.Rendering;

/// <summary>Visibility before expensive run-clip sampling; never changes pursuit state.</summary>
public static class PursuerVisibility
{
    // Covers the entire shared run cycle; checked against installed clip samples.
    public static readonly Bounds3 RunBounds = new(new(-2, -1, -2), new(2, 3, 2));

    public static Matrix4 Transform(float elapsed, float distance, float playerX, bool close)
    {
        float gap = close ? 2 : 14 + Math.Max(0, distance - elapsed*3.37f);
        return Matrix4.CreateRotationY(MathF.PI) * Matrix4.CreateTranslation(playerX+.75f, 0, gap);
    }

    public static bool IsNeeded(Bounds3 world, ViewFrustum camera, ViewFrustum light)
    {
        if (camera.Intersects(world)) return true;
        if (!light.Intersects(world)) return false;
        // Normal street receivers are at/above pavement level. Include the full
        // swept shadow volume down to a conservative -0.5 m, including walls.
        float height = Math.Max(0, world.Max.Y + .5f);
        var offset = -MapShadowPass.SunDirection * (height / MapShadowPass.SunDirection.Y);
        var influence = new Bounds3(Vector3.ComponentMin(world.Min, world.Min+offset),
            Vector3.ComponentMax(world.Max, world.Max+offset));
        return camera.Intersects(influence);
    }
}
