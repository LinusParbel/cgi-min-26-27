# Duck barrier report

Completed original generic overhead construction barrier. Ready for independent review; no installation, engine changes or commits performed.

## Deliverables
- `build.py`: reproducible source, --export performs atlas bake; shared helpers imported read-only.
- `editable.blend`: separate named crossbar, stripes, supported uprights, sockets, weighted bases and bolts. Saved before export joins objects.
- `out/PROP_DuckBarrier_barrier.obj`, `PROP_DuckBarrier.png`, `PROP_DuckBarrier_parts.json`: one assembled independent prop, bottom-centred pivot, one opaque 512 atlas.
- `previews/engine_sheet.png`: actual course-engine views at 0, 30 and 160 degrees; visually reviewed. Clear warning bands both sides, supported upright silhouette and grounded bases read cleanly.

## Verified measurements
Actual serialized OBJ: 824 triangles, dimensions 2.400 x 0.740 x 1.695 m, centred X/Y and ground Z=0. Physical central opening 1.900 m wide, crossbar underside 1.430 m and upper edge 1.680 m. Actual triangle bounds reject any intrusion into central opening below 1.430 m, including low base intrusions. Weighted bases offset outward to preserve the opening, overall width within 2.5 m lane.

Independent reviewer complete rider OBJ bounds, including hair, ground-relative with scooter: riding 1.674661 m and duck 1.316786 m. Actual opening yields 0.113214 m duck clearance and 0.244661 m riding height overlap. No gameplay collider or live animation validation claimed.

Checks: finite serialized vertices/UVs/normals, valid complete positive OBJ v/vt/vn indices, triangles only, nonzero triangle area, normalized normals, UV range, opaque 512 atlas, <=5000-triangle budget, ground contact, centre and opening. Results in `out/export_checks.json`; Blender geometry checks and rejection of raised ground, blocked central opening, oversized base fixtures in `out/geometry_checks.json`. Geometry initially caught inward base intrusion and corrected before bake. Bake once, CPU <=8 threads, samples=32.

## Provenance
All geometry is original scripted work; procedural materials from existing local helper. No photos, third-party meshes, textures, trademarks or logos. This is a generic prop rather than an exact real-world replica.

Reproduce: Blender 5.2 background `--threads 8 --python-exit-code 1 --python build.py -- --export`, then standard Python `verify.py`; SpikeViewer with exported OBJ and PNG for engine sheets. Spec records design contract; generator uses same explicit constants. No shared helper edits.

Original parent-provided crown-only bounds (ride 1.65619 m, duck 1.29515 m) excluded hair and have been superseded by the complete-mesh measurements above. No geometry or bake change was needed.



Installation closeout 2026-10-23: user approved the live batch (good). All eight runtime files installed and SHA256 verified. Full runtime scene: docs/art/installed-street-scene.json. Gameplay integration remains pending.
