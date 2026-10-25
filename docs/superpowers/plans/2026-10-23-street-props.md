# Street props implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Fill the approved street slice with bench, planter, lamp, pothole and tree candidates.

**Architecture:** Original generic scripted props, not replicas of specific street furniture. Shared furniture atlas for bench/planter/lamp; independent pothole and opaque-leaf tree. Preserve existing game, approved models and shared libraries.

**Tech Stack:** Blender5.2 headless/Python, photo_lib helpers read-only, triangulatedOBJ+opaquePNG, existing engine review tools.

**Spec:** docs/art/2026-10-22-asset-backlog.md next batch; user approved the first batch and said "lets move on"2026-10-23.

## Global constraints and review focus

- Continue feature/photo-to-model without commits; preserve unrelated dirty work. One geometry/bake worker at a time,8threads,32samples, one completed bake unless a visible blocker justifies correction.
- Sourcefront-Y, Zup, metres; export-forward-Z/upY. Each independent prop bottom-centred zero pivot. Furniture separated for atlas baking then export positions normalised to independent local origins, not baked together at overlapping origins.
- Reproducible spec/build/editableblend, pre-bake actual geometry checks, independent exported bounds/budget/normals/UV/texture checks, engine sheet. No logos/photos/alpha/dependency on normalmaps.
- Review: support/ground contacts, physical seating shape, planter inner rim/soil, believable lamp proportions, leaf culling and canopy silhouette, pothole depth against opaque road, and isolated-atlas correctness.

### Task1: Street furniture kit

Create Art/assets/street_furniture/{BRIEF.md,spec.json,build.py,verify.py,REPORT.md,out,previews}.
- [ ] Build three independently placeable parts: bench1.8m long/~.6mdeep/~.85mhigh with seat at.45m, individual wooden seat/back slats, curved/angled metal supports and armrests; square planter~.9x.9x.8m with thick inset rim, visible soil and modest opaque shrub; slender streetlamp6mhigh with sturdy base, curved short arm and recognisable lamp head/lens (no emitted lighting claim).
- [ ] <=10000tri combined,1024sharedatlas, prefix PROP_StreetFurniture. Each part includes its complete physical prop, bottomorigin. Materials restrained wood/paintedmetal/concrete/soil/leaf; authored dimensions documented in spec.
- [ ] Build checks first, save source, separate bake layout sufficiently for6mlamp, bake once, normalize exported zero pivots. Validate actual exports and render per-prop3/4 engine views; kit overview optional.
- [ ] Independent review, one bounded correction batch if needed. No installation before presentation.

### Task2: Pothole

Create Art/assets/pothole/{BRIEF.md,spec.json,build.py,verify.py,REPORT.md,out,previews}.
- [ ] Original irregular asphalt patch~1.1x.8m, broken jagged lip, dark recessed centre and sparse aggregate, <=1500tri,512atlas, prefix PROP_Pothole.
- [ ] Current road is opaque solid atz0: negative hole geometry would be hidden. Provide a self-contained opaque surface overlay with dark bowl impression at z>=.002m; document it as visual damage patch rather than real road excavation. Origin groundzero; simple independent gameplay trigger is future work.
- [ ] Check silhouette, normals, non-coplanar layered surfaces, budget and engine placement on actual street road. Export/review, no installation yet.

### Task3: Opaque tree

Create Art/assets/street_tree/{BRIEF.md,spec.json,build.py,verify.py,REPORT.md,out,previews,provenance.json}.
- [ ] Generic authored deciduous street tree,~6.5mhigh/~3.5mcanopydiameter, branching taper trunk, open space below canopy~2.4m. Original deterministic procedural geometry; no claim of real tree/species replica.
- [ ] Avoid a few giant ellipsoids and alpha cards. Use many small opaque two-sided leaf polygons in natural branch clusters with varied restrained greens, sparse gaps and coherent crown silhouette. Trunk/branch geometry visible near base; <=12000tri,1024atlas, prefix ENV_StreetTree. Budget leaf faces including both windings.
- [ ] Verify ground/origin, real bounds/budget, front/back leaf visibility and deterministic output. One bake then engine review at pavement/game distances. No installation yet.

### Task4: Combined review

- [ ] Run all new actual-export checks, renderer/solution build and source records.
- [ ] Extend a copy of docs/art/essential-scene.json, placing furniture/tree on pavements without obstructing lanes and pothole visibly on asphalt. Render with actual engine, then open the PNG in desktop viewer (inline tool images were invisible to user).
- [ ] Record files/limits and show the complete next batch before installation. No extra-zone or gameplay implementation in this scope.
