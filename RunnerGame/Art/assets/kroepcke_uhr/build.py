"""Kroepcke-Uhr (Hannover), built from spec.json.

Blender Z-up, metres. Square plan, four identical faces; the origin is on the ground in the centre, the "front"
(the face the reference photos show) looks towards -Y. Every number comes from spec.json; fix measurements
there, never here.

Headless:  blender --background --factory-startup --python RunnerGame/Art/assets/kroepcke_uhr/build.py -- [--preview out.png | --export]
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "lib"))
import photo_lib as pl  # noqa: E402

al = pl.al


class Acc:
    """Plain polygon soup for one material. Faces are oriented by the direction they must face."""

    def __init__(self):
        self.v, self.f = [], []

    def vert(self, p):
        self.v.append(tuple(p))
        return len(self.v) - 1

    def face(self, idx, out):
        pts = [Vector(self.v[i]) for i in idx]
        n = Vector()
        for i in range(len(pts)):
            n += pts[i].cross(pts[(i + 1) % len(pts)])
        self.f.append(list(idx) if n.dot(Vector(out)) >= 0 else list(reversed(idx)))

    def quad(self, p0, p1, p2, p3, out):
        self.face([self.vert(p) for p in (p0, p1, p2, p3)], out)

    def convex(self, pts, faces):
        """Closed convex solid: every face points away from the centroid."""
        base = [self.vert(p) for p in pts]
        c = sum((Vector(p) for p in pts), Vector()) / len(pts)
        for fc in faces:
            fc_c = sum((Vector(pts[i]) for i in fc), Vector()) / len(fc)
            self.face([base[i] for i in fc], fc_c - c)

    def hexa(self, a, b):
        """Hexahedron from two quad rings a, b (4 points each, in ring order)."""
        pts = list(a) + list(b)
        faces = [(0, 1, 2, 3), (4, 5, 6, 7)] + [(i, (i + 1) % 4, 4 + (i + 1) % 4, 4 + i) for i in range(4)]
        self.convex(pts, faces)

    def box(self, x0, x1, y0, y1, z0, z1):
        self.hexa([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)],
                  [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)])

    def frustum(self, z0, z1, w0, w1, cx=0.0, cy=0.0):
        r0, r1 = w0 / 2, w1 / 2
        self.hexa([(cx - r0, cy - r0, z0), (cx + r0, cy - r0, z0), (cx + r0, cy + r0, z0), (cx - r0, cy + r0, z0)],
                  [(cx - r1, cy - r1, z1), (cx + r1, cy - r1, z1), (cx + r1, cy + r1, z1), (cx - r1, cy + r1, z1)])

    def lathe(self, profile, n, caps=True, cx=0.0, cy=0.0):
        """Surface of revolution round the Z axis; profile = [(radius, z), ...] bottom to top."""
        rings = []
        for r, z in profile:
            if r <= 1e-9:
                rings.append([self.vert((cx, cy, z))])
            else:
                rings.append([self.vert((cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n), z))
                              for i in range(n)])
        for k in range(len(profile) - 1):
            a, b = rings[k], rings[k + 1]
            for i in range(n):
                j = (i + 1) % n
                if len(a) > 1 and len(b) > 1:
                    idx = [a[i], a[j], b[j], b[i]]
                elif len(a) > 1:
                    idx = [a[i], a[j], b[0]]
                else:
                    idx = [a[0], b[j], b[i]]
                c = sum((Vector(self.v[q]) for q in idx), Vector()) / len(idx)
                self.face(idx, Vector((c.x - cx, c.y - cy, 0)))
        if caps:
            if len(rings[0]) > 1:
                self.face(rings[0], (0, 0, -1))
            if len(rings[-1]) > 1:
                self.face(rings[-1], (0, 0, 1))

    def prism(self, poly, ya, yb, back=True):
        """Polygon in the XZ plane (CCW seen from -Y) extruded from y=ya (front, more negative) to y=yb."""
        a = [self.vert((x, ya, z)) for x, z in poly]
        b = [self.vert((x, yb, z)) for x, z in poly]
        self.face(a, (0, -1, 0))
        if back:
            self.face(b, (0, 1, 0))
        for i in range(len(poly)):
            j = (i + 1) % len(poly)
            (x0, z0), (x1, z1) = poly[i], poly[j]
            self.face([a[i], a[j], b[j], b[i]], (z1 - z0, 0, -(x1 - x0)))

    def decal(self, poly, y):
        """Flat polygon facing -Y."""
        self.face([self.vert((x, y, z)) for x, z in poly], (0, -1, 0))

    def add_rotated(self, other, k):
        """Copy `other` rotated by k * 90 degrees about Z (k=0 front, 1 = the +X side, ...)."""
        c, s = [(1, 0), (0, 1), (-1, 0), (0, -1)][k % 4]
        off = len(self.v)
        for x, y, z in other.v:
            self.v.append((x * c - y * s, x * s + y * c, z))
        self.f += [[i + off for i in fc] for fc in other.f]

    def to_object(self, name, mat):
        me = bpy.data.meshes.new(name)
        me.from_pydata(self.v, [], self.f)
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='EAR_CLIP')
        bm.to_mesh(me)
        bm.free()
        me.update()
        o = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(o)
        if mat is not None:
            me.materials.append(mat)
        return o


def cyl(acc, c, axis, r, ln, n=12):
    """Cylinder with its axis along x or y, centred at c."""
    def P(a, u, v):
        return (c[0] + a, c[1] + u, c[2] + v) if axis == "x" else (c[0] + u, c[1] + a, c[2] + v)

    def N(u, v):
        return (0, u, v) if axis == "x" else (u, 0, v)

    ring = [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    for i in range(n):
        (u0, v0), (u1, v1) = ring[i], ring[(i + 1) % n]
        acc.quad(P(-ln / 2, u0, v0), P(-ln / 2, u1, v1), P(ln / 2, u1, v1), P(ln / 2, u0, v0), N(u0 + u1, v0 + v1))
    for a, o in ((-ln / 2, -1), (ln / 2, 1)):
        acc.face([acc.vert(P(a, u, v)) for u, v in ring], (o, 0, 0) if axis == "x" else (0, o, 0))


def annulus(acc, ri, ro, cz, yf, yb, n=48):
    """Ring round the axis (0, y, cz) facing -Y: front at yf, back at yb."""
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        am = (a0 + a1) / 2
        o0, o1 = (ro * math.cos(a0), ro * math.sin(a0)), (ro * math.cos(a1), ro * math.sin(a1))
        i0, i1 = (ri * math.cos(a0), ri * math.sin(a0)), (ri * math.cos(a1), ri * math.sin(a1))
        acc.quad((i0[0], yf, cz + i0[1]), (o0[0], yf, cz + o0[1]), (o1[0], yf, cz + o1[1]), (i1[0], yf, cz + i1[1]), (0, -1, 0))
        acc.quad((o0[0], yf, cz + o0[1]), (o1[0], yf, cz + o1[1]), (o1[0], yb, cz + o1[1]), (o0[0], yb, cz + o0[1]), (math.cos(am), 0, math.sin(am)))
        acc.quad((i0[0], yf, cz + i0[1]), (i1[0], yf, cz + i1[1]), (i1[0], yb, cz + i1[1]), (i0[0], yb, cz + i0[1]), (-math.cos(am), 0, -math.sin(am)))


def flute(acc, cx, cy, zb, h, w):
    """Organ-pipe flute: D-shaped column (round side towards -Y) with a tapered rounded top."""
    r = w / 2
    pts = [(cx + r * math.cos(math.pi + math.pi * i / 6), cy + r * math.sin(math.pi + math.pi * i / 6)) for i in range(7)]
    mx, my = cx, cy - r * 0.3
    secs = [(zb, 1.0), (zb + h - 0.02, 1.0), (zb + h - 0.008, 0.75), (zb + h, 0.4)]
    rings = [[acc.vert((mx + (x - mx) * k, my + (y - my) * k, z)) for x, y in pts] for z, k in secs]
    for a, b in zip(rings, rings[1:]):
        for i in range(len(pts)):
            j = (i + 1) % len(pts)
            idx = [a[i], a[j], b[j], b[i]]
            c = sum((Vector(acc.v[q]) for q in idx), Vector()) / 4
            acc.face(idx, (c.x - mx, c.y - my, 0))
    acc.face(rings[-1], (0, 0, 1))


def circle(cx, cz, r, n):
    return [(cx + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def bar(cx, cz, length, width, ang):
    """Quad starting at (cx, cz), `length` long in the direction ang (0 = up, clockwise positive)."""
    dx, dz = math.sin(ang), math.cos(ang)
    nx, nz = -dz * width / 2, dx * width / 2
    return [(cx + nx, cz + nz), (cx - nx, cz - nz), (cx - nx + dx * length, cz - nz + dz * length),
            (cx + nx + dx * length, cz + nz + dz * length)]


def star(cx, cz, ro, ri):
    return [(cx + (ro if i % 2 == 0 else ri) * math.cos(math.pi / 2 + i * math.pi / 5),
             cz + (ro if i % 2 == 0 else ri) * math.sin(math.pi / 2 + i * math.pi / 5)) for i in range(10)]


def shoulder_arch(w, z0, z1, seg=8):
    """Outline of the showcase: rectangle with shoulders and a round head (CCW from the front).
    Returns (outline, arc points left to right from angle 0 to 180 deg, shoulder height)."""
    cz = z1 - 0.3 * w
    zs = cz - 0.05
    arc = [(0.3 * w * math.cos(math.pi * i / seg), cz + 0.3 * w * math.sin(math.pi * i / seg)) for i in range(seg + 1)]
    return [(-w / 2, z0), (w / 2, z0), (w / 2, zs)] + arc + [(-w / 2, zs)], arc, zs


def build(spec):
    d, c = spec.d, spec.c
    mat = {"iron": al.material("iron", c("iron"), dust=0.15, streaks=0.25, grime=0.3, scratches=0.15, mottle=0.1),
           "dial": al.flat("dial", c("dial")), "glass": al.flat("glass", c("glass")), "gold": al.flat("gold", c("gold")),
           "iron_top": al.flat("iron_top", c("iron_top"))}
    S = {k: Acc() for k in mat}                      # whole clock, per material
    F = {k: Acc() for k in mat}                      # one face (front, -Y); copied 4x rotated into S

    body, ped, ledge = d("body"), d("pedestal"), d("ledge")
    h = body["w"] / 2                                # half width of the shaft
    pw, hp = body["pilaster_w"], body["w"] / 2 + body["pilaster_proud"]   # pilaster front plane at hp

    # --- plinth slab, pedestal (four feet + ring beam; the arches between the feet stay open), profiles
    for z0p, z1p, wp in d("plinth_slab")["steps"]:
        S["iron"].box(-wp / 2, wp / 2, -wp / 2, wp / 2, z0p, z1p)
    pe, feet = ped["w"] / 2, ped["feet_w"]
    arch_z1 = ped["arch"]["z1"]
    table_z = max(ped["z1"], ledge["profile"][0][0])
    orn = d("ornaments")
    pc = pe - feet / 2
    legs = [(sx * pc, sy * pc) for sx in (-1, 1) for sy in (-1, 1)] + [(0, -pc), (0, pc), (-pc, 0), (pc, 0)]
    prof = ped["baluster_profile"]
    for cx, cy in legs:                              # square waisted pillar (stacked frustums), square cap slab under the table
        for (za, wa), (zb, wb) in zip(prof, prof[1:]):
            S["iron"].frustum(za, zb, wa, wb, cx, cy)
        S["iron"].box(cx - feet / 2, cx + feet / 2, cy - feet / 2, cy + feet / 2, prof[-1][0] - 0.005, table_z)
    S["iron"].box(-pe, pe, -pe, pe, table_z - 0.035, table_z)   # apron joining the caps

    def stack(profile):
        for (za, wa), (zb, wb) in zip(profile, profile[1:]):
            S["iron"].frustum(za, zb, wa, wb)

    for (za, wa), (zb, wb) in zip(ledge["profile"], ledge["profile"][1:]):    # fascia in iron, the sloped top in iron_top
        (S["iron"] if abs(wa - wb) < 1e-9 else S["iron_top"]).frustum(za, zb, wa, wb)
    stack(d("body_base")["profile"])
    stack(d("wings")["profile"])
    head = d("head_box")
    S["iron"].box(-head["w"] / 2, head["w"] / 2, -head["w"] / 2, head["w"] / 2, head["z0"], head["z1"])
    stack(d("crown")["profile"])

    # --- round ribbed melon dome (profile = z, diameter) on a thin square foot plate
    cap = d("cap")
    crown_top = d("crown")["profile"][-1]
    stack([crown_top, [cap["profile"][0][0], cap["profile"][0][1]]])
    S["iron"].lathe([(dm / 2, z) for z, dm in cap["profile"]], 32)
    rw, lift = 0.03, cap["rib_proud"]
    for (za, da), (zb, db) in zip(cap["profile"], cap["profile"][1:]):
        ra, rb = da / 2, db / 2
        nr, nz = (zb - za), (ra - rb)                # outward normal of this segment in the (r, z) plane
        ln = math.hypot(nr, nz)
        nr, nz = nr / ln * lift, nz / ln * lift
        for i in range(cap["ribs"]):
            th = 2 * math.pi * i / cap["ribs"]
            c_, s_ = math.cos(th), math.sin(th)
            ring = []
            for r, z in ((ra, za), (rb, zb)):
                ring.append([(r * c_ + s_ * rw / 2, r * s_ - c_ * rw / 2, z), (r * c_ - s_ * rw / 2, r * s_ + c_ * rw / 2, z),
                             (r * c_ + nr * c_ - s_ * rw * 0.3, r * s_ + nr * s_ + c_ * rw * 0.3, z + nz),
                             (r * c_ + nr * c_ + s_ * rw * 0.3, r * s_ + nr * s_ - c_ * rw * 0.3, z + nz)])
            S["iron"].hexa(ring[0], ring[1])

    sr, sl = cap["corner_scrolls"]["r"], 0.12      # volute scrolls: horizontal cylinders along the face edge at the cap foot
    zf, wf = cap["profile"][0]
    for sx in (-1, 1):
        cx = sx * (wf / 2 - sl / 2 - 0.01)
        cy, cz = -wf / 2 - sr * 0.4, zf + sr
        xa, xb = cx - sl / 2, cx + sl / 2
        ringp = [(cy + sr * math.cos(2 * math.pi * i / 12), cz + sr * math.sin(2 * math.pi * i / 12)) for i in range(12)]
        for i in range(12):
            (y0, z0), (y1, z1) = ringp[i], ringp[(i + 1) % 12]
            F["iron"].quad((xa, y0, z0), (xa, y1, z1), (xb, y1, z1), (xb, y0, z0), (0, (y0 + y1) / 2 - cy, (z0 + z1) / 2 - cz))
        for x, o in ((xa, -1), (xb, 1)):
            F["iron"].face([F["iron"].vert((x, y, z)) for y, z in ringp], (o, 0, 0))

    # --- neck, ball and spike on the top
    ball, spike = d("ball"), d("spike")
    S["iron"].lathe([(ball["r"] * math.sin(math.pi * k / 12), ball["z"] - ball["r"] * math.cos(math.pi * k / 12))
                     for k in range(13)], 16, caps=False)
    fin = spike["finial"]                            # gilt finial of stacked lobes on the ball, then the thin rod
    lobes = [(0.4, 0.0), (1.0, 0.12), (0.45, 0.22), (0.8, 0.34), (0.35, 0.46), (0.55, 0.58), (0.25, 0.7), (0.35, 0.8), (0.15, 1.0)]
    S["gold"].lathe([(rf * fin["w"] / 2, spike["z0"] + zf * fin["h"]) for rf, zf in lobes], 12)
    S["iron"].lathe([(0.15 * fin["w"] / 2, spike["z0"] + fin["h"]), (0.0, spike["z1"])], 8)

    # --- shaft with the showcase recesses, corner pilasters
    sc = d("showcase")
    z0s, z1s, sw = sc["z0"], sc["z1"], sc["w"]
    t = 0.1 * sw                                     # recess depth: inset ~ 10 % of the width
    S["iron"].box(-h, h, -h, h, body["z0"], z0s)
    S["iron"].box(-h, h, -h, h, z1s, body["z1"])
    S["iron"].box(-(h - t), h - t, -(h - t), h - t, z0s, z1s)
    for sx in (-1, 1):
        for sy in (-1, 1):
            xa, xb = sorted((sx * hp, sx * (hp - pw)))
            ya, yb = sorted((sy * hp, sy * (hp - pw)))
            S["iron"].box(xa, xb, ya, yb, body["z0"], body["z1"])

    poly, arc, zs = shoulder_arch(sw, z0s, z1s)
    sf = orn["showcase_frame"]
    stp = sc["frame_w"] / sf["steps"]
    outlines = [shoulder_arch(sw - 2 * k * stp, z0s + k * stp, z1s - k * stp)[0] for k in range(sf["steps"] + 1)]
    inner = outlines[-1]
    yg = -h + t - 0.004
    planes = [-h + (k + 1) * 0.25 * t for k in range(sf["steps"])] + [yg]
    for sx in (-1, 1):                               # wall beside the recess
        xa, xb = sorted((sx * sw / 2, sx * h))
        F["iron"].box(xa, xb, -h, -h + t, z0s, z1s)
    right = [(sw / 2, zs), (sw / 2, z1s)] + list(reversed(arc[:len(arc) // 2 + 1]))   # shoulder filler beside the head
    F["iron"].prism(right, -h, -h + t, back=False)
    F["iron"].prism([(-x, z) for x, z in reversed(right)], -h, -h + t, back=False)

    def reveal(outline, ya, yb):
        for i in range(len(outline)):
            (x0, z0), (x1, z1) = outline[i], outline[(i + 1) % len(outline)]
            F["iron"].quad((x0, ya, z0), (x1, ya, z1), (x1, yb, z1), (x0, yb, z0), (-(z1 - z0), 0, x1 - x0))

    reveal(outlines[0], -h, planes[0])
    for k in range(sf["steps"]):                     # stepped frame: each step one plane deeper
        reveal(outlines[k + 1], planes[k], planes[k + 1])
        a, b = outlines[k], outlines[k + 1]
        for i in range(len(a)):
            j = (i + 1) % len(a)
            F["iron"].quad((a[i][0], planes[k], a[i][1]), (a[j][0], planes[k], a[j][1]),
                           (b[j][0], planes[k], b[j][1]), (b[i][0], planes[k], b[i][1]), (0, -1, 0))
    for sx in (-1, 1):                               # small scroll at each shoulder of the head
        cyl(F["iron"], (sx * (sw / 2 - 0.03), -h - 0.012, zs + 0.035), "x", 0.025, 0.07, n=8)
    F["glass"].decal(inner, yg)

    # --- pilaster ornaments (alternating relief figure / gilt star), medallions
    med = d("medallions")
    pf = orn["pilaster_figures"]
    px = hp - pw / 2
    for sx in (-1, 1):
        for k, z in enumerate(pf["z"]):
            if k % 2 == 0:
                r0 = pf["w"] / 2
                zt = z + pf["h"] / 2 - r0
                fig = [(sx * px - r0, z - pf["h"] / 2), (sx * px + r0, z - pf["h"] / 2)] + \
                      [(sx * px + r0 * math.cos(math.pi * i / 8), zt + r0 * math.sin(math.pi * i / 8)) for i in range(9)]
                F["iron"].prism(fig, -hp - pf["proud"], -hp + 0.005, back=False)
            else:
                F["gold"].decal(star(sx * px, z, 0.025, 0.011), -hp - 0.003)
    for x in med["x"]:
        F["iron"].prism(circle(x, med["z"], med["r"], 16), -hp - 0.015, -hp + 0.005, back=False)

    # --- dial: disc, thick ring, arched hood, hands, hour marks
    dl = d("dial")
    dz, dy = dl["z"], -(h + dl["proud"])
    F["dial"].prism(circle(0, dz, dl["r"], 48), dy, -h + 0.01, back=False)
    ring_front = dy - 0.02
    n = 48
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        am = (a0 + a1) / 2
        o0, o1 = (dl["ring_r"] * math.cos(a0), dl["ring_r"] * math.sin(a0)), (dl["ring_r"] * math.cos(a1), dl["ring_r"] * math.sin(a1))
        i0, i1 = (dl["r"] * math.cos(a0), dl["r"] * math.sin(a0)), (dl["r"] * math.cos(a1), dl["r"] * math.sin(a1))
        F["iron"].quad((i0[0], ring_front, dz + i0[1]), (o0[0], ring_front, dz + o0[1]),
                       (o1[0], ring_front, dz + o1[1]), (i1[0], ring_front, dz + i1[1]), (0, -1, 0))
        F["iron"].quad((o0[0], ring_front, dz + o0[1]), (o1[0], ring_front, dz + o1[1]),
                       (o1[0], -h, dz + o1[1]), (o0[0], -h, dz + o0[1]), (math.cos(am), 0, math.sin(am)))
        F["iron"].quad((i0[0], ring_front, dz + i0[1]), (i1[0], ring_front, dz + i1[1]),
                       (i1[0], dy, dz + i1[1]), (i0[0], dy, dz + i0[1]), (-math.cos(am), 0, -math.sin(am)))
    dh = d("dial_hood")                              # stepped concentric rings round the dial, the outer one most proud
    hr = orn["hood_rings"]
    yh0, yh1 = -head["w"] / 2 - dh["depth"], -head["w"] / 2 + 0.01
    edges = hr["radii"] + [hr["radii"][-1] - 0.05]
    for k in range(len(hr["radii"])):
        annulus(F["iron"], edges[k + 1], edges[k], dz, yh0 + k * hr["step_depth"], yh1)
    rh = dl["ring_r"] + 0.07
    cz_h = dl["arch_top_z"] - rh
    hood = [(-rh, dz + 0.17), (rh, dz + 0.17)] + [(rh * math.cos(math.pi * i / 16), cz_h + rh * math.sin(math.pi * i / 16))
                                                  for i in range(17)]
    F["iron"].prism(hood, -(h + 0.034), -head["w"] / 2 + 0.005, back=False)
    for ang, ln, wd in ((math.radians(-60), 0.17, 0.022), (math.radians(60), 0.25, 0.014)):
        F["iron"].decal(bar(0, dz, ln, wd, ang), dy - 0.004)
    F["iron"].decal(circle(0, dz, 0.018, 12), dy - 0.005)
    for k in range(12):
        a = math.radians(30 * k)
        r0 = dl["r"] - 0.075
        F["iron"].decal(bar(r0 * math.sin(a), dz + r0 * math.cos(a), 0.045, 0.012, a), dy - 0.004)

    ws = orn["wing_scrolls"]
    wz_top = d("wings")["profile"][1][0]
    wwid = d("wings")["profile"][1][1] / 2
    for sx in (-1, 1):                               # scroll at the outer tip of each flared bracket
        cyl(F["iron"], (sx * (wwid - ws["r"]), -wwid + 0.06, wz_top), "y", ws["r"], 0.12)

    for key in mat:
        for k in range(4):
            S[key].add_rotated(F[key], k)
    objs = [S[key].to_object("clock_" + key, mat[key]) for key in mat if S[key].f]

    # --- landmarks (names match refs.json, front = -Y)
    lw = ledge["profile"][1][1] / 2
    cw, cz0 = d("crown")["profile"][0][1] / 2, d("crown")["profile"][0][0]
    ww, wz = d("wings")["profile"][1][1] / 2, d("wings")["profile"][1][0]
    for name, loc in {
        "spike_tip": (0, 0, spike["z1"]), "ball_centre": (0, 0, ball["z"]),
        "crown_l": (-cw, -cw, cz0), "crown_r": (cw, -cw, cz0),
        "wing_l": (-ww, -ww, wz), "wing_r": (ww, -ww, wz),
        "dial_centre": (0, ring_front, dz),
        "body_l_bottom": (-h, -h, body["z0"]), "body_r_bottom": (h, -h, body["z0"]),
        "ledge_l": (-lw, -lw, ledge["profile"][1][0]), "ledge_r": (lw, -lw, ledge["profile"][1][0]),
        # ref/01.jpg (3/4 view: front face on the left, +X face on the right, near corner (+x, -y))
        "dial_side_centre": (-ring_front, 0, dz),           # +X face dial (ring_front is the front dial y < 0)
        "ledge_back_r": (lw, lw, ledge["profile"][1][0]),
        "ledge_near_bottom": (lw, -lw, ledge["profile"][0][0]),
        "plinth_near": (d("plinth_slab")["steps"][0][2] / 2, -d("plinth_slab")["steps"][0][2] / 2, 0.0),
        "crown_back_r": (cw, cw, cz0),
    }.items():
        pl.landmark(name, loc)
    return {"body": objs}


def main(argv):
    al.clear_scene()
    spec = pl.Spec(HERE / "spec.json")
    parts = build(spec)
    if "--export" in argv:
        out = HERE / "out"
        pl.bake_shared_and_export(parts, {"body": (0, 0, 0)}, str(out.resolve()), "PRP_KroepckeUhr",
                                  res=int(spec.d("tex_res")), samples=32)
        return
    if "--preview" in argv:
        objs = parts["body"]
        out = str(Path(argv[argv.index("--preview") + 1]).resolve())
        al.render_previews(objs[0], out, extra_objects=objs[1:])


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
