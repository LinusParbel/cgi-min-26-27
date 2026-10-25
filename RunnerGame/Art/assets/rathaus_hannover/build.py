"""Neues Rathaus Hannover ("High" level), built from spec.json.

Blender Z-up, metres. Static prop: the Maschteich facade faces -Y, origin = footprint centre on the ground.
Every number comes from spec.json; fix measurements there, never here.

Layout: ring of four wings (front, back, two sides) around two inner courtyards, joined by a central cross wing
under the dome block; every wing has its own hipped/pitched roof. Geometry is collected per material in Geo
accumulators and turned into one object per material.

Headless:  blender --background --factory-startup --python RunnerGame/Art/assets/rathaus_hannover/build.py -- [--preview out.png | --export]
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "lib"))
import photo_lib as pl  # noqa: E402

al = pl.al
bpy = pl.bpy

Z = (0.0, 0.0, 1.0)

FRONT_OPENINGS = []        # every window/door opening built on the Maschteich front (filled by build(), read by the tests)


class Geo:
    """Vertex/face accumulator; closed solids get their normals recalculated, flat decals (recalc=False) keep order."""

    def __init__(self, name, mat, recalc=True):
        self.name, self.mat, self.recalc = name, mat, recalc
        self.v, self.f = [], []

    def solid(self, verts, faces):
        b = len(self.v)
        self.v += [tuple(p) for p in verts]
        self.f += [tuple(b + i for i in face) for face in faces]

    def extrude(self, poly, vec):
        """Prism: closed polygon (convex, 3D, coplanar) swept by vec."""
        k = len(poly)
        top = [(x + vec[0], y + vec[1], z + vec[2]) for x, y, z in poly]
        faces = [tuple(range(k)), tuple(range(2 * k - 1, k - 1, -1))]
        faces += [(i, (i + 1) % k, k + (i + 1) % k, k + i) for i in range(k)]
        self.solid(list(poly) + top, faces)

    def box(self, x0, x1, y0, y1, z0, z1):
        self.extrude([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], (0, 0, z1 - z0))

    def frustum(self, cx, cy, z0, z1, w0, d0, w1, d1):
        """Rectangular frustum, or pyramid when w1 == 0."""
        base = [(cx + sx * w0 / 2, cy + sy * d0 / 2, z0) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        if w1 <= 0:
            self.solid(base + [(cx, cy, z1)], [(0, 3, 2, 1), (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)])
            return
        top = [(cx + sx * w1 / 2, cy + sy * d1 / 2, z1) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        self.solid(base + top, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])

    def roof(self, x0, x1, y0, y1, z0, z1, axis, hip):
        """Pitched roof over the plan x0..x1 x y0..y1, ridge along `axis`; hip = ridge inset at both ends
        (0 = gable ends)."""
        if axis == "y":
            sw = Geo("tmp", None)
            sw.roof(y0, y1, x0, x1, z0, z1, "x", hip)
            self.solid([(y, x, z) for x, y, z in sw.v], [f[::-1] for f in sw.f])
            return
        cy = (y0 + y1) / 2
        v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0 + hip, cy, z1), (x1 - hip, cy, z1)]
        self.solid(v, [(0, 3, 2, 1), (0, 1, 5, 4), (1, 2, 5), (2, 3, 4, 5), (3, 0, 4)])

    def lathe(self, cx, cy, profile, seg=16, phase=0.0, rib=None):
        """Solid of revolution about Z through (cx, cy); profile = [(radius, z)] bottom to top (radius 0 = apex).
        rib = (height, every) pushes every second vertex of a ring outwards (raised ribs)."""
        v, rings, f = [], [], []
        for r, z in profile:
            if r <= 1e-6:
                rings.append(("apex", len(v)))
                v.append((cx, cy, z))
            else:
                rings.append(("ring", len(v)))
                for i in range(seg):
                    rr = r + (rib if rib and i % 2 == 0 else 0.0)
                    a = phase + 2 * math.pi * i / seg
                    v.append((cx + rr * math.cos(a), cy + rr * math.sin(a), z))
        for (ka, a), (kb, b) in zip(rings, rings[1:]):
            for i in range(seg):
                j = (i + 1) % seg
                if ka == "ring" and kb == "ring":
                    f.append((a + i, a + j, b + j, b + i))
                elif ka == "apex":
                    f.append((a, b + j, b + i))
                else:
                    f.append((a + i, a + j, b))
        for kind, base in (rings[0], rings[-1]):
            if kind == "ring":
                f.append(tuple(base + i for i in range(seg)))
        self.solid(v, f)

    def decal(self, pts):
        """One flat polygon, vertex order as given (counter-clockwise seen from outside)."""
        self.solid(pts, [tuple(range(len(pts)))])

    def to_object(self):
        import bmesh
        me = bpy.data.meshes.new(self.name)
        me.from_pydata(self.v, [], self.f)
        me.update()
        if self.recalc:
            bm = bmesh.new()
            bm.from_mesh(me)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(me)
            bm.free()
        o = bpy.data.objects.new(self.name, me)
        bpy.context.scene.collection.objects.link(o)
        me.materials.append(self.mat)
        return o


class Plane:
    """Facade plane: origin (ox, oy), horizontal axis u, outward normal n (u x Z = n, so decals face outward)."""

    def __init__(self, ox, oy, u, n):
        self.o, self.u, self.n = (ox, oy), u, n

    def pt(self, pu, pv, off=0.0):
        return (self.o[0] + self.u[0] * pu + self.n[0] * off, self.o[1] + self.u[1] * pu + self.n[1] * off, pv)

    def prism(self, g, pts, off0, off1):
        g.extrude([self.pt(pu, pv, off0) for pu, pv in pts], (self.n[0] * (off1 - off0), self.n[1] * (off1 - off0), 0))

    def decal(self, g, pts, off):
        g.decal([self.pt(pu, pv, off) for pu, pv in pts])


def arch_outline(cx, zb, w, h, n):
    """Convex (u, z) outline of a rectangle with a semicircular top, counter-clockwise, sill at zb, height h."""
    r = w / 2
    zs = zb + h - r
    pts = [(cx - r, zb), (cx + r, zb)]
    pts += [(cx + r * math.cos(math.pi * i / n), zs + r * math.sin(math.pi * i / n)) for i in range(n + 1)]
    return pts


def head_outline(cx, zb, w, zt, n, spring=None):
    """Convex (u, z) outline, counter-clockwise: rectangle with a semicircular (or elliptic) head, sill zb, top zt."""
    a = w / 2
    zs = zt - a if spring is None else spring
    b = zt - zs
    pts = [(cx - a, zb), (cx + a, zb)]
    return pts + [(cx + a * math.cos(math.pi * i / n), zs + b * math.sin(math.pi * i / n)) for i in range(n + 1)]


def rect_outline(x0, z0, x1, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def circle_outline(cx, cz, r, n):
    return [(cx + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def sides_of(cx, cy, hx, hy):
    """The four facade planes of an axis-aligned box centred at (cx, cy), starting at the front (-Y)."""
    return [Plane(cx, cy - hy, (1, 0), (0, -1)), Plane(cx + hx, cy, (0, 1), (1, 0)),
            Plane(cx, cy + hy, (-1, 0), (0, 1)), Plane(cx - hx, cy, (0, -1), (-1, 0))]


def build(spec):
    d, c = spec.d, spec.c
    FRONT_OPENINGS.clear()
    mat = {
        "stone": al.material("stone", c("stone"), **d("stone_weathering")),
        "roof": al.material("roof", c("roof"), dust=0.15, streaks=0.3, grime=0.2, scratches=0.1, mottle=0.25),
        "copper": al.material("copper", c("copper"), dust=0.1, streaks=0.4, grime=0.1, scratches=0.05, mottle=0.45),
        "window": al.flat("window", c("window")),
        "clock": al.flat("clock", c("clock")),
    }
    S, R, C = Geo("stone", mat["stone"]), Geo("roof", mat["roof"]), Geo("copper", mat["copper"])
    DOME, CAP = Geo("dome", mat["copper"]), Geo("dome_cap", mat["copper"])
    WS = Geo("windows_solid", mat["window"])
    WF = Geo("windows", mat["window"], recalc=False)
    CK = Geo("clock", mat["clock"])
    geos = [S, R, C, DOME, CAP, WS, WF, CK]

    W, D = d("width"), d("depth")
    hw, hd = W / 2, D / 2
    fy = -hd
    wd = d("wing_d")
    eave, ridge = d("wing_eave_h"), d("wing_roof_h")
    proj = d("corner_proj")
    cw, cf = d("center_w"), d("center_fwd")
    crw = d("cross_w") / 2
    tw, tx = d("tower_w"), d("tower_x")
    pw = d("pav_w")
    dy = d("dome_y")
    rows = d("window_rows_h")
    ww, wh = d("window_w"), d("window_h")
    nA = int(d("arch_pts"))
    co, chh = d("cornice_out"), d("cornice_h")
    inner_x = hw - wd                                          # inner face of the side wings (x)
    inner_y = hd - wd                                          # inner face of front/back wings (|y|)

    # ---------------------------------------------------------------- helpers
    def win(plane, pu, zb, w, h, framed=False, off=0.03):
        """Dark arched window on a facade; framed = stone surround standing proud, window in front of it."""
        if framed:
            z0 = max(0.0, zb - 0.2)
            plane.prism(S, arch_outline(pu, z0, w + 0.55, h + 0.2 + zb - z0, nA), -0.1, 0.18)
            off = 0.2
        plane.decal(WF, arch_outline(pu, zb, w, h, nA), off)

    def window_rows(plane, centres, w=ww, h=wh, rws=None, framed=False):
        for pu in centres:
            for r in (rws if rws is not None else rows):
                win(plane, pu, r - h / 2, w, h, framed)

    def spaced(length, pitch, skip=()):
        n = int(length // pitch)
        m = (length - n * pitch) / 2
        return [m + (k + 0.5) * pitch for k in range(n) if not any(a <= m + (k + 0.5) * pitch <= b for a, b in skip)]

    def band(plane, u0, u1, z, h, out):
        plane.prism(S, [(u0, z - h), (u1, z - h), (u1, z), (u0, z)], -0.1, out)

    def stepped_gable(plane, pu, z0, z1, w0, w1, steps, thick, finial_h):
        """Stepped stone gable standing on z0 at plane origin line, narrowing from w0 to w1, finial pyramid on top."""
        sh = (z1 - finial_h - z0) / steps
        for i in range(steps):
            w = w0 - i * (w0 - w1) / max(1, steps - 1)
            plane.prism(S, [(pu - w / 2, z0 + i * sh), (pu + w / 2, z0 + i * sh), (pu + w / 2, z0 + (i + 1) * sh),
                            (pu - w / 2, z0 + (i + 1) * sh)], -thick, 0.1)
            plane.prism(S, [(pu - w / 2 - 0.25, z0 + (i + 1) * sh - 0.3), (pu + w / 2 + 0.25, z0 + (i + 1) * sh - 0.3),
                            (pu + w / 2 + 0.25, z0 + (i + 1) * sh), (pu - w / 2 - 0.25, z0 + (i + 1) * sh)], -thick, 0.25)
        px, py, _ = plane.pt(pu, 0, -thick / 2)
        C.frustum(px, py, z1 - finial_h, z1, 0.9, 0.9, 0, 0)

    def pinnacle(px, py, z0, z1, w, cap_h):
        S.box(px - w / 2, px + w / 2, py - w / 2, py + w / 2, z0, z1 - cap_h)
        C.frustum(px, py, z1 - cap_h, z1, w * 1.25, w * 1.25, 0, 0)

    # ---------------------------------------------------------------- wings, ring around two courtyards
    S.box(-hw, hw, fy, fy + wd, 0, eave)                           # front wing
    S.box(-hw, hw, hd - wd, hd, 0, eave)                           # back wing
    for s in (-1, 1):
        S.box(min(s * hw, s * inner_x), max(s * hw, s * inner_x), -inner_y, inner_y, 0, eave)   # side wings
    S.box(-crw, crw, -inner_y, inner_y, 0, eave)                   # central cross wing through the dome block
    rise = ridge - eave
    R.roof(-hw, hw, fy, fy + wd, eave, ridge, "x", wd / 2)
    R.roof(-hw, hw, hd - wd, hd, eave, ridge, "x", wd / 2)
    for s in (-1, 1):
        R.roof(min(s * hw, s * inner_x), max(s * hw, s * inner_x), -(hd - wd / 2), hd - wd / 2, eave, ridge, "y", 0)
    R.roof(-crw, crw, -(hd - wd / 2), hd - wd / 2, eave, ridge, "y", 0)

    # ---------------------------------------------------------------- central projection
    yc = fy - cf
    ce, ch, cre = d("center_eave_h"), d("center_h"), d("center_roof_h")
    S.box(-cw / 2, cw / 2, yc, fy + wd - 3, 0, ce)
    R.roof(-cw / 2, cw / 2, yc + 0.6, fy + wd - 9, ce, cre, "y", 0)
    pc = Plane(0, yc, (1, 0), (0, -1))
    for s in (-1, 1):
        pinnacle(s * (cw / 2 - 0.8), yc + 0.8, ce - 1.0, d("center_corner_pinnacle_h"), d("center_pinnacle_w"), 3.0)

    # ---------------------------------------------------------------- front wings: dormers, windows, bands
    pf = Plane(0, fy, (1, 0), (0, -1))
    xs_mid = [s * (d("dormer_x0") + i * d("dormer_pitch")) for s in (-1, 1) for i in range(3)]
    dz, dg, dw = d("dormer_z"), d("dormer_gable_h"), d("dormer_w")
    for sy in (-1, 1):
        pl_ = Plane(0, sy * hd, (1, 0), (0, -1)) if sy < 0 else Plane(0, sy * hd, (-1, 0), (0, 1))
        for x in xs_mid:
            u = pl_.u[0]
            pu = x * u
            pl_.prism(S, [(pu - dw / 2, eave - 0.2), (pu + dw / 2, eave - 0.2), (pu + dw / 2, dz), (pu - dw / 2, dz)], -5.0, 0.0)
            pl_.prism(R, [(pu - dw / 2, dz), (pu + dw / 2, dz), (pu, dg - 0.5)], -5.0, -0.4)
            pl_.prism(S, [(pu - dw / 2 - 0.15, dz), (pu + dw / 2 + 0.15, dz), (pu, dg)], -0.4, 0.35)
            pl_.prism(S, [(pu - dw / 2 - 0.3, dz - 0.3), (pu + dw / 2 + 0.3, dz - 0.3), (pu + dw / 2 + 0.3, dz),
                          (pu - dw / 2 - 0.3, dz)], -0.4, 0.45)
            if sy > 0:
                win(pl_, pu, eave + 0.5, dw * 0.45, dz - eave - 0.9, False, 0.03)
            px, py, _ = pl_.pt(pu, 0, 0.2)
            C.frustum(px, py, dg, dg + 0.9, 0.5, 0.5, 0, 0)
    # small copper turrets on the wing roofs
    stw, sth = d("small_turret_w"), d("small_turret_h")
    for s in (-1, 1):
        for x_ in d("small_turret_xs"):                    # measured on the front (Maschteich) wing
            pinnacle(s * x_, -(hd - wd / 2), ridge - 1.5, sth, stw, 2.6)
        pinnacle(s * d("small_turret_xs")[0], hd - wd / 2, ridge - 1.5, sth, stw, 2.6)
    for s in (-1, 1):
        pinnacle(s * (inner_x + wd / 2), 0.0, ridge - 1.5, sth, stw, 2.6)

    # ---------------------------------------------------------------- corner towers
    ctd = d("corner_tower_detail")
    body, tip = d("tower_body_h"), d("tower_tip_h")
    bw = ctd["body_w"]
    cr, bl, fg, rp = ctd["crown"], ctd["belfry"], ctd["front_gable"], ctd["roof"]["profile"]
    lt, cp, sp_, vn = ctd["lantern"], ctd["cap"]["profile"], ctd["spire"], ctd["vane"]
    up = d("tower_upper_rows")
    bw2 = bl["w"]
    for s in (-1, 1):
        cx_, cy_ = s * tx, fy - proj + bw / 2
        S.box(cx_ - bw / 2, cx_ + bw / 2, cy_ - bw / 2, cy_ + bw / 2, 0, cr["z1"])
        # projecting crown on a row of corbels
        ov = cr["overhang"]
        ch_c = 0.9
        S.box(cx_ - bw / 2 - ov, cx_ + bw / 2 + ov, cy_ - bw / 2 - ov, cy_ + bw / 2 + ov, cr["z0"] + ch_c, cr["z1"])
        nc = int(cr["corbels"])
        for i, pl2 in enumerate(sides_of(cx_, cy_, bw / 2, bw / 2)):
            for k in range(nc):
                u = (k + 0.5) * bw / nc - bw / 2
                pl2.prism(S, [(u - 0.28, cr["z0"] + ch_c), (u + 0.28, cr["z0"] + ch_c), (u + 0.12, cr["z0"]),
                              (u - 0.12, cr["z0"])], -0.1, ov * 0.85)
            if i:                                              # the front (i == 0) comes from front_layout
                window_rows(pl2, (0.0,), w=1.5, h=3.0, rws=rows + up)
        # belfry with two arched openings per face, pointed stone gables with round window and corner figures
        S.box(cx_ - bw2 / 2, cx_ + bw2 / 2, cy_ - bw2 / 2, cy_ + bw2 / 2, bl["z0"], bl["z1"])
        op = bl["openings"]
        for pl2 in sides_of(cx_, cy_, bw2 / 2, bw2 / 2):
            for dx in op["dx"]:
                win(pl2, dx, op["z0"], op["w"], op["z1"] - op["z0"], False, 0.03)
            pl2.prism(S, [(-fg["w"] / 2, fg["z0"]), (fg["w"] / 2, fg["z0"]), (0, fg["apex_z"])], -0.8, 0.15)
            rw = fg["round_window"]
            pl2.decal(WF, circle_outline(0.0, rw["z"], rw["r"], 12), 0.17)
            for sg in (-1, 1):
                u0, u1 = sorted((sg * (fg["w"] / 2 - 0.55), sg * (fg["w"] / 2 + 0.05)))
                pl2.prism(S, rect_outline(u0, fg["z0"], u1, fg["z0"] + fg["corner_figures_h"]), -0.3, 0.3)
        # square flaring (concave) copper roof, one frustum per profile segment
        for (za, wa), (zb, wb) in zip(rp, rp[1:]):
            C.frustum(cx_, cy_, za, zb, wa, wa, wb, wb)
        # open lantern: arched opening per face, gallery ring, corner posts
        lw_, lz0, lz1 = lt["w"], lt["z0"], lt["z1"]
        S.box(cx_ - lw_ / 2, cx_ + lw_ / 2, cy_ - lw_ / 2, cy_ + lw_ / 2, lz0, lz1)
        gl = lt["gallery"]
        S.box(cx_ - gl["w"] / 2, cx_ + gl["w"] / 2, cy_ - gl["w"] / 2, cy_ + gl["w"] / 2, gl["z"], gl["z"] + gl["h"])
        S.box(cx_ - lw_ / 2 - 0.15, cx_ + lw_ / 2 + 0.15, cy_ - lw_ / 2 - 0.15, cy_ + lw_ / 2 + 0.15, lz1 - 0.3, lz1)
        for ix in (-1, 1):
            for iy in (-1, 1):
                S.box(cx_ + ix * (lw_ / 2 - 0.1) - 0.2, cx_ + ix * (lw_ / 2 - 0.1) + 0.2,
                      cy_ + iy * (lw_ / 2 - 0.1) - 0.2, cy_ + iy * (lw_ / 2 - 0.1) + 0.2, lz0, lz1 - 0.3)
        for pl2 in sides_of(cx_, cy_, lw_ / 2, lw_ / 2):
            win(pl2, 0.0, lt["arches"]["z0"], lt["arches"]["w"], lt["arches"]["z1"] - lt["arches"]["z0"], False, 0.03)
        # ogee copper cap, thin spire, flat weather-vane plate up to the measured tip height
        C.lathe(cx_, cy_, [(w_ / 2, z_) for z_, w_ in cp], seg=12)
        vh = vn["z1"] - vn["z0"]
        C.lathe(cx_, cy_, [(sp_["w0"] / 2, sp_["z0"]), (0.04, tip - vh)], seg=8)
        C.box(cx_ - vn["w"] / 2, cx_ + vn["w"] / 2, cy_ - 0.03, cy_ + 0.03, tip - vh, tip)

    # ---------------------------------------------------------------- end pavilions with stepped gables
    pe, pg = d("pav_eave_h"), d("pav_gable_h")
    for sx in (-1, 1):
        for sy in (-1, 1):
            x0, x1 = sorted((sx * (hw - pw), sx * hw))          # flush with the facade edge (photo), only the front projects
            y0, y1 = (fy - proj, fy + wd) if sy < 0 else (hd - wd, hd + proj)
            S.box(x0, x1, y0, y1, 0, pe)
            R.roof(x0, x1, y0 + 0.6 if sy < 0 else y0, y1 if sy < 0 else y1 - 0.6, pe, d("pav_roof_h"), "y", 0)
            pp = Plane((x0 + x1) / 2, y0 if sy < 0 else y1, (1, 0) if sy < 0 else (-1, 0), (0, sy))
            prof = d("pav_gable_profile")                           # measured gable profile (front and back):
            for (za, wa), (zb, wb) in zip(prof, prof[1:]):          # one trapezoid per segment, so the outline
                pp.prism(S, [(-wa / 2, za), (wa / 2, za), (wb / 2, zb), (-wb / 2, zb)], -0.8, 0.0)   # narrows smoothly
            band(pp, -pw / 2 - 0.3, pw / 2 + 0.3, pe, chh, co)
            if sy > 0:                                         # the front pavilions come from front_layout
                window_rows(pp, [u - pw / 2 for u in spaced(pw, d("window_pitch"))])
            ps = Plane(sx * hw, y0 if sx > 0 else y1, (0, sx), (sx, 0))
            window_rows(ps, spaced(y1 - y0, d("side_pitch")))

    # ---------------------------------------------------------------- Maschteich front from spec front_layout
    fl = d("front_layout")
    pT = Plane(0, fy - proj, (1, 0), (0, -1))                   # tower and pavilion fronts
    FR, DEP = 0.25, 0.35                                         # stone frame width, reveal depth

    def mir(xs):
        return sorted({round(x, 3) for x in xs} | {round(-x, 3) for x in xs})

    def ring(plane, inner, outer, off0, off1):
        """Closed stone ring between two outlines of equal point count, from off0 to off1."""
        k = len(inner)
        v = ([plane.pt(u, z, off0) for u, z in inner] + [plane.pt(u, z, off1) for u, z in inner] +
             [plane.pt(u, z, off0) for u, z in outer] + [plane.pt(u, z, off1) for u, z in outer])
        i0, i1, o0, o1 = 0, k, 2 * k, 3 * k
        f = []
        for i in range(k):
            j = (i + 1) % k
            f += [(i1 + i, i1 + j, o1 + j, o1 + i), (o0 + i, o0 + j, i0 + j, i0 + i),
                  (o0 + i, o0 + j, o1 + j, o1 + i), (i0 + i, i1 + i, i1 + j, i0 + j)]
        S.solid(v, f)

    def bar(plane, u0, u1, z0, z1, off0, off1):
        plane.prism(S, rect_outline(u0, z0, u1, z1), off0, off1)

    def opening(plane, x, z0, z1, w, shape, base=0.0, spring=None, frame=FR, depth=DEP, register=True):
        """Recessed opening: dark face on the wall, stone ring standing `depth` proud around it (reads as a reveal)."""
        n = 8
        if shape == "rect":
            def outl(g):
                return rect_outline(x - w / 2 - g, max(0.0, z0 - g), x + w / 2 + g, z1 + g)
        else:
            sp = spring if spring is not None else z1 - w / 2

            def outl(g):
                return head_outline(x, max(0.0, z0 - g), w + 2 * g, z1 + g, n, sp)
        inner = outl(0.0)
        if shape == "arch2":
            m = 0.3
            lw = (w - m) / 2 - 0.2
            lz = z1 - 0.7
            for sgn in (-1, 1):
                plane.decal(WF, head_outline(x + sgn * (m / 2 + 0.1 + lw / 2), z0, lw, lz, n), base + 0.03)
            bar(plane, x - m / 2, x + m / 2, z0, lz - lw / 2, base, base + depth)
        else:
            plane.decal(WF, inner, base + 0.03)
        ring(plane, inner, outl(frame), base, base + depth)
        if shape == "tracery":
            zs = z1 - w / 2
            mw_ = 0.26
            for mx in (-w / 4, 0.0, w / 4):
                bar(plane, x + mx - mw_ / 2, x + mx + mw_ / 2, z0, zs + 0.9, base, base + depth * 0.8)
            tz = z0 + 0.52 * (zs - z0)
            bar(plane, x - w / 2, x + w / 2, tz, tz + 0.3, base, base + depth * 0.8)
            for cx_, cz_, r_ in ((0.0, zs + 1.45, 1.0), (-w / 4 - 0.1, zs + 0.85, 0.62), (w / 4 + 0.1, zs + 0.85, 0.62)):
                ring(plane, [(x + cx_ + a, cz_ + b) for a, b in circle_outline(0, 0, r_, 12)],
                     [(x + cx_ + a, cz_ + b) for a, b in circle_outline(0, 0, r_ + 0.17, 12)], base, base + depth * 0.8)
        if register:
            FRONT_OPENINGS.append({"x": x, "z0": z0, "z1": z1, "w": w, "shape": shape, "y": round(plane.o[1], 3),
                                   "hw": w / 2 + frame + 0.05})

    def fband(plane, u0, u1, z, h, out):
        """Projecting band (top at z) that leaves the openings of this plane free."""
        y = round(plane.o[1], 3)
        cuts = sorted((o["x"] - o["hw"], o["x"] + o["hw"]) for o in FRONT_OPENINGS
                      if o["y"] == y and o["z0"] - 0.3 < z and o["z1"] + 0.3 > z - h
                      and o["x"] + o["hw"] > u0 and o["x"] - o["hw"] < u1)
        cur = u0
        for a, b in cuts:
            if a > cur + 0.05:
                band(plane, cur, a, z, h, out)
            cur = max(cur, b)
        if u1 > cur + 0.05:
            band(plane, cur, u1, z, h, out)

    cbl = fl["central_bays"]
    stair_n, stair_d, stair_w = int(fl["terrace"]["steps"]), fl["terrace"]["depth"], fl["terrace"]["w"]
    rise = 0.12
    z_floor = stair_n * rise
    en, bw, att, gb = cbl["entrance"], cbl["big_window"], cbl["attic_windows"], cbl["gable"]
    cz = cbl["cornice_z"]
    bays = mir(cbl["x"])
    piers = mir(cbl["pier_x"])
    pw_ = cbl["pier_w"]
    edges = [-cw / 2] + [e for p in piers for e in (p - pw_ / 2, p + pw_ / 2)] + [cw / 2]

    # terrace: broad stair in front of the central projection
    sd = stair_d / stair_n
    for j in range(stair_n):
        S.box(-stair_w / 2, stair_w / 2, yc - sd * (j + 1), yc - sd * j + 0.05, 0, rise * (stair_n - j))
    S.box(-cw / 2, cw / 2, yc, yc + 1.0, ce - 0.1, cz)           # attic parapet under the gables

    for bx in bays:
        opening(pc, bx, z_floor, en["z_top"], en["w"], "arch", spring=en["z_spring"])
        opening(pc, bx, bw["z0"], bw["z_top"], bw["w"], "tracery")
        for dx in att["dx"]:
            opening(pc, bx + dx, att["z0"], att["z1"], att["w"], "arch")
    # piers with statues, stepping 0.4 m forward
    z0s, z1s = cbl["statues"]["z0"], cbl["statues"]["z1"]
    for px_ in piers:
        bar(pc, px_ - pw_ / 2, px_ + pw_ / 2, 0, cz - 0.5, 0, 0.4)
        bar(pc, px_ - pw_ / 2 - 0.15, px_ + pw_ / 2 + 0.15, cz - 0.9, cz - 0.5, 0, 0.55)
        bar(pc, px_ - 0.5, px_ + 0.5, z0s, z0s + 0.55, 0.4, 1.0)
        bar(pc, px_ - 0.35, px_ + 0.35, z0s + 0.55, z1s - 0.7, 0.4, 0.95)
        bar(pc, px_ - 0.17, px_ + 0.17, z1s - 0.7, z1s, 0.45, 0.85)
    # balustrades between the piers (inner pier faces)
    inner_e = [edges[i] for i in range(len(edges))]
    spans = [(-cw / 2, piers[0] - pw_ / 2)] + [(piers[i] + pw_ / 2, piers[i + 1] - pw_ / 2) for i in range(len(piers) - 1)] \
        + [(piers[-1] + pw_ / 2, cw / 2)]
    bz0, bz1 = cbl["balustrade"]["z0"], cbl["balustrade"]["z1"]
    for u0, u1 in spans:
        if u1 - u0 < 5.0:
            continue
        u0, u1 = max(u0, -17.5), min(u1, 17.5)
        bar(pc, u0, u1, bz0, bz0 + 0.18, 0, 0.5)
        bar(pc, u0, u1, bz1 - 0.16, bz1, 0, 0.55)
        nb = int((u1 - u0) / 0.5)
        for k in range(nb):
            ux = u0 + (k + 0.5) * (u1 - u0) / nb
            bar(pc, ux - 0.1, ux + 0.1, bz0 + 0.18, bz1 - 0.16, 0.05, 0.35)
    gw, gz0, gzt, nw, nz = gb["w"], gb["z0"], gb["z_top"], gb["neck_w"], gb["neck_z"]
    nsl = 12

    def half(z):
        t = (z - gz0) / (nz - gz0)
        return nw / 2 + (gw / 2 - nw / 2) * (1 - t) ** 2.2
    for bx in bays:                                              # ogee gables with statue niche, pedestal and finial
        for k in range(nsl):
            za, zb_ = gz0 + (nz - gz0) * k / nsl, gz0 + (nz - gz0) * (k + 1) / nsl
            pc.prism(S, [(bx - half(za), za), (bx + half(za), za), (bx + half(zb_), zb_), (bx - half(zb_), zb_)], -0.8, 0.1)
        bar(pc, bx - nw / 2 - 0.3, bx + nw / 2 + 0.3, nz, nz + 0.25, -0.8, 0.3)
        bar(pc, bx - 0.6, bx + 0.6, nz + 0.25, nz + 1.0, -0.4, 0.3)
        fx, fy_, _ = pc.pt(bx, 0, -0.05)
        C.frustum(fx, fy_, nz + 1.0, gzt, 0.9, 0.9, 0, 0)
        opening(pc, bx, gb["niche_z0"], gb["niche_z1"], 2.4, "arch", base=0.1, register=False)
        bar(pc, bx - 0.45, bx + 0.45, gb["niche_z0"], gb["niche_z0"] + 0.4, 0.1, 0.5)
        bar(pc, bx - 0.35, bx + 0.35, gb["niche_z0"] + 0.4, gb["niche_z1"] - 1.3, 0.1, 0.45)
        bar(pc, bx - 0.17, bx + 0.17, gb["niche_z1"] - 1.3, gb["niche_z1"] - 0.75, 0.1, 0.4)

    # middle wing, towers, wing ends and pavilions
    mwg = fl["middle_wing"]
    for x in mir(mwg["x"]):
        for r in mwg["rows"]:
            opening(pf, x, r["z0"], r["z1"], r["w"], r["shape"])
        dwn = mwg["dormer_window"]
        opening(pf, x, dwn["z0"], dwn["z1"], dwn["w"], "arch", depth=0.3)
    for key, plane in (("tower_body", pT), ("wing_end", pf), ("pavilion", pT)):
        for x in mir(fl[key]["x"]):
            for r in fl[key]["rows"]:
                opening(plane, x, r["z0"], r["z1"], r["w"], r["shape"])
    gwn = fl["pavilion"]["gable_window"]
    for x in mir([gwn["x"]]):
        opening(pT, x, gwn["z0"], gwn["z1"], gwn["w"], gwn["shape"])

    # floor bands across the whole front, plus cornice and the old eave / string-course bands
    xp0, xp1 = hw - pw, hw + proj
    for z in fl["floor_bands_z"]:
        if z >= cz - 0.01:
            continue
        fband(pc, -cw / 2, cw / 2, z, 0.3, 0.25)
        if z <= eave:
            fband(pf, -(hw - pw), hw - pw, z, 0.3, 0.25)
        for s in (-1, 1):
            fband(pT, s * tx - tw / 2, s * tx + tw / 2, z, 0.3, 0.25)
            fband(pT, min(s * xp0, s * xp1), max(s * xp0, s * xp1), z, 0.3, 0.25)
    band(pc, -cw / 2 - 0.3, cw / 2 + 0.3, cz, 0.5, 0.5)
    fband(pf, -(hw - pw), hw - pw, eave, chh, co)
    fband(pf, -(hw - pw), hw - pw, d("string_course_z"), 0.6, co * 0.7)
    fband(pc, -cw / 2, cw / 2, d("string_course_z"), 0.6, co * 0.7)

    # ---------------------------------------------------------------- side, rear and courtyard facades
    sp = d("side_pitch")
    L = 2 * inner_y
    facs = [  # (origin x, origin y, u, n, length) for the right half; mirrored for the left
        (hw, -inner_y, (0, 1), (1, 0), L),                       # outer side
        (crw, -inner_y, (0, 1), (1, 0), L),                      # cross wing side into the courtyard
        (inner_x, inner_y, (0, -1), (-1, 0), L),                 # side wing into the courtyard
        (inner_x, -inner_y, (-1, 0), (0, 1), inner_x - crw),     # front wing back face
        (crw, inner_y, (1, 0), (0, -1), inner_x - crw),          # back wing front face
    ]
    for ox, oy, u, n, ln in facs:
        for mirror in (False, True):
            if mirror:
                ex_, ey_ = ox + u[0] * ln, oy + u[1] * ln
                pln = Plane(-ex_, ey_, (u[0], -u[1]), (-n[0], n[1]))
            else:
                pln = Plane(ox, oy, u, n)
            window_rows(pln, spaced(ln, sp))
    pb = Plane(hw - pw, hd, (-1, 0), (0, 1))                       # rear, between the pavilions
    window_rows(pb, spaced(W - 2 * pw, sp), framed=False)
    pb2 = Plane(0, hd, (-1, 0), (0, 1))
    band(pb2, -(hw - pw), hw - pw, eave, chh, co)
    band(pb2, -(hw - pw), hw - pw, d("string_course_z"), 0.6, co * 0.7)
    for s in (-1, 1):
        po = Plane(s * hw, 0, (0, s), (s, 0))
        band(po, -inner_y, inner_y, eave, chh, co)
        band(po, -inner_y, inner_y, d("string_course_z"), 0.6, co * 0.7)

    # ---------------------------------------------------------------- dome group
    db_w, db_e, db_t = d("domebase_w"), d("domebase_emerge_h"), d("domebase_top_h")
    dp, dpn = d("domebase_pediment_h"), d("domebase_pinnacle_h")
    h2 = db_w / 2
    S.box(-h2, h2, dy - h2, dy + h2, eave - 0.5, db_t - 1.0)
    S.box(-h2 - 0.8, h2 + 0.8, dy - h2 - 0.8, dy + h2 + 0.8, db_t - 1.0, db_t)
    S.box(-h2 - 0.5, h2 + 0.5, dy - h2 - 0.5, dy + h2 + 0.5, db_e - 0.6, db_e)
    dd = d("domebase_detail")
    clk_r, clk_z = dd["clock"]["r"], dd["clock"]["z"]
    fw = dd["frontispiece"]["w"]
    pw_d = dd["corner_pier_w"]
    cz_d = dd["cornice_z"]
    rel = 0.8                                                   # frontispiece / cornice projection
    for i, pl2 in enumerate(sides_of(0, dy, h2, h2)):
        tw_ = dd["tracery_window"]
        opening(pl2, 0.0, tw_["z0"], tw_["z1"], tw_["w"], "tracery", register=False)
        sw_ = dd["side_windows"]
        for x in mir(sw_["x"]):
            win(pl2, x, sw_["z0"], sw_["w"], sw_["z1"] - sw_["z0"], True)
        bz0, bz1 = dd["balustrade"]["z0"], dd["balustrade"]["z1"]
        ub = h2 - pw_d
        bar(pl2, -ub, ub, bz0, bz0 + 0.18, 0, 0.5)
        bar(pl2, -ub, ub, bz1 - 0.16, bz1, 0, 0.55)
        nb = int(2 * ub / 1.0)
        for k in range(nb):
            ux = -ub + (k + 0.5) * 2 * ub / nb
            bar(pl2, ux - 0.1, ux + 0.1, bz0 + 0.18, bz1 - 0.16, 0.05, 0.35)
        ga = dd["gallery_arches"]
        for x in mir(ga["side_x"]) + list(ga["centre_x"]):
            win(pl2, x, ga["z0"], ga["w"], ga["z1"] - ga["z0"], False, 0.03)
        # central frontispiece with the clock and a small pediment
        pl2.prism(S, rect_outline(-fw / 2, cz_d, fw / 2, dd["frontispiece"]["z1"]), -1.0, rel)
        pm = dd["pediment"]
        pl2.prism(S, [(-pm["w"] / 2, pm["z0"]), (pm["w"] / 2, pm["z0"]), (0, pm["z1"])], -0.6, rel + 0.2)
        n_ = 20
        ring_ = [(clk_r * math.cos(2 * math.pi * k / n_), clk_z + clk_r * math.sin(2 * math.pi * k / n_)) for k in range(n_)]
        pl2.prism(CK, ring_, rel, rel + 0.25)
        pl2.decal(WF, [(-0.12, clk_z), (0.12, clk_z), (0.12, clk_z + clk_r * 0.75), (-0.12, clk_z + clk_r * 0.75)], rel + 0.28)
        pl2.decal(WF, [(0.0, clk_z - 0.12), (clk_r * 0.55, clk_z - 0.12), (clk_r * 0.55, clk_z + 0.12), (0.0, clk_z + 0.12)], rel + 0.28)
        px, py, _ = pl2.pt(0, 0, 0.5)
        C.frustum(px, py, dp - 0.1, dp + 1.2, 0.9, 0.9, 0, 0)
    pin = h2 - d("domebase_pinnacle_inset")
    tr = dd["corner_turret"]
    for ix in (-1, 1):
        for iy in (-1, 1):
            xa, xb = sorted((ix * (h2 - pw_d), ix * (h2 + 0.3)))
            ya, yb = sorted((dy + iy * (h2 - pw_d), dy + iy * (h2 + 0.3)))
            S.box(xa, xb, ya, yb, dd["roof_emerge_z"], dd["corner_pier_top_z"])
            S.box(xa - 0.15, xb + 0.15, ya - 0.15, yb + 0.15, dd["corner_pier_top_z"] - 0.3, dd["corner_pier_top_z"])
            pinnacle(ix * pin, dy + iy * pin, dd["corner_pier_top_z"], dd["pinnacle_top_z"], d("domebase_pinnacle_w"), 2.4)
            tcx, tcy = ix * (h2 + 0.4 * tr["x_off"]), dy + iy * (h2 + 0.4 * tr["x_off"])
            S.lathe(tcx, tcy, [(tr["r"], tr["z0"]), (tr["r"], tr["z1"])], seg=12)
            tz = tr["z1"]
            C.lathe(tcx, tcy, [(tr["r"] * 1.1, tz), (tr["r"] * 1.15, tz + 0.3), (tr["r"] * 0.85, tz + 0.9),
                               (tr["r"] * 0.45, tz + 1.6), (tr["r"] * 0.12, tz + 2.2), (0, tz + 2.5)], seg=12)
    dbh, dm = d("dome_base_h"), d("dome_top_h")
    R_d = d("dome_w") / 2
    S.lathe(0, dy, [(R_d + 0.4, db_t), (R_d + 0.4, dbh - 0.01)], seg=24)           # drum under the dome
    l1w, l1t, l2w, l2t = d("lantern1_w"), d("lantern1_top_h"), d("lantern2_w"), d("lantern2_top_h")
    rt = l1w / 2 * 0.8
    ribs = int(d("dome_ribs"))
    prof = []
    for k in range(13):
        t = k / 12
        r = rt + (R_d - rt) * (1 - t ** 2.0) ** 0.6 * (1 + 0.05 * math.sin(math.pi * t))
        prof.append((r, dbh + (dm - dbh) * t))
    DOME.lathe(0, dy, prof, seg=2 * ribs, rib=d("dome_rib_h"))
    k8 = 1 / math.cos(math.pi / 8)
    S.lathe(0, dy, [(l1w / 2 * k8, dm - 0.2), (l1w / 2 * k8, l1t - 0.8)], seg=8, phase=math.pi / 8)
    S.lathe(0, dy, [(l1w / 2 * k8 + d("lantern_rim"), l1t - 0.8), (l1w / 2 * k8 + d("lantern_rim"), l1t)], seg=8, phase=math.pi / 8)
    S.lathe(0, dy, [(l2w / 2 * k8, l1t), (l2w / 2 * k8, l2t - 0.6)], seg=8, phase=math.pi / 8)
    S.lathe(0, dy, [(l2w / 2 * k8 + d("lantern_rim"), l2t - 0.6), (l2w / 2 * k8 + d("lantern_rim"), l2t)], seg=8, phase=math.pi / 8)
    lw1 = dd["lantern1_windows"]
    for pl2 in sides_of(0, dy, l1w / 2 * 0.99, l1w / 2 * 0.99):
        win(pl2, 0.0, lw1["z0"], lw1["w"], lw1["z1"] - lw1["z0"], False, 0.05)
    ob = dd["lantern1_obelisks"]
    ob_r = (l1w / 2 - ob["inset"] + 0.3) / math.sqrt(2)           # on the four diagonal faces of the octagon
    for ix in (-1, 1):
        for iy in (-1, 1):
            ox_, oy_ = ix * ob_r, dy + iy * ob_r
            S.box(ox_ - ob["w"] / 2, ox_ + ob["w"] / 2, oy_ - ob["w"] / 2, oy_ + ob["w"] / 2, dm + 0.5, ob["top_z"] - 0.8)
            C.frustum(ox_, oy_, ob["top_z"] - 0.8, ob["top_z"], ob["w"] * 1.3, ob["w"] * 1.3, 0, 0)
    g2 = dd["lantern2_gallery"]
    S.lathe(0, dy, [(g2["w"] / 2 * k8, g2["z"]), (g2["w"] / 2 * k8, g2["z"] + g2["h"])], seg=8, phase=math.pi / 8)
    ar = dd["lantern2_arcade"]
    cu = [(k - (ar["cols"] - 1) / 2) * 1.2 for k in range(ar["cols"])]
    for pl2 in sides_of(0, dy, l2w / 2 * 0.99, l2w / 2 * 0.99):
        for u in cu:                                            # open arcade: columns with dark arches between
            pl2.prism(S, rect_outline(u - ar["col_w"] / 2, ar["z0"], u + ar["col_w"] / 2, ar["z1"]), -0.2, 0.3)
        for a_, b_ in zip(cu, cu[1:]):
            win(pl2, (a_ + b_) / 2, ar["z0"] + 0.4, 0.75, ar["z1"] - ar["z0"] - 0.8, False, 0.05)
    ct, st = d("cap_top_h"), d("spire_tip_h")
    ch_ = ct - l2t
    c0, c1, c2, c3 = d("cap_profile")
    CAP.lathe(0, dy, [(l2w / 2 * c0, l2t), (l2w / 2 * c1, l2t + 0.15 * ch_), (l2w / 2 * c2, l2t + 0.45 * ch_),
                      (l2w / 2 * c3, l2t + 0.8 * ch_), (0.45, ct), (0.2, ct + (st - ct) * 0.35), (0, st)], seg=16)
    cobx, cobt, cobw = dd["cap_obelisks"]["x"][1], dd["cap_obelisks"]["top_z"], dd["cap_obelisks"]["w"]
    for ix in (-1, 1):                                          # obelisks beside the cap
        for iy in (-1, 1):
            ox_, oy_ = ix * cobx, dy + iy * cobx
            S.box(ox_ - cobw / 2, ox_ + cobw / 2, oy_ - cobw / 2, oy_ + cobw / 2, l2t - 0.3, cobt - 0.9)
            C.frustum(ox_, oy_, cobt - 0.9, cobt, cobw * 1.3, cobw * 1.3, 0, 0)
    fb_r, fb_z = dd["finial_ball"]["r"], dd["finial_ball"]["z"]
    CK.lathe(0, dy, [(0, fb_z - fb_r)] + [(fb_r * math.sin(math.pi * k / 7), fb_z - fb_r * math.cos(math.pi * k / 7))
                                         for k in range(1, 7)] + [(0, fb_z + fb_r)], seg=10)   # gold-ish finial ball

    # ---------------------------------------------------------------- landmarks (names from refs.json, ref/01.jpg)
    fz = dy - h2
    lm = {
        "facade_left_base": (-hw, fy, 0), "facade_right_base": (hw, fy, 0),
        "wing_l_eave": (-hw, fy, eave), "wing_r_eave": (hw, fy, eave),
        "spire_tip": (0, dy, st), "cap_top": (0, dy, ct),
        "lantern2_top_l": (-l2w / 2, dy - l2w / 2, l2t), "lantern2_top_r": (l2w / 2, dy - l2w / 2, l2t),
        "lantern1_top_l": (-l1w / 2, dy - l1w / 2, l1t), "lantern1_top_r": (l1w / 2, dy - l1w / 2, l1t),
        "dome_top": (0, dy, dm), "dome_base_l": (-R_d, dy, dbh), "dome_base_r": (R_d, dy, dbh),
        "domebase_top_l": (-h2, fz, db_t), "domebase_top_r": (h2, fz, db_t), "pediment_top": (0, fz, dp),
        "tower_l_tip": (-tx, fy + tw / 2, tip), "tower_r_tip": (tx, fy + tw / 2, tip),
        "tower_l_body_top_l": (-tx - tw / 2, fy, body), "tower_l_body_top_r": (-tx + tw / 2, fy, body),
        "tower_r_body_top_l": (tx + tw / 2, fy, body), "tower_r_body_top_r": (tx - tw / 2, fy, body),
        "pav_l_gable": (-(hw - pw / 2), fy, pg), "pav_r_gable": (hw - pw / 2, fy, pg),
        "pav_l_eave": (-hw, fy, pe), "pav_r_eave": (hw, fy, pe),
        "center_corner_l": (-(cw / 2 - 0.8), yc + 0.8, d("center_corner_pinnacle_h")),
        "center_corner_r": (cw / 2 - 0.8, yc + 0.8, d("center_corner_pinnacle_h")),
    }
    for name, loc in lm.items():
        pl.landmark(name, loc)

    return {"body": [g.to_object() for g in geos if g.v]}


def main(argv):
    al.clear_scene()
    spec = pl.Spec(HERE / "spec.json")
    parts = build(spec)
    if "--export" in argv:
        out = HERE / "out"
        pl.bake_shared_and_export({"body": parts["body"]}, {"body": (0, 0, 0)}, str(out.resolve()), "BLD_NeuesRathaus",
                                  res=int(spec.d("tex_res")), samples=32)
        return
    if "--preview" in argv:
        objs = [o for group in parts.values() for o in group]
        out = str(Path(argv[argv.index("--preview") + 1]).resolve())   # Blender resolves relative paths oddly
        al.render_previews(objs[0], out, size=512, extra_objects=objs[1:])


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
