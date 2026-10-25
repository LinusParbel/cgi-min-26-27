# Delivery van candidate ready

Generic unbranded high-roof cargo van, adopted from Innerscene's explicit CC0 source. This is not a measured Mercedes-Benz replica. Source reference photos by EurovisionNim and exact source/licence hashes are retained under the asset's refs/provenance records.

Actual output:15532triangles (body12412, four780wheel parts), one opaque2048RGBatlas, dimensions5.704837m long /2.437192m wide including mirrors /2.505583m high. Body preserved at source scale; mirror projection shortened to fit the2.5m lane. Wheels have local axle origins and exact ground contact; front source+Y/engine-Z. Nominal12ktarget was exceeded to preserve visible contour, below approved18khard cap.

Source/build/editable blend, export/negative checks and independent PASS review: `RunnerGame/Art/assets/delivery_van/`. Final engine angle sheet: `previews/engine-sheet.jpg`. Full street context: `docs/art/previews/delivery-van-street.png`. Candidate is placed in the left lane atx-2.5,z-16, clear of prior obstacles; centre lane remains open.

Live review uses `tools/essential-scene` with `docs/art/delivery-van-inspection-scene.json --show`, starting closer to the van. WASD moves camera, rightmouse/arrows looks, Q/E down/up, Shift faster, R resets, Esc closes. This is an art viewer, not gameplay. Candidate remains in Art/out pending visual approval. `docs/art/delivery-van-install-plan.json` enumerates seven proposed runtime files with SHA256; no installation yet.

All actual-export and four negative-fixture checks pass. Single8thread/32samplebake native exit0; no correction bake. Close headlamp/door seam irregularities remain; static images cannot establish absence of temporal seam flashing. Independent review found no blocking geometry/export issue. Street-scene rendering succeeds with59instances/31meshes/13textures; performance not benchmarked. No shared helpers/Engine/gameplay changes or commits.


Approved and installed 2026-10-23: user approved the live delivery van. All seven runtime files copied and SHA256 verified; gameplay integration remains pending.
