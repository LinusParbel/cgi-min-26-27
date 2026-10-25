# Flat pedestrian blockout candidate

Intended metric route: Hannover Hauptbahnhof → Kröpcke → Steintor. Source buildings are official GroundSurface polygons and CityGML-derived massing. Opening edges and route proposal are manually interpreted official orthophoto coordinates, not surveyed.

Upper floor H54 / engine Y−1 and lower floor 3m below it are blockout assumptions. Intended lane spacing 1.5m with player halfwidth 0.3m means swept halfwidth 1.8m. Require additional building clearance 0.3m and opening clearance 0.5m. Preserve source footprints, opening polygons and route order.

The original upper NW promenade route is disconnected even at 0.25m grid, within 15m of the proposal. See retained `clearance-audit.json` and `diagnostic.png`. The exported route instead uses the SE upper corridor on the same pedestrian street. A third search explicitly permitted up to 40m proposal deviation. Original footprints and opening polygons remain unchanged.

`build.py` exports `out/map.json`: perforated upper paving, lower floor, walls, supported rails, original procedural texture, and per-building vertical normalization in a copied OBJ only. It validates the rounded quadratic route used by RoutePath (20% of shorter adjacent segment). Straight segments are subdivided to at most 15m to preserve broad turns. The actual route is approximately 714.276m. Minimum clearance from the full player tube is 1.038m to buildings and 1.074m to openings; clock clearance is 5.598m. See `REPORT.json` and `overview.png`.

One bounded usability revision increased the minimum runtime sampled turning radius from 1.962m to 4.576m. The actual C# RoutePath reports 52 nodes, length 714.27637m, maximum sampled curvature 0.21855/m, and zero reverse steps on either ±1.5m lane. Ground was regenerated and its complete tube support reverified. Previous assets and build script remain in `checkpoint-tight-bend/`.

Paving UVs intentionally repeat every 4m; render texture wrapping as Repeat. Dark rails sample the original paving texture's narrow dark edge. Guardrail spans crossing source building conflicts are clipped to retain physical support. Lower opening floors and vertical depth are visual blockout assumptions. Gray massing, beige paving and geometric rails are an architectural blockout, not photorealism or a surveyed terrain model.
