Approved and installed2026-10-23 after user desktop-preview approval; runtime files verified against docs/art/essential-install-plan.json.

# City car candidate report

Status: exported review candidate; not installed or user-approved.

Source: Innerscene original unbranded five-door hatchback, CC0 1.0 on publisher page. Download SHA256 107410e01453abbce452fabbe6d51436fb98a0920672643a893263a8861873d7. Full evidence hashes and URLs: provenance.json. No independent authoring-process verification beyond publisher page and glTF metadata. Existing source/reference inputs remain unchanged.

Final actual exported triangles: **17,686** (body 14,344; front left 836; front right 835; rear left 836; rear right 835). Original 130,902 triangles / 314 mesh objects. 86.49% reduction. Target 12,000 exceeded to preserve visible silhouette; hard 18,000 passes with 314 triangles spare. One 2048x2048 RGB opaque atlas; five OBJ files plus manifest. All source material nodes replaced by procedural constant colors before baking; no photo pixels or source bitmap textures.

Assembled actual export dimensions: length 4.259023 m, mirror width 2.116730 m, height 1.485697 m. Within 2.5 m lane including mirrors. Body origin is common ground center (source longitudinal asymmetry retained). Hood/headlamps at source -X prove front; mapping (x,y,z)->(y,-x,z) gives Blender +Y / engine -Z forward. Wheel X axles: +/-0.775 m; front Y 1.2321 m, rear Y -1.3505 m; Z 0.31205 m. Wheels have axle-centered local coordinates, +/-0.31205 m vertical extent, exact assembled minimum Z=0. Local rotation axis Blender X / engine X. Export correction removes 0.002858 m inherited wheel-node height offset; deterministic normalize_export.py is called by build.py and preserves atlas/UVs.

Hidden interior, brakes, screws/lugs, tread blocks and tiny optical fittings removed. Source body, roof, glazing, seams, mirrors, lamps, handles and five-spoke rims retained with family-specific reduction. Tyres reconstructed with smooth six-ring 40-sector source-matching profiles, independently of source rim simplification. Full source-to-result per-object log: reduction-log.json. Editable procedural-material source: editable.blend. Build/pre-bake numeric output: pre-bake-check.json. Single 8-thread 32-sample bake/export log: bake.log. The recorded shell invocation returned1; the retained log ends with successful exports and Blender quit, with no captured Python traceback. The native Blender process code was not independently preserved, so the cause of the shell status is unresolved. This is not evidence that nonzero Blender exits are normal. Artifact validation and engine loading subsequently returned0; those prove the delivered files, not the earlier process status.

Independent actual-export checks: python RunnerGame/Art/assets/city_car/verify.py PASSES. Five resolved manifest files, actual triangles <=18k, finite coordinates/UVs/normals, unit normals, every face triangular with nonzero area and valid indices, UVs in [0,1], four grounded wheels and centered axle extents, 2048 RGB image. Exact output hashes in export-check.json. Independent visual review is recorded separately in REVIEW.md by reviewer.

Preview paths:
- previews/reduced-workbench.png: initial reduced shape inspection before sole bake.
- previews/engine_0.png, engine_90.png, engine_180.png: final existing asset-viewer front/rear/side views (viewer yaw convention).
- previews/engine_game.png: existing viewer default game camera at common origin crops large car at close range.
- previews/context_game.png: same game camera, candidate translated six metres ahead using previews/game-context-parts.json; no geometry duplication or runtime changes.

Limits: moderate faceting remains in glass and dense body transitions; opaque glass intentionally hides interior. No exact real-car replica claim. Wheels are baked rigid pieces suitable for axle rotation, no steering rig. No gameplay/shared tool/Engine changes; no runtime installation or commit.
