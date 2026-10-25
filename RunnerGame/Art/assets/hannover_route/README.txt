Official Hannover LoD2 route massing

This is a geographically positioned grey blockout, not a detailed current facade replica. It uses Landeshauptstadt Hannover CityGML LoD2, CC BY 4.0 International. CREDITS.txt is ready to merge into project credits. Publisher and licence HTML, retrieval log and hashes are archived in evidence/ and provenance.json. The publisher's German deed link is not a separate German licence port.

Source: 2010 laser survey, source modification 2024-12-05, publication 2026-01-20. Generalized roof shapes, stated height accuracy approximately +/-1 m. Source vertical datum is DE_DHHN92_NH. No facade textures or imagery pixels are used.

Coordinates: source EPSG:25832 metres. Engine X=E-550000, Y=H-55, Z=-(N-5803000). This is a proper rotation plus translation, preserving winding. Blender uses X=E-550000, Y=N-5803000, Z=H-55. Parent can translate the whole mesh without changing this source mapping.

Selection: all whole buildings whose source bounding box intersects longitude 9.7315..9.7445, latitude 52.3735..52.3785. Border buildings extend outside the rectangle. No ground mesh. 504 GML buildings, 54274 triangles. This is an area selection, not a street-centreline buffer. Buildings.json maps each OBJ object and Blender object to source GML ID, tile, ENH bounds and face range. Building IDs have no semantic station label. The corrected station-front reference is approximately E550420,N5803165; the earlier E550508,N5803296 reference was on the tracks, so building_0500 must not be identified as the station from that approximation.

Reproduce from repository root:
  python RunnerGame/Art/assets/hannover_route/fetch_sources.py
  python -m pip install --target .model-research/hannover_route/python_deps shapely==2.1.2 pyproj==3.7.1
  python RunnerGame/Art/assets/hannover_route/build.py
  python RunnerGame/Art/assets/hannover_route/validate.py
  blender --background --factory-startup --python-exit-code 1 --python RunnerGame/Art/assets/hannover_route/save_blend.py

The fetch script uses HTTP ranges and verifies original ZIP CRCs and extracted file SHA256 hashes. The original partial ZIP is only local research evidence; there is no asserted complete-archive hash. Build uses constrained Delaunay triangulation per projected polygon, including its holes, checks area equality and preserves source normals. OBJ readback validates indices, finiteness, nondegeneracy, unit flat normals and winding, opaque 512px authored grey texture and the 100k triangle budget. verification.json records output hashes.

HannoverRoute.blend preserves separate editable source buildings; out/ holds engine Y-up OBJ/MTL/PNG and parts.json. overview.png is a north-up geometry overview, not an orthophoto.

footprints.geojson contains all 504 selected buildings from actual CityGML GroundSurface polygons, retaining holes. Counts: GroundSurface=504, fallback=0. Coordinates are projected E,N metres in EPSG25832 (explicit legacy GeoJSON CRS, not RFC7946 lon/lat). Properties include original GML ID, OBJ object name, source tile, ground height min/max in DE_DHHN92_NH and footprint area. Reproduce with export_footprints.py; no massing rebuild needed.

