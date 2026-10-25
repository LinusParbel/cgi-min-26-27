Approved and installed2026-10-23 after user desktop-preview approval; runtime files verified against docs/art/essential-install-plan.json.

# Civilian scooter rider — 2026-10-22

Reviewable Art candidate; not installed or committed. Only this asset folder was edited. Existing reference photographs, titles and refs.json are preserved. Fresh MPFB body, not a derivative of the officer scene.

## Deliverables

`out/CHR_ScooterRider_ride.obj`, `out/CHR_ScooterRider_duck.obj`, shared opaque `out/CHR_ScooterRider.png`, per-pose `_ride_parts.json` / `_duck_parts.json`, and `out/CHR_ScooterRider_poses.json`. Display exactly one endpoint at a time. Both manifests have the same zero pivot and common scooter ground/axle origin, Blender +Y forward (engine -Z).

Editable `rider_rig.blend`: native MPFB -Y skeleton, frame1 ride / frame2 duck. Export applies a pi rotation to captured coordinates, preserving the rig for editing. `rider_export.blend` preserves the baked template; `final_assembly.blend` assembles actual exported endpoints and the unchanged approved scooter. Final review image: `previews/final_export_board.png`. The older `fit_board.png` is a diagnostic with rejected collar/dashboard issues and MUST NOT be used as the final review.

## Results and checks

- 26,706 triangles and 14,727 vertices per pose. Both resident endpoints: 53,412 triangles. Body15,816; top+jeans4,120; adapted shoes3,104; opaque hair3,450; eyes172; brows44. No body/finger decimation.
- Single 2048×2048 opaque PNG, exactly one completed bake from ride only (16 samples, AO strength .12). Duck reuses the same atlas and UV coordinates with vertex-coordinate updates only. No overlapping two-pose bake.
- `python verify.py` PASS: independently parsed endpoint OBJ indices, finite positions/normals/UVs, nondegenerate triangles, index range, usable UV range, exactly matching face vertex/UV indices and UV values, resolvable one-part manifests and common origin, opaque atlas, budgets and distinct poses. Exact output SHA256 values are in `out/validation.json`.
- `python test_verify.py`: 5 tests PASS, including intentional invalid indices, degenerate triangles, NaN coordinates and out-of-range UV values. The validator rejects all four corruptions.
- Strict analytic two-bone solves assert reachable anatomy rather than silently clamping targets. Source skin and individually rigged fingers retained. Hands remain fixed on actual scooter grips in both endpoints; wrists are offset from the grip axis by anatomical palm length/roll.
- Actual grip-surface proximity, not wrist-only contact: three cross-sections ×24 samples around each .018m cylinder. Each hand in each pose has 65/72 sampled cylinder points within8mm of evaluated skin; minimum surface distance ≈0.035mm. `previews/{ride,duck}_grip_surfaces.json`; wrapping fingers/palms visible in final exported hand view.
- All sampled original low-sole vertices lie within deck x±.09,y[-.291,.214] in both poses (100% support). Lowestsole z=.184 within5e-8m. Authored source sole curvature spans7.92mm. Shoes retain original length/width; bound rigidly to foot bones to avoid calf-weight sole deformation. Whole shoe geometries have an8.65mm fore/aft gap; they do not intersect. `previews/contact_measurements.json`.
- Dashboard actual exported bounds x±.045,y[.134006,.330047],z[1.082745,1.179856]. Evaluated skin and clothing have ZERO intersecting triangle pairs with dashboard in both poses. Nearest dashboard-vertex-to-surface distance4.65mm ride /60.67mm duck. `previews/{ride,duck}_clearance.json`. Duck hips are deliberately behind the display (source y≈-.40) with hands and feet unchanged.
- Body crown drops from1.656190m to1.295149m: **36.104cm**. Crown metric excludes the short hairstyle; the same hairstyle follows the head in both poses.

## Sources and licence

Verified local primary MPFB licence sections C/D classify base mesh, targets, textures, clothes, rigs and expressions as CC0, separately from the GPL addon code. Copied evidence: `source/LICENSE.md`, `source/LICENSE.ASSETS.md`. The adopted MHCLO/material headers explicitly record their September2020 CC0 release. `provenance.json` includes35 exact local source-file paths and SHA256 values: official base OBJ, game_engine rig/weights, casualsuit02, shoes01, low-poly eyes, short01 hair, eyebrow001 and middleage_caucasian_male skin. MakeHuman Community; Data Collection AB; Joel Palmius; Jonas Hauquier. Existing official sources were reused, with no install or re-download.

Original source shirt texture/logo is not used: all shirt/sleeve islands receive plain teal material, trouser islands denim. No uniform patches, badges, radio, pouches, vest, officer targets or source officer meshes are present. Hair/brow alpha was trimmed geometrically once, then made opaque. No photographic reference pixels enter the atlas. Photo1 (Ilkka Jukarainen, Commons, CC BY-SA2.0) is riding category/pose reference; photo2 (Roger Cornfoot, Commons, CC BY-SA2.0) is distant context only; exact source metadata remains in refs.json.

## Bounded fitting work and remaining limitations

Three meaningful fitting rounds, plus the final observed must-fix batch before the single bake: original height-based shirt recolor replaced by connected-island assignment, supported tandem stance solved, palm roll/height corrected, high source shoe collars trimmed with hidden termination under trousers, calf sole deformation removed, crouch moved decisively behind dashboard. No subsequent cosmetic refinement or rebake.

Two discrete endpoint poses; no interpolated transition is delivered. Atlas AO is baked from ride and reused in duck as required. Clothing has normal close-fitting hem/ankle overlap; shoe upper termination is hidden under trousers. Hair uses trimmed opaque source geometry instead of engine transparency. Independent reviewer and user gate remain with parent; no runtime installation was performed.
