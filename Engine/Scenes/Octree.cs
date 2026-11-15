using OpenTK.Mathematics;

namespace Engine.Scenes;

// An octree divides a cube-shaped area into eight sub-areas, each of them again into eight, and so on
// (a quadtree does the same in 2D with four sub-areas).
//
// Insert: an element goes into every sub-area its bounding sphere intersects; sub-areas are only created
// when something is inserted. An element that is bigger than a sub-area stays in the current area
// (otherwise a big wall would end up in thousands of small areas).
//
// Query: if an area is outside the view frustum, none of its elements is visible and none of them has
// to be tested. Elements can be referenced in more than one area, so the query remembers which elements
// it has already found.
//
// The octree only knows positions and radii: it does not draw anything. It is meant for elements that
// do not move; a moving element would have to be removed and inserted again.
public sealed class Octree<T> where T : notnull
{
    private readonly Vector3 _min;
    private readonly Vector3 _max;
    private readonly int _depth;
    private readonly int _maxDepth;

    private readonly Octree<T>?[] _children = new Octree<T>?[8];
    private readonly List<(T Item, Vector3 Center, float Radius)> _items = new();

    // elements already found in the current query (only used by the root)
    private readonly HashSet<T> _found = new();

    public Octree(Vector3 min, Vector3 max, int maxDepth = 5) : this(min, max, 1, maxDepth) { }

    private Octree(Vector3 min, Vector3 max, int depth, int maxDepth)
    {
        if (min.X >= max.X || min.Y >= max.Y || min.Z >= max.Z)
            throw new ArgumentException("min must be smaller than max.");
        if (maxDepth < 1) throw new ArgumentOutOfRangeException(nameof(maxDepth));

        _min = min;
        _max = max;
        _depth = depth;
        _maxDepth = maxDepth;
    }

    public void Insert(T item, Vector3 center, float radius)
    {
        ArgumentNullException.ThrowIfNull(item);

        Vector3 subSize = (_max - _min) / 2;
        bool smallerThanSubArea = 2 * radius <= MathF.Min(subSize.X, MathF.Min(subSize.Y, subSize.Z));

        // maximum depth reached or too big for the sub-areas: the element stays in this area
        if (_depth == _maxDepth || !smallerThanSubArea)
        {
            _items.Add((item, center, radius));
            return;
        }

        // i is the index of the sub-area: bit 0 = right half (X), bit 1 = upper half (Y), bit 2 = front half (Z)
        for (int i = 0; i < 8; i++)
        {
            (Vector3 subMin, Vector3 subMax) = GetSubArea(i);
            if (SphereIntersectsBox(center, radius, subMin, subMax))
            {
                // create the sub-octree only when it is needed
                _children[i] ??= new Octree<T>(subMin, subMax, _depth + 1, _maxDepth);
                _children[i]!.Insert(item, center, radius);
            }
        }
    }

    // Adds all elements whose bounding sphere is in the frustum to results (each element once).
    // Returns the number of sphere tests (areas + elements), to compare it with testing every element.
    public int Query(Frustum frustum, List<T> results)
    {
        ArgumentNullException.ThrowIfNull(frustum);
        ArgumentNullException.ThrowIfNull(results);

        _found.Clear();
        return Query(frustum, results, _found);
    }

    private int Query(Frustum frustum, List<T> results, HashSet<T> found)
    {
        // this area is not visible: nothing inside can be visible, no further tests
        int tests = 1;
        if (!frustum.BoxInFrustum(_min, _max)) return tests;

        foreach ((T item, Vector3 center, float radius) in _items)
        {
            if (found.Contains(item)) continue;   // already found in another area
            tests++;
            if (frustum.SphereInFrustum(center, radius))
            {
                found.Add(item);
                results.Add(item);
            }
        }

        foreach (Octree<T>? child in _children)
        {
            if (child is not null) tests += child.Query(frustum, results, found);
        }
        return tests;
    }

    private (Vector3 Min, Vector3 Max) GetSubArea(int i)
    {
        Vector3 half = (_max - _min) / 2;
        Vector3 subMin = _min;
        if ((i & 1) != 0) subMin.X += half.X;
        if ((i & 2) != 0) subMin.Y += half.Y;
        if ((i & 4) != 0) subMin.Z += half.Z;
        return (subMin, subMin + half);
    }

    // Sphere and axis-aligned box intersect if the point of the box closest to the sphere center
    // is not farther away than the radius.
    private static bool SphereIntersectsBox(Vector3 center, float radius, Vector3 min, Vector3 max)
    {
        Vector3 closest = Vector3.Clamp(center, min, max);
        return Vector3.DistanceSquared(center, closest) <= radius * radius;
    }
}
