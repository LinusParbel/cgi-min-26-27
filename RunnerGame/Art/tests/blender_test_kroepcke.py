r"""Blender tests for the Kroepcke-Uhr build. Run from the repo root:
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup
    --python-exit-code 1 --python RunnerGame/Art/tests/blender_test_kroepcke.py
"""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

import bpy

ART = Path(__file__).resolve().parents[1]
ASSET = ART / "assets" / "kroepcke_uhr"
sys.path.insert(0, str(ART / "lib"))
import photo_lib  # noqa: E402


def load_build():
    spec = importlib.util.spec_from_file_location("kroepcke_build", ASSET / "build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def lm(name):
    return bpy.data.objects["LM_" + name].matrix_world.translation


def meshes(parts):
    return [o for objs in parts.values() for o in objs if o.type == 'MESH']


def world_edges(parts):
    for o in meshes(parts):
        mw = o.matrix_world
        vs = [mw @ v.co for v in o.data.vertices]
        for e in o.data.edges:
            yield vs[e.vertices[0]], vs[e.vertices[1]]


class KroepckeBuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        photo_lib.al.clear_scene()
        cls.spec = photo_lib.Spec(ASSET / "spec.json")
        cls.parts = load_build().build(cls.spec)
        cls.verts = [o.matrix_world @ v.co for o in meshes(cls.parts) for v in o.data.vertices]

    def width_at(self, z):
        xs = []
        for a, b in world_edges(self.parts):
            if (a.z - z) * (b.z - z) <= 0:
                if abs(a.z - b.z) < 1e-9:
                    xs += [a.x, b.x]
                else:
                    t = (z - a.z) / (b.z - a.z)
                    xs.append(a.x + t * (b.x - a.x))
        return max(xs) - min(xs)

    def test_budget(self):
        tris = sum(len(p.vertices) - 2 for o in meshes(self.parts) for p in o.data.polygons)
        self.assertLessEqual(tris, self.spec.d("tri_budget"))

    def test_ground_and_height(self):
        self.assertAlmostEqual(min(v.z for v in self.verts), 0.0, delta=0.01)
        self.assertAlmostEqual(max(v.z for v in self.verts), self.spec.d("spike")["z1"], delta=0.02)

    def test_landmarks_of_ref04(self):
        refs = json.loads((ASSET / "refs.json").read_text(encoding="utf-8"))
        photo = next(p for p in refs["photos"] if p["file"] == "ref/04.jpg")
        self.assertTrue(photo["landmarks"])
        for name in photo["landmarks"]:
            self.assertIn("LM_" + name, bpy.data.objects, name)
        self.assertLess(lm("dial_centre").y, 0)          # faces -Y

    def test_ledge_width(self):
        z = self.spec.d("ledge")["profile"][0][0] + 0.01
        self.assertAlmostEqual(self.width_at(z), self.spec.d("ledge")["profile"][0][1], delta=0.03)

    def test_body_width_with_pilasters(self):
        b = self.spec.d("body")
        z = (b["z0"] + b["z1"]) / 2
        self.assertAlmostEqual(self.width_at(z), b["w"] + 2 * b["pilaster_proud"], delta=0.03)

    def test_pedestal_arch_is_open(self):
        # A ray through the middle of the gap between the front feet must pass the whole pedestal (faces, not
        # vertices: a closed panel has no vertices in the gap and would slip past a vertex check).
        from mathutils import Vector
        ped = self.spec.d("pedestal")
        z = (ped["z0"] + ped["arch"]["z1"]) / 2
        bpy.context.view_layer.update()
        hit, *_ = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, Vector((0, -5, z)), Vector((0, 1, 0)),
                                             distance=10)
        self.assertFalse(hit, f"something blocks the gap between the feet at z {z:.2f}")


class ExportTest(unittest.TestCase):
    def test_export_single_part(self):
        photo_lib.al.clear_scene()
        parts = load_build().build(photo_lib.Spec(ASSET / "spec.json"))
        with tempfile.TemporaryDirectory() as tmp:
            photo_lib.bake_shared_and_export(parts, {"body": (0, 0, 0)}, tmp, "T", res=128, samples=1)
            self.assertEqual(sorted(p.name for p in Path(tmp).iterdir()), ["T.png", "T_body.obj", "T_parts.json"])


if __name__ == "__main__":
    unittest.main(argv=["x"])
