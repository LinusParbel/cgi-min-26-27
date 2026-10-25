Approved and installed2026-10-23; source/runtime SHA256 verified via docs/art/street-props-install-plan.json.

# Street tree candidate

Original seeded generic deciduous tree, no external assets or species replica claim. Editable source/baked blends, spec/build/provenance and atlas/OBJ in out. No installation or shared-library edits.

Final actual export: 11,516 triangles, including 8,000 leaf triangles from 2,000 explicit two-sided diamonds and 3,516 wood triangles. Source bounds 3.5x3.5x6.5m, trunk-ground pivot zero, leaf underside 2.568m. Leaves authored .20x.125m (random scale .8-1.2), revised from .15x.08 after parent review. No leaf bevels, alpha cards or giant crown blobs. Atlas 1024 opaque; subdued varied greens.

verify.py exits0 checking actual exported triangles, finite positions/UV/normals, unit normals aligned to winding, nonzero area, bounds, centred trunk ground contacts, 4,000 opposed geometric leaf triangle pairs, opaque atlas and varied pixels. --negative-fixture strips reverse faces in memory and exits1 at the exact opposed-face assertion (0 versus 4,000). Neither test modifies source/export.

Pre-bake evaluated checks: 11,516 triangles, zero modifiers, 2,000 opposed quad pairs. Determinism: final no-bake geometry run and correction-bake fresh rebuild independently emitted geometry SHA256 bc1beba17f490089973bc5b3c2df870c203e398f8f6dd0761b094a4bc6d8f0ef with identical bounds/counts; fixed local random seed 230326. out/export_checks.json records final OBJ hash.

Three cheap Workbench checks total. First completed bake exposed a real exporter failure: smart-project edit conversion discarded reverse quads sharing vertex IDs, leaving 7,516 actual triangles / zero reverse pairs despite source checks passing. Parent explicitly authorized one correction bake: distinct backside vertex IDs survive UV conversion/export; leaves enlarged in same batch. Two total completed atlas bake sessions, 8 CPU threads / 32 samples each; no additional bake. Initial wrapper exit1 despite Blender quit (native stderr warning); correction captured BLENDER_NATIVE_EXIT=0 and wrapper exit0. Final verify exit0; expected negative fixture exit1; EssentialScene exit0, 11,516 triangles. CPU released.

Final standalone actual engine view previews/engine.png uses explicit camera/target and complete framing. Green porous crown with visible branches; intentionally low-poly angular bark and flat opaque leaves. Combined pavement/game-distance review belongs to parent. Candidate only, no gameplay or installation.
