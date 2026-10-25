Approved and installed2026-10-23 after user desktop-preview approval; runtime files verified against docs/art/essential-install-plan.json.

# Facade kit final build report

Candidate assets only; not installed into runtime. Original generic Hannover-inspired architecture, no building-specific replication, branding, photo pixels or external textures. Editable source: `shopfront_kit.blend`; reproducible construction: `build.py` + `spec.json`; independent validation: `verify.py`.

## Contract and final results

Three separately reusable modules: `shop_ground`, `sandstone_upper`, `brick_upper`. Each bottom-centre origin(0,0,0), source Blender Z up/front-Y; exported OBJ Y up/-Z forward. Each exact envelope is x[-3,3], y[-.4,.4], z[0,3.2] metres, verified within1e-6m. All projections fit inside advertised6x.8x3.2m footprint. Main wall front-.22m; glass front-.06m, recessed .16m. Cornice/awning projection .18m maximum; awning deliberately shallow for fixed footprint. Finished opaque backs and sides, no transparency or interior dependence.

Final actual OBJ checks PASS:588triangles each,1764combined versus6000budget;2048x2048 shared opaque atlas; manifest paths resolve, zero pivots; finite coordinates and unit normals; valid UV/index ranges; all faces triangular/nondegenerate. Independent triangle clipping proves no positive-area overlap of exterior triangles on either x+/-3 side plane. Pre-bake checks additionally prove closed constituent solids, recessed glass, opaque nontransmitting source materials, and front/back/both-side face normals. Geometry uses overlapping closed solids internally; no whole-mesh welded-manifold claim.

Source scene is saved before baking. Bake isolates modules at x0/8/16m, exports relative to layout offsets, then sets deliverable pivots tozero. Preview stack alone translates upper floors by3.2/6.4m; no duplicated stacked geometry in individual exports.

## Commands and results

Repo-root PowerShell, final corrected bake/export (exit0):

```
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --threads 8 --factory-startup --python-exit-code 1 --python RunnerGame/Art/assets/shopfront_kit/build.py -- --export
python RunnerGame/Art/assets/shopfront_kit/verify.py
python RunnerGame/Art/assets/shopfront_kit/preview_manifests.py
```

Bake2048 at32samples,8threads. Shared helper performs diffuse andAO passes. Logs: `out/build_final.log`; numerical results: `out/geometry_checks.json`, `out/export_checks.json`. Final bake/export completed2026-10-22 approximately23:27Europe/Berlin; CPU release reported immediately to parent.

Canonical engine previews, all exit0 (executable `tools/asset-viewer/bin/Debug/net10.0/AssetViewer.exe`):

```
AssetViewer.exe RunnerGame/Art/assets/shopfront_kit/out/preview_stack.json RunnerGame/Art/assets/shopfront_kit/previews/stack 0,30,90,160
AssetViewer.exe RunnerGame/Art/assets/shopfront_kit/out/preview_shop_ground.json RunnerGame/Art/assets/shopfront_kit/previews/shop_ground 0,30
AssetViewer.exe RunnerGame/Art/assets/shopfront_kit/out/preview_sandstone_upper.json RunnerGame/Art/assets/shopfront_kit/previews/sandstone_upper 0,30
AssetViewer.exe RunnerGame/Art/assets/shopfront_kit/out/preview_brick_upper.json RunnerGame/Art/assets/shopfront_kit/previews/brick_upper 0,30
```

Current final paths: `previews/stack_{0,30,90,160}.png`, `previews/{shop_ground,sandstone_upper,brick_upper}_{0,30}.png`. Builder inspected final stack30 and exact-side90: obsolete dark side bands and hatching are gone; readable recessed glazing, restrained warm masonry, discreet awning and finished sides. Thin masonry construction seam remains visible at exact side elevation; no overlapping exterior faces.

## Review correction and limitations

Initial overlapping-variant bake was stopped before completion. First completed isolated bake exposed coplanar quoin/wall/trim sides. Correction shortened quoins to facade plane, inset trim ends5mm and shortened trim backs to+.23m. Geometry-only export proved overlap removed but obsoleteAO remained; the final corrected-source bake above replaced that atlas. Two completed bake invocations total; final asset derives entirely from corrected-source bake. Legacy `fix_quoin_depth.py` records intermediate UV-preserving investigation and is unnecessary for final reproduction.

No additional cosmetic changes after review. Original authored proportions, plain back elevation, shallow awning, opaque glazing and retained internal faces are intentional limitations. Independent reviewer/parent acceptance of final corrected previews remains separate from builder verification. No shared tools,Engine,gameplay or runtime folders changed; no install or commit.
