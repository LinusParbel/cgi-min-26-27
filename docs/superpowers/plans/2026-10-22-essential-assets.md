# Essential street assets implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Deliver the approved clock and reviewable rider, street, facade, car and token assets for Hannover Rush Hour.

**Architecture:** Keep each model's reproducible build, specification, verification and preview in its own Art asset folder. Export triangulated OBJ parts sharing an opaque PNG atlas. Reuse the existing photo_lib helpers without modifying shared tools or gameplay.

**Tech Stack:** Blender 5.2 headless/Python, existing C#/OpenTK asset viewer, OBJ/PNG.

**Spec:** docs/art/2026-10-22-asset-backlog.md, first batch approved by user on 2026-10-22 ("clock is find lets do the next essentials").

## Global Constraints

- No commits, paid services, AI 3D generators, logos or photo pixels in textures.
- Preserve pre-existing source edits. Continue on existing feature/photo-to-model branch because approved source assets and licensed local dependencies are uncommitted here.
- One model builder at a time; independent read-only review follows each candidate. Only one bake at a time.
- Shared tools/asset-spike/asset_lib.py, tools/asset-viewer and Engine remain unchanged.
- 1 unit = 1 metre; OBJ -Z forward/Y up; record source orientation and manifest pivots.
- Install approved clock now. New candidates stay in Art/out until shown to the user.

## Review Focus

- Repeated street endpoints: no cracks, doubled curb sections, UV discontinuity or unexpected lane obstruction.
- Rider contact: hands fit actual scooter grips and soles fit deck in both poses, without modifying approved scooter.
- Facade reuse: finished visible sides, correct ground elevation and no dependence on transparent windows.
- Vehicle readability: wheel-ground contact, believable silhouette and lane-compatible footprint.
- Shared exports: all faces valid, finite coordinates/normals, usable UVs, resolvable manifests and actual triangle budgets.

### Task 1: Install approved clock

Files: runtime Models/Wahrzeichen/KroepckeUhr, Art/ASSETS.md, clock FINAL_REVIEW.md.
- [ ] Copy the three verified output files to runtime; compare SHA256.
- [ ] Record explicit user approval and current export statistics without replacing unrelated register changes.

### Task 2: Street kit

Files: Art/assets/street_kit/{BRIEF.md,spec.json,build.py,verify.py,out/,previews/,REVIEW.md}.
Interface: build(spec) returns five named parts (road, pavement_left/right, curb_left/right); parts.json uses zero pivots and the common module origin. Length 20 m along Blender Y, endpoints +/-10 m; road x +/-3.75 m at z0; pavements extend 2 m outward, top z0.15. Curbs must be included within pavement width, not additional width. Budget <=3000 triangles, 2048 atlas. Original generic construction, not a specific photographed street.
- [ ] Write geometry checks before building: five parts, actual bounds, drivable width, pavement elevation, exact snap ends, budget.
- [ ] Build asphalt, paving pattern and curbstones with restrained procedural materials; all longitudinal patterns repeat at endpoints.
- [ ] Run checks, export once, validate exported geometry and render assembled engine views.
- [ ] Independent review; one fix batch if necessary.

### Task 3: Facade kit

Files: Art/assets/shopfront_kit/{BRIEF.md,spec.json,build.py,verify.py,out/,previews/,REVIEW.md}.
Interface: three independent reusable modules: shop ground floor, sandstone upper floor, brick upper floor. Width6m, depth0.8m, height3.2m, front Blender -Y, ground origin for each module. <=6000 triangles total, 2048 atlas. Original Hannover-inspired generic architecture; no brand signage. Build recessed opaque glazing, window frames, plinth, lintels/cornice and discreet shop awning. One assembled preview stacks ground+two upper storeys without baking duplicate stacked geometry into the individual exports.
- [ ] Check module bounds, fronts, no missing backs/sides and triangle/texture contract.
- [ ] Build, verify, export, engine preview and independent review.

### Task 4: City car

Files: Art/assets/city_car/{BRIEF.md,spec.json,build.py,verify.py,out/,previews/,REVIEW.md,provenance.json}.
Interface: generic compact five-door hatchback, not a branded replica, approx4.2x1.8x1.5m body (mirrors may reach2.16m); target12000 triangles, hard limit18000 within approved backlog range, 2048 atlas. Body and four wheels, meaningful axle pivots, Blender +Y forward. Keep rounded profiles, glasshouse, wheel wells, bumpers, lamps, seams, mirrors and door handles; no logos/plates identifying people. Selected licensed base: Innerscene CC0 original unbranded hatchback, verified source/provenance in city_car/candidates.json; publisher preview inspected. Drop hidden interior and simplify expensive wheel fittings; preserve body silhouette. Original lofted construction remains fallback if adaptation fails.
- [ ] Record dimensions as authored design choices; inspect photographic category references before geometry.
- [ ] Verify footprint/ground/wheel positions and pivots; build and export; independent engine-view review.

### Task 5: Rider

Files: Art/assets/scooter_rider/{BRIEF.md,spec.json,build.py,verify.py,out/,previews/,REVIEW.md,provenance.json}.
Interface: two baked poses (ride, duck), same topology/UV and one2048 atlas, <=35000 triangles per pose. Adopt the already available CC0 MPFB base and verified official wardrobe assets; civilian jacket/trousers/shoes, no uniform patches/equipment. Front +Y matches Voi. Contact targets come from actual scooter source/export rather than guessed world positions. Save editable rig and contact measurements. Same common origin in both exported poses; manifests must make mutually exclusive pose display clear.
- [ ] Verify base/wardrobe provenance and inspect local anatomical source.
- [ ] Measure scooter deck/grips; define rig contact targets; build two poses with plausible limb bends and grip wraps.
- [ ] Verify hand/sole contact, clearance, matching topology/UV, resident-pose cost, export and combined rider+scooter preview.
- [ ] Independent review and one correction batch.

### Task 6: City token and full batch check

Files: Art/assets/city_token/{BRIEF.md,spec.json,build.py,verify.py,out/,previews/,REVIEW.md}; docs/art/2026-10-22-essential-progress.md.
Interface: original double-sided bronze/gold token, diameter0.32m/thickness0.035m, centre pivot, <=1000tris,512 atlas. Raised original H motif/rim, no city seal. Spin axis recorded.
- [ ] Build/check/export token and independent review at pickup distance.
- [ ] Render coherent street-slice preview using new candidates and existing scooter/bin/barrier/clock, without editing gameplay or shared viewer.
- [ ] Run relevant asset checks and solution build; record new warnings separately from existing CS0649.
- [ ] Present candidates, exact files and remaining limitations; update backlog statuses truthfully.
