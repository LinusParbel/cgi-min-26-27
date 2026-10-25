"""Read exported meshes only; run from any directory with Python + repository deps."""
from pathlib import Path
import hashlib
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '.model-research/hannover_route/python_deps'))
import numpy as np
from shapely import transform
from shapely.affinity import translate, scale, rotate
from shapely.geometry import LineString, Polygon, shape
from shapely.ops import unary_union

A = ROOT / 'RunnerGame/Art/assets/hannover_public_realm'
OUT = A / 'out'


def projections(path):
    vertices, groups, group = [], {}, 'default'
    for line in path.read_text().splitlines():
        t = line.split()
        if not t:
            continue
        if t[0] == 'v':
            vertices.append(tuple(map(float, t[1:4])))
        elif t[0] in ('o', 'g'):
            group = t[1] if len(t) > 1 else 'default'
        elif t[0] == 'f':
            p = Polygon([(vertices[int(i.split('/')[0])-1][0],
                          vertices[int(i.split('/')[0])-1][2]) for i in t[1:]])
            if p.area > 1e-10:
                groups.setdefault(group, []).append(p)
    return {g: unary_union(p) for g, p in groups.items()}


def route_curve(route):
    controls = [np.array([p['x'], p['z']]) for p in route['points']]
    points, radii = [controls[0]], []
    for a, b, c in zip(controls, controls[1:], controls[2:]):
        trim = .2 * min(np.linalg.norm(a-b), np.linalg.norm(c-b))
        en = b + (a-b)/np.linalg.norm(a-b)*trim
        ex = b + (c-b)/np.linalg.norm(c-b)*trim
        points.append(en)
        for t in np.linspace(0, 1, max(4, math.ceil(2*trim/.05)))[1:]:
            points.append((1-t)**2*en + 2*(1-t)*t*b + t*t*ex)
        for t in np.linspace(0, 1, 101):
            velocity = 2*((1-t)*(b-en)+t*(ex-b))
            accel = 2*(ex-2*b+en)
            cross = abs(velocity[0]*accel[1]-velocity[1]*accel[0])
            if cross > 1e-8:
                radii.append(np.linalg.norm(velocity)**3/cross)
    points.append(controls[-1])
    return LineString(points), min(radii)


def main():
    route = json.loads((OUT/'route.json').read_text())
    curve, radius = route_curve(route)
    tube = curve.buffer(1.8, resolution=32)
    hero = projections(OUT/'KroepckeFacades.obj')
    hero_all = unary_union(list(hero.values()))
    clearances = {}
    for building in ['building_0271', 'building_0307']:
        footprint = unary_union([p for g, p in hero.items() if building in g])
        assert not footprint.is_empty, building
        assert footprint.intersection(tube).area < 1e-7, building
        clearances[building] = footprint.distance(tube)
    ground = unary_union(list(projections(OUT/'PedestrianGround.obj').values()))
    unsupported = tube.difference(ground).area
    assert unsupported < 1e-6
    features = json.loads((A.parent/'hannover_route/footprints.geojson').read_text())['features']
    source = unary_union([shape(f['geometry']) for f in features])
    source = transform(source, lambda c: np.column_stack((c[:, 0]-550000, 5803000-c[:, 1])))
    obstacles = unary_union([source, hero_all])
    tree_path = ROOT/'RunnerGame/Assets/Models/Umgebung/StreetTree/ENV_StreetTree.obj'
    tree = unary_union(list(projections(tree_path).values()))
    props = json.loads((OUT/'map.json').read_text())['sceneProps']
    distances = []
    tree_count = 0
    for prop in props:
        if prop['kind'] != 'tree':
            continue
        factor, yaw = prop.get('scale', 1), prop.get('yaw', 0)
        assert math.isfinite(factor) and factor > 0 and math.isfinite(yaw)
        assert math.isfinite(prop['x']) and math.isfinite(prop['z'])
        # Engine row-vector Y rotation maps X/Z as (x*cos+z*sin,-x*sin+z*cos).
        canopy = scale(tree, xfact=factor, yfact=factor, origin=(0, 0))
        canopy = rotate(canopy, -yaw, origin=(0, 0), use_radians=True)
        canopy = translate(canopy, prop['x'], prop['z'])
        assert canopy.intersection(obstacles).area < 1e-7, prop
        distances.append(canopy.distance(obstacles))
        tree_count += 1
    # Deliberately place an actual canopy inside the actual hero projection.
    target = hero_all.representative_point()
    blocked = translate(scale(tree, xfact=1.5, yfact=1.5, origin=(0, 0)), target.x, target.y)
    assert blocked.intersection(hero_all).area > 1e-5
    paths = [OUT/'route.json', OUT/'map.json', OUT/'KroepckeFacades.obj', OUT/'PedestrianGround.obj', tree_path]
    result = dict(status='PASS', routeLength_m=curve.length, minimumTurnRadius_m=radius,
                  playerTubeRadius_m=1.8, heroTubeClearances_m=clearances,
                  unsupportedTubeArea_m2=unsupported, treeCount=tree_count,
                  minimumFullTreeClearance_m=min(distances), blockedTreeNegativeDetected=True,
                  limitations='All-height horizontal projection; not a front-face or GPU visibility test.',
                  sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    destination = Path(__file__).with_name('v2-integration-checks.json')
    destination.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
