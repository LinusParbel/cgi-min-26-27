# Delivery van candidate

Built generic unbranded high-roof cargo van from verified CC0 Innerscene source; category reference photographs remain comparison-only. No logos, real registration marks or photographic pixels.

- Actual export: **15,532 triangles**, body12,412 + four780-triangle wheels; exceeds12k target by3,532, below18k hard cap. Contour, doors, hinges and bumper features retained.
- Bounds including mirrors: **2.437192m wide x5.704837m long x2.505583m high**, exact tyre ground z0. Body unscaled. Source actual mirror width2.624m exceeded advertised2.420m; only projection beyond0.96m attachment shortened by0.260/0.352.
- +Y Blender front (engine -Z) proved by negative-X source headlamp/hood versus positive-X rear doors. Axles x=+/-0.9072m, y=1.68/-1.72m,z0.3931m; independent rotating wheel meshes.
- Source135,896tri/344meshes. Family decisions in reduction-log.json; source mesh bounds/material inspection archived. Tyres rebuilt40segments, rims independently reduced, hidden cabin/brakes/tiny fittings removed.
- Workbench shape checked once; final engine0(rear),180(front),135(oblique) all completely framed. No correction bake. Front-panel/source door-line contour irregularities remain visible at close inspection; silhouette/category reads clearly.
- Single completed2048RGB opaque shared-atlas bake,8threads32samples. bake-native-exit.txt=0; Blender CPU released. Explicit native exit distinguishes harmless PowerShell stderr wrapping of Blender warnings.
- Independent evaluated pre-bake check passed (pre-bake-independent.json). Actual OBJ verifier passed: valid indices, finite coordinates, UV range, unit normals, nonzero triangle areas, ground/pivots/bounds, source hash, RGB2048atlas. No serialized zero-area faces needed removal; normal normalization preserves UVs. Actual export equals evaluated15,532tri.
- Negative fixtures correctly reject invalid indices, degenerate triangles, zero normals and a wheel floated50mm. Run python negative_fixtures.py; production files unchanged.

Deliverables: editable.blend, build.py, spec.json, BRIEF.md, provenance.json, refs.json, precheck.py, verify.py, normalize_export.py, logs/reports, out/VEH_DeliveryVan_parts.json + fiveOBJ + PNG, previews/engine-sheet.jpg and full-size engine images.

Candidate remains in Art/assets/delivery_van/out. No installed models, runtime, gameplay, shared helpers or viewer code edited; no commit. Parent handles street-scene context, independent visual review and interactive handoff. Any correction bake requires parent clearance.


Approved and installed 2026-10-23: user approved the live delivery van. All seven runtime files copied and SHA256 verified; gameplay integration remains pending.
