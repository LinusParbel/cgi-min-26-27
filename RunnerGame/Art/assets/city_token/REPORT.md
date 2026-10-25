Approved and installed2026-10-23 after user desktop-preview approval; runtime files verified against docs/art/essential-install-plan.json.

# City token verification

Original scripted geometry and procedural colours; no downloaded model, bitmap artwork, brand or photo pixels. Candidate only, not installed. Editable source: city_token.blend; reproducible build.py/spec.json.

Actual export independently checked by parent and reviewer:868triangles,448vertices,792UVcoordinates; engine dimensions0.32x0.32x0.035m, bounds centred atzero; one part, zero pivot; opaqueRGB512atlas. All indexed triangles finite/nondegenerate with valid UVs and unit/outward normals. Both faces have raised outward H geometry, readable in engine token_35/token_180 previews.

The builder reported one512atlas/32sample bake at8threads. Its final prose report was not delivered before the user interruption; this record is reconstructed from the retained source, exported geometry_checks/export_checks, independent reviewer and fresh parent verification. It does not invent a captured bake-process exit code.

Rebuild source geometry: headless Blender5.2 --python build.py; append -- --export to bake/export using the existing photo_lib helper. Validate actual export: `python RunnerGame/Art/assets/city_token/verify.py` (fresh parent execution exit0). Source spinZ maps to engineY; source face normals+/-Y map to engine-/+Z. Origin is intentionally at coin centre, so a grounded placement needs0.16m lift; scene pickups are lifted0.9m.

The full scene `docs/art/previews/essential-batch-engine.png` renders three candidates at pickup distance. Parent inspected gold-token visibility in the lane; standalone review establishes H detail, while the scene establishes silhouette/colour readability. This is a static art scene, not implemented pickup logic. Source/review outputs retain exact numeric evidence. No runtime installation or commit.

Fresh parent source-only headless rebuild completed with native exit0 (TOKEN_NATIVE_EXIT=0);868tri and the same centred bounds/motif geometry passed before saving editable source. Blender emitted the existing use_nodes deprecation warning. No extra texture bake performed.
