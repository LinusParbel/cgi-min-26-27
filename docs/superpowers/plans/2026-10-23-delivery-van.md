# Delivery van implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Deliver a reviewed generic cargo-van candidate and show it in the interactive street viewer.

**Architecture:** Adopt the verified CC0 Innerscene high-roof cargo panel van, normalize and selectively reduce its visible geometry, export body and four axle-pivoted wheels sharing one opaque atlas. Preserve installed assets and gameplay.

**Tech Stack:** Blender5.2 headless, photo_lib read-only helpers, OBJ/PNG, existing interactive EssentialScene viewer.

**Spec:** docs/art/2026-10-22-asset-backlog.md van entry; user "lets continze" after prior viewer acceptance. Vehicle sourcing choices are agent recommendations within delegated backlog scope.

## Constraints / review focus

- Source/primary licence evidence and category reference photos prepared before build under .model-research/delivery-van and Art/assets/delivery_van. RouteB, generic unbranded category interpretation, not an exact Sprinter replica. No AI3Dservice, logo, real registration or source photograph pixels.
- Target12k, hard18000tri total,2048sharedopaqueatlas. Preserve silhouette, doors, bumpers, lamps and mirrors; drop hidden interior/tiny hardware and reduce wheels separately.
- Source dimensions advertised roughly5.675x2.420x2.480m; actual exported width including mirrors must fit2.5m lane. Aim<=2.45m; if source exceeds it, adjust only mirror projection with documented authored choice instead of squashing the body.
- Metres, groundedcommonbodyorigin, Blender+Yfront/engine-Zfront. Four independent wheel meshes with axle pivots and exact ground contact, sourceXrotation axis. All actual exports valid indices/UVs/unit normals/nonzero triangles.
- One geometry/bake worker,8threads32samples, one completed bake then at most one visible-blocker fix batch. Wait for review before any correction bake. Evaluate modifiers when counting geometry; record native exit explicitly.
- Do not edit shared asset libraries, asset-viewer, Engine, gameplay, installed models or live viewer code. Continue featurebranch, no commits. New candidate remains in Art/out until visual approval.

### Task1: Adapt van

Own Art/assets/delivery_van only. Read provenance/refs and existing city_car build as pattern, not as a blindly copied geometry script. Save spec/BRIEF/build/verify/provenance/reduction log/editableblend and REPORT.
- [ ] Inspect source actual axes, bounds, parts, triangle costs; photograph/reference sheet already inspected by parent.
- [ ] Define independent meaningful footprint/wheel/budget/export checks before final bake. Detect degenerate triangles introduced by serialization and preserve reproducible source/export parity.
- [ ] Normalize and selectively reduce. Replace source material nodes with restrained opaque white/grey/black paint/plastic/glazing and lamp colours. Avoid coplanar decorative panels or tiny live seam strips that cause flashing.
- [ ] Inspect one Workbench shape, bake/export prefixVEH_DeliveryVan, body+4wheel parts manifest. Verify actual files and source hashes. Report any target/budget tradeoff honestly.
- [ ] Render final engine front/rear/oblique views and one street-camera context; do not use a clipped default large-vehicle camera as full-model evidence.

### Task2: Review and show

- [ ] Independent reviewer against two category photos, actual export, manifest, primary CC0 evidence and engine images; one bounded correction batch if necessary.
- [ ] Parent runs actual-export verifier and relevant build. Add van to a copy of installed street scene, keeping at least the centre lane clear and avoiding existing obstacles.
- [ ] Open candidate in the existing persistent interactive viewer with visible/focused window. Record delivery hashes and pending installation accurately. No screenshot-only handoff.
