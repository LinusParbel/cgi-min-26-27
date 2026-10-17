"""Blender side of the photo-to-model workflow (runs inside Blender 5.2; never imports PIL).

Builds on the shared tools/asset-spike/asset_lib.py (materials, primitives, bake + export), which is
imported read-only — never edit it from here.

Conventions: Z-up, 1 unit = 1 m. Vehicles face +Y (they drive towards -Z in the engine), props face -Y.
Landmarks are empties named LM_<name>; the same names are used for pixel positions in refs.json.
"""
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools" / "asset-spike"))
import asset_lib as al  # noqa: E402,F401  (re-exported for asset build scripts)


class Spec:
    """spec.json of an asset: measured dimensions (metres/degrees) and linear RGB colours."""

    def __init__(self, path):
        self.path = Path(path)
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.dims = data["dims"]
        self.colors = data["colors"]

    def d(self, name):
        if name not in self.dims:
            raise KeyError(f"{self.path.name} has no dim '{name}'")
        return self.dims[name]["value"]

    def c(self, name):
        if name not in self.colors:
            raise KeyError(f"{self.path.name} has no colour '{name}'")
        return tuple(self.colors[name]["linear"])


def landmark(name, loc):
    o = bpy.data.objects.new("LM_" + name, None)
    o.empty_display_size = 0.03
    o.location = loc
    bpy.context.scene.collection.objects.link(o)
    bpy.context.view_layer.update()   # so matrix_world is valid right away
    return o


def tube(name, p0, p1, r, mat, verts=16, bevel=0.0):
    """Cylinder of radius r from point p0 to point p1 (any direction)."""
    p0, p1 = Vector(p0), Vector(p1)
    axis = p1 - p0
    o = al.cyl(name, r, axis.length, (p0 + p1) / 2, mat, axis='Z', verts=verts, bevel=bevel)
    o.rotation_euler = axis.to_track_quat('Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    return o
