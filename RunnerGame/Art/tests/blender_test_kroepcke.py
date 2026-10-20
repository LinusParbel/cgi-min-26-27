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


class FrameStepsTest(unittest.TestCase):
    """Relative test: more frame steps in the spec must give more distinct frame planes in the built model.
    (An absolute plane count is fooled by the bead row and the glass recess.)"""

    def planes(self, steps):
        photo_lib.al.clear_scene()
        spec = photo_lib.Spec(ASSET / "spec.json")
        spec.dims["ornaments"]["value"]["showcase_frame"]["steps"] = steps
        parts = load_build().build(spec)
        sc, h = spec.d("showcase"), spec.d("body")["w"] / 2
        ys = set()                       # slice every edge with the plane x = 0 (long rails have no vertex there)
        for o in [o for objs in parts.values() for o in objs if o.type == 'MESH']:
            mw = o.matrix_world
            for e in o.data.edges:
                a, b = (mw @ o.data.vertices[i].co for i in e.vertices)
                if (a.x > 0) == (b.x > 0) or abs(a.x - b.x) < 1e-9:
                    continue
                s = -a.x / (b.x - a.x)
                y, z = a.y + s * (b.y - a.y), a.z + s * (b.z - a.z)
                if sc["z0"] - 0.10 < z < sc["z0"] + 0.06 and -h - 0.02 < y < -h + 0.12:
                    ys.add(round(y, 3))
        return len(ys)

    def test_steps_change_the_frame(self):
        spec_steps = photo_lib.Spec(ASSET / "spec.json").d("ornaments")["showcase_frame"]["steps"]
        self.assertGreater(spec_steps, 1)
        self.assertGreater(self.planes(spec_steps), self.planes(1))


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
        self.assertAlmostEqual(max(v.z for v in self.verts), self.spec.d("top")["rod"]["z1"], delta=0.02)

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
        self.assertEqual(len([v for v in gold.vertices if v.co.z < 4.0]), 10 * 4 * 2 * len(pf["z"][1::2]))

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

    def test_four_corner_legs_waisted(self):
        ped = self.spec.d("pedestal")
        c = self.spec.d("pedestal")["apron"]["w"] / 2 - ped["w"] / 2
        prof = dict((round(z, 2), w) for z, w in ped["profile"])
        zs = sorted(prof)                       # sample heights come from the spec profile, not fixed numbers
        z_bot = zs[0]
        z_waist = min(zs[1:-1], key=lambda z: prof[z])
        z_top = zs[-1] - 0.001
        prof[z_top] = prof[zs[-1]]
        widths = {}
        for z in (z_bot, z_waist, z_top):
            xs = [x for x, y in self.slice_points(z) if abs(x - c) < 0.3 and abs(y + c) < 0.3]
            widths[z] = max(xs) - min(xs)
            self.assertAlmostEqual(widths[z], prof[z], delta=0.02)
        self.assertLess(widths[z_waist], widths[z_bot] - 0.05)
        self.assertLess(widths[z_waist], widths[z_top] - 0.05)
        pts = self.slice_points((z_bot + z_top) / 2)
        groups = []
        for p in pts:
            for g in groups:
                if any(abs(p[0] - q[0]) < 0.6 and abs(p[1] - q[1]) < 0.6 for q in g):
                    g.append(p)
                    break
            else:
                groups.append([p])
        self.assertEqual(len(groups), 4)                  # one leg per corner, nothing at the middle of a side
        self.assertEqual(sorted((round(sum(x for x, _ in g) / len(g), 1), round(sum(y for _, y in g) / len(g), 1)) for g in groups),
                         sorted((round(sx * c, 1), round(sy * c, 1)) for sx in (-1, 1) for sy in (-1, 1)))
        self.assertFalse([p for p in pts if abs(p[0]) < 0.4 and abs(p[1]) > 0.4])

    def test_plinth_and_stone_widths(self):
        ps = self.spec.d("plinth_slab")
        self.assertAlmostEqual(self.width_at(ps["stone"]["z1"] / 2), ps["stone"]["w"], delta=0.03)
        z, w = ps["iron_plinth"]["profile"][0]
        self.assertAlmostEqual(self.width_at(z + 0.01), w, delta=0.03)

    def test_sloped_ledge(self):
        led = self.spec.d("ledge")["profile"]
        self.assertAlmostEqual(self.width_at((led[1][0] + led[2][0]) / 2), (led[1][1] + led[2][1]) / 2, delta=0.03)

    def top_hs(self, t):
        dm = self.spec.d("top")["dome"]
        return dm["top_w"] / 2 + (dm["foot_w"] - dm["top_w"]) / 2 * math.sqrt(1 - t * t)

    def test_dome_is_square_in_plan(self):
        dm = self.spec.d("top")["dome"]
        z = (dm["z0"] + dm["z1"]) / 2
        pts = [p for p in self.slice_points(z) if math.hypot(*p) < 0.8]
        ex = max(abs(x) for x, _ in pts)
        ey = max(abs(y) for _, y in pts)
        self.assertAlmostEqual(ex / ey, 1.0, delta=0.02)
        self.assertGreater(max(math.hypot(x, y) for x, y in pts) / ex, 1.3)       # corners reach out: a round dome gives 1.0

    def test_dome_half_width_follows_profile(self):
        dm = self.spec.d("top")["dome"]
        for k in (2, 4, 6):                           # levels of the 8-step stack
            t = k / 8
            z = dm["z0"] + (dm["z1"] - dm["z0"]) * t
            front = max(-y for x, y in self.slice_points(z) if abs(x) < 0.1)    # includes the 0.018 rib crest
            self.assertAlmostEqual(front, self.top_hs(t) + dm["rib_r"], delta=0.02)

    def test_dome_foot_width(self):
        dm = self.spec.d("top")["dome"]
        front = max(-y for x, y in self.slice_points(dm["z0"] + 0.005) if abs(x) < 0.1 and abs(y) < 0.6)
        self.assertAlmostEqual(2 * (front - dm["rib_r"]), dm["foot_w"], delta=0.02)

    def test_four_hip_ropes(self):
        from mathutils import Vector
        dm = self.spec.d("top")["dome"]
        r = dm["hip_rope"]["r"]
        n_ropes = 0
        for sx in (-1, 1):
            for sy in (-1, 1):
                ok = True
                for t in (0.25, 0.5, 0.75):
                    z = dm["z0"] + (dm["z1"] - dm["z0"]) * t
                    c = Vector((sx * self.top_hs(t), sy * self.top_hs(t), z)) + Vector((sx, sy, 0)).normalized() * 0.6 * r
                    near = [v for v in self.verts if (v - c).length < 0.03]
                    ok = ok and len(near) >= 6
                n_ropes += ok
        self.assertEqual(n_ropes, 4)

    def test_ball_radius_and_rod_tip(self):
        top = self.spec.d("top")
        ring = [math.hypot(v.x, v.y) for v in self.verts if abs(v.z - top["ball"]["z"]) < 1e-3]
        self.assertAlmostEqual(min(ring), top["ball"]["r"], delta=0.003)
        self.assertAlmostEqual(max(v.z for v in self.verts), top["rod"]["z1"], delta=0.002)

    def test_one_medallion_ring_facing_sideways(self):
        # ref/04 (straight front) sees the ring edge-on, ref/01 (45 deg) sees it at an angle -> one ring, plane x = 0
        md = self.spec.d("top")["medallion"]
        ro = md["r_outer"]
        near = [v for v in self.verts if abs(v.z - md["z"]) < 2e-3]
        self.assertTrue([v for v in near if abs(abs(v.y) - ro) < 2e-3 and abs(v.x) < md["thick"]])        # ring in the YZ plane
        self.assertFalse([v for v in near if abs(abs(v.x) - ro) < 2e-3 and abs(v.y) < md["thick"]])       # none in the XZ plane

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

    def test_glass_material_varies_with_height(self):
        nodes = bpy.data.materials["glass"].node_tree.nodes
        links = bpy.data.materials["glass"].node_tree.links
        types = {n.type for n in nodes}
        self.assertIn("SEPXYZ", types)
        self.assertIn("MAP_RANGE", types)
        self.assertIn("NEW_GEOMETRY", types)
        self.assertTrue([l for l in links if l.from_node.type == "SEPXYZ" and l.from_socket.name == "Z" and l.to_node.type == "MAP_RANGE"])
        bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
        self.assertTrue(bsdf.inputs["Base Color"].is_linked)
        # the height gradient must really change colour: some MIX node blends two clearly different colours
        spread = 0.0
        for n in nodes:
            if n.type == "MIX" and getattr(n, "data_type", "") == "RGBA" and not n.inputs[6].is_linked and not n.inputs[7].is_linked:
                a, b = n.inputs[6].default_value, n.inputs[7].default_value
                spread = max(spread, max(abs(a[i] - b[i]) for i in range(3)))
        self.assertGreater(spread, 0.05, "glass gradient endpoints are (almost) the same colour")

    def test_glass_pane_is_recessed(self):
        from mathutils import Vector
        sc, gl = self.spec.d("showcase"), self.spec.d("glass_look")
        h = self.spec.d("body")["w"] / 2
        frame_inner = -h + self.spec.d("ornaments")["showcase_frame"]["steps"] * 0.25 * 0.1 * sc["w"]
        zc = (sc["z0"] + sc["z1"]) / 2
        bpy.context.view_layer.update()
        hit, loc, *_ = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, Vector((0, -5, zc)), Vector((0, 1, 0)), distance=10)
        self.assertTrue(hit)
        self.assertGreaterEqual(loc.y - frame_inner, gl["recess"] - 1e-3)

    def test_pane_head_has_concave_corners_and_bump(self):
        sc = self.spec.d("showcase")
        gl = self.spec.d("glass_look")
        h = self.spec.d("body")["w"] / 2
        stp = sc["frame_w"] / self.spec.d("ornaments")["showcase_frame"]["steps"]
        w, z1 = sc["w"] - 2 * sc["frame_w"], sc["z1"] - sc["frame_w"]
        yg = -h + self.spec.d("ornaments")["showcase_frame"]["steps"] * 0.25 * 0.1 * sc["w"] + gl["recess"]
        glass = [v for o in meshes(self.parts) if o.data.materials and o.data.materials[0].name == "glass" for v in
                 [o.matrix_world @ v.co for v in o.data.vertices]]
        pane = [v for v in glass if abs(v.y - yg) < 1e-4 and v.z > 2.0 and abs(v.x) < w / 2 + 1e-3]

        def top_at(x):                                # highest pane vertex near x, interpolating the outline
            pts = sorted(pane, key=lambda v: v.x)
            best = None
            for a, b in zip(pts, pts[1:]):
                if a.x <= x <= b.x and b.x > a.x:
                    zz = max(a.z, b.z)
                    best = zz if best is None else max(best, zz)
            return best

        near = max(v.z for v in pane if abs(abs(v.x) - (w / 2 - 0.05)) < 0.006)
        centre = max(v.z for v in pane if abs(v.x) < 0.01)
        self.assertGreaterEqual(centre - near, 0.03)
        self.assertAlmostEqual(centre, z1, delta=0.01)

    def test_frame_beads_exist(self):
        sc, steps = self.spec.d("showcase"), self.spec.d("ornaments")["showcase_frame"]["steps"]
        fb = self.spec.d("glass_look")["frame_beads"]
        h = self.spec.d("body")["w"] / 2
        y_apex = -h + 0.25 * 0.1 * sc["w"] - fb["r"]
        apex = [v for v in self.verts if abs(v.y - y_apex) < 1e-4 and abs(v.x) < sc["w"] / 2 and sc["z0"] < v.z < sc["z1"]]
        self.assertGreaterEqual(len(apex), 100)

    def test_hood_arch_projects_from_head_face(self):
        from mathutils import Vector
        ha, dl = self.spec.d("hood_arch"), self.spec.d("dial")
        hw = self.spec.d("head_box")["w"] / 2
        z = dl["z"] + (ha["r_inner"] + ha["r_outer"]) / 2           # inside the arch band at the top
        bpy.context.view_layer.update()
        hit, loc, *_ = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, Vector((0, -5, z)), Vector((0, 1, 0)), distance=10)
        self.assertTrue(hit)
        self.assertGreaterEqual(-hw - loc.y, ha["depth"] - 0.02)
        hit, loc, *_ = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, Vector((5, 0, z)), Vector((-1, 0, 0)), distance=10)
        self.assertTrue(hit)
        self.assertGreaterEqual(loc.x - hw, ha["depth"] - 0.02)

    def test_dial_has_numerals_around_it(self):
        dl = self.spec.d("dial")
        h = self.spec.d("body")["w"] / 2
        plane = -(h + dl["proud"]) - 0.006
        sectors = set()
        for v in self.verts:
            if abs(v.y - plane) < 1e-4 and abs(v.x) < 0.4:
                dx, dz = v.x, v.z - dl["z"]
                r = math.hypot(dx, dz)
                if 0.18 < r < dl["r"]:
                    sectors.add(int(round(math.degrees(math.atan2(dx, dz)) / 30)) % 12)
        self.assertEqual(len(sectors), 12)

    def test_pedestal_arch_is_open(self):
        # Rays through the middle of each side (x = 0 / y = 0) must pass the whole pedestal: faces, not vertices.
        from mathutils import Vector
        ped = self.spec.d("pedestal")
        z = (ped["z0"] + ped["arch"]["z1"]) / 2
        bpy.context.view_layer.update()
        for origin, direction in ((Vector((0, -5, z)), Vector((0, 1, 0))), (Vector((-5, 0, z)), Vector((1, 0, 0)))):
            hit, *_ = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, origin, direction, distance=10)
            self.assertFalse(hit, f"something blocks the gap between the legs at z {z:.2f}")


class ExportTest(unittest.TestCase):
    def test_export_single_part(self):
        photo_lib.al.clear_scene()
        parts = load_build().build(photo_lib.Spec(ASSET / "spec.json"))
        with tempfile.TemporaryDirectory() as tmp:
            photo_lib.bake_shared_and_export(parts, {"body": (0, 0, 0)}, tmp, "T", res=128, samples=1)
            self.assertEqual(sorted(p.name for p in Path(tmp).iterdir()), ["T.png", "T_body.obj", "T_parts.json"])


if __name__ == "__main__":
    unittest.main(argv=["x"])
