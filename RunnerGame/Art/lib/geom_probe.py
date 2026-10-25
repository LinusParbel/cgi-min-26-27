"""Surface probes for Blender build tests (runs inside Blender; no PIL).

Tests that look at vertices are blind: a gap between two feet, a frame step or a long rail has vertices only at
its ends. These helpers measure the BUILT surface instead:

    tri_count(parts)               triangles of all mesh objects
    bounds(parts)                  ((xmin, ymin, zmin), (xmax, ymax, zmax)) in world space
    slice_points(parts, z)         (x, y) where every edge crosses the plane at height z
    width_at(parts, z)             x extent of that slice
    ray_hit(origin, direction, d)  first surface hit by scene.ray_cast, or None (use it for openings and gaps)
    fingerprint(parts)             one string (tris + bounds) that changes when the geometry changes

`parts` is the dict returned by an asset's build(spec): {part name: [objects]}.
"""
import hashlib

import bpy
from mathutils import Vector


def meshes(parts):
    return [o for objs in parts.values() for o in objs if o.type == 'MESH']


def world_edges(parts):
    for o in meshes(parts):
        mw = o.matrix_world
        vs = [mw @ v.co for v in o.data.vertices]
        for e in o.data.edges:
            yield vs[e.vertices[0]], vs[e.vertices[1]]


def tri_count(parts):
    return sum(len(p.vertices) - 2 for o in meshes(parts) for p in o.data.polygons)


def bounds(parts):
    vs = [o.matrix_world @ v.co for o in meshes(parts) for v in o.data.vertices]
    return (tuple(min(v[i] for v in vs) for i in range(3)), tuple(max(v[i] for v in vs) for i in range(3)))


def slice_points(parts, z):
    pts = []
    for a, b in world_edges(parts):
        if (a.z - z) * (b.z - z) <= 0:
            if abs(a.z - b.z) < 1e-9:
                pts += [(a.x, a.y), (b.x, b.y)]
            else:
                t = (z - a.z) / (b.z - a.z)
                pts.append((a.x + t * (b.x - a.x), a.y + t * (b.y - a.y)))
    return pts


def width_at(parts, z):
    xs = [x for x, _ in slice_points(parts, z)]
    return max(xs) - min(xs)


def ray_hit(origin, direction, distance=50.0):
    """First surface hit as a world-space Vector, or None. A ray through an opening that should be empty must return None."""
    bpy.context.view_layer.update()
    hit, loc, *_ = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, Vector(origin), Vector(direction), distance=distance)
    return loc if hit else None


def fingerprint(parts):
    """tris + bounds + a hash of every vertex rounded to 1 mm: any real geometry change alters it."""
    lo, hi = bounds(parts)
    vs = sorted((round(v.x, 3), round(v.y, 3), round(v.z, 3)) for o in meshes(parts) for v in (o.matrix_world @ w.co for w in o.data.vertices))
    digest = hashlib.md5(repr(vs).encode()).hexdigest()[:10]
    return f"tris={tri_count(parts)} bounds={[round(v, 3) for v in lo + hi]} verts={digest}"
