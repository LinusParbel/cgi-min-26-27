r"""Blender tests for the Kroepcke-Uhr build. Run from the repo root:
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup
    --python-exit-code 1 --python RunnerGame/Art/tests/blender_test_kroepcke.py
"""
import importlib.util
import json
import math
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

    def clusters(self, values, gap):
        values = sorted(values)
        n = 0
        prev = None
        for v in values:
            if prev is None or v - prev > gap:
                n += 1
            prev = v
        return n

    def test_pilaster_figures_and_stars(self):
        pf = self.spec.d("ornaments")["pilaster_figures"]
        b = self.spec.d("body")
        plane = -(b["w"] / 2 + b["pilaster_proud"] + pf["proud"])
        zs = [v.z for v in self.verts if abs(v.y - plane) < 1e-4 and v.x > 0.4]
        self.assertEqual(self.clusters(zs, 0.15), len(pf["z"][0::2]))
        gold = bpy.data.objects["clock_gold"].data
        self.assertEqual(len([v for v in gold.vertices if v.co.z < 4.9]), 10 * 4 * 2 * len(pf["z"][1::2]))

    def test_showcase_frame_steps(self):
        sc, steps = self.spec.d("showcase"), self.spec.d("ornaments")["showcase_frame"]["steps"]
        h = self.spec.d("body")["w"] / 2
        t = 0.1 * sc["w"]
        planes = {round(v.y, 3) for v in self.verts if abs(v.x) < 0.41 and 1.34 < v.z < 1.45 and -h + 0.001 < v.y < -h + t - 0.0045}
        self.assertGreaterEqual(len(planes), steps)

    def slice_points(self, z):
        pts = []
        for a, b in world_edges(self.parts):
            if (a.z - z) * (b.z - z) <= 0:
                if abs(a.z - b.z) < 1e-9:
                    pts += [(a.x, a.y), (b.x, b.y)]
                else:
                    t = (z - a.z) / (b.z - a.z)
                    pts.append((a.x + t * (b.x - a.x), a.y + t * (b.y - a.y)))
        return pts

    def test_square_legs_waist_belly_and_count(self):
        ped = self.spec.d("pedestal")
        c = ped["w"] / 2 - ped["feet_w"] / 2
        widths = {}
        for z in (0.42, 0.60):
            xs = [x for x, y in self.slice_points(z) if abs(x - c) < 0.3 and abs(y + c) < 0.3]
            widths[z] = max(xs) - min(xs)
        prof = dict((round(z, 2), dm) for z, dm in ped["baluster_profile"])
        self.assertAlmostEqual(widths[0.42], prof[0.42], delta=0.02)
        self.assertAlmostEqual(widths[0.60], prof[0.6], delta=0.02)
        self.assertLess(widths[0.60], widths[0.42] * 0.7)
        pts = self.slice_points(0.60)                 # eight separate square legs
        groups = []
        for p in pts:
            for g in groups:
                if any(abs(p[0] - q[0]) < 0.3 and abs(p[1] - q[1]) < 0.3 for q in g):
                    g.append(p)
                    break
            else:
                groups.append([p])
        self.assertEqual(len(groups), 8)
        for g in groups:                              # square section: x and y extent equal
            self.assertAlmostEqual(max(x for x, _ in g) - min(x for x, _ in g), max(y for _, y in g) - min(y for _, y in g), delta=0.01)

    def test_sloped_ledge_and_finial(self):
        led = self.spec.d("ledge")["profile"]
        self.assertAlmostEqual(self.width_at((led[1][0] + led[2][0]) / 2), (led[1][1] + led[2][1]) / 2, delta=0.03)
        spike = self.spec.d("spike")
        gold = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith("clock_gold")][0]
        zs = [v.co.z for v in gold.data.vertices]
        self.assertGreater(max(zs), spike["z0"] + 0.9 * spike["finial"]["h"])

    def test_cap_is_a_round_dome(self):
        import math as m
        cap = self.spec.d("cap")
        z = (cap["profile"][0][0] + cap["profile"][-1][0]) / 2
        sector_min = {}
        for x, y in self.slice_points(z):
            r = m.hypot(x, y)
            if r < 0.6:
                k = int((m.atan2(y, x) + m.pi) / (2 * m.pi) * 16) % 16
                sector_min[k] = min(sector_min.get(k, 9), r)
        self.assertEqual(len(sector_min), 16)
        lo, hi = min(sector_min.values()), max(sector_min.values())
        self.assertLessEqual(hi / lo, 1.06)
        self.assertGreater(lo, 0.25)
        top_r = cap["profile"][-1][1] / 2
        self.assertTrue([v for v in self.verts if abs(v.z - cap["profile"][-1][0]) < 2e-3 and abs(m.hypot(v.x, v.y) - top_r) < 3e-3])
        self.assertFalse([v for v in self.verts if 0.3 < m.hypot(v.x, v.y) < 0.6 and v.z > cap["profile"][-1][0] + 0.02 and v.z < 5.0])

    def test_hood_rings(self):
        hr, dh = self.spec.d("ornaments")["hood_rings"], self.spec.d("dial_hood")
        head = self.spec.d("head_box")
        dz = self.spec.d("dial")["z"]
        for k, r in enumerate(hr["radii"]):
            y = -head["w"] / 2 - dh["depth"] + k * hr["step_depth"]
            hits = [v for v in self.verts if abs(v.y - y) < 1e-3 and abs(math.hypot(v.x, v.z - dz) - r) < 2e-3]
            self.assertTrue(hits, (k, r))

    def test_wing_scrolls(self):
        ws, w = self.spec.d("ornaments")["wing_scrolls"], self.spec.d("wings")["profile"][1]
        ztop = w[0] + ws["r"]
        for sign in (-1, 1):
            self.assertTrue([v for v in self.verts if abs(v.z - ztop) < 1e-3 and sign * v.x > 0.5 and v.y < -0.5])

    def test_pedestal_arch_is_open(self):
        # A ray through the middle of the gap between the front feet must pass the whole pedestal (faces, not
        # vertices: a closed panel has no vertices in the gap and would slip past a vertex check).
        from mathutils import Vector
        ped = self.spec.d("pedestal")
        z = (ped["z0"] + ped["arch"]["z1"]) / 2
        bpy.context.view_layer.update()
        c = ped["w"] / 2 - ped["feet_w"] / 2
        for x in (-c / 2, c / 2):                    # midway between the middle leg (x=0) and a corner leg
            hit, *_ = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, Vector((x, -5, z)), Vector((0, 1, 0)),
                                                 distance=10)
            self.assertFalse(hit, f"something blocks the gap between the legs at x {x:.2f}, z {z:.2f}")


class ExportTest(unittest.TestCase):
    def test_export_single_part(self):
        photo_lib.al.clear_scene()
        parts = load_build().build(photo_lib.Spec(ASSET / "spec.json"))
        with tempfile.TemporaryDirectory() as tmp:
            photo_lib.bake_shared_and_export(parts, {"body": (0, 0, 0)}, tmp, "T", res=128, samples=1)
            self.assertEqual(sorted(p.name for p in Path(tmp).iterdir()), ["T.png", "T_body.obj", "T_parts.json"])


if __name__ == "__main__":
    unittest.main(argv=["x"])
