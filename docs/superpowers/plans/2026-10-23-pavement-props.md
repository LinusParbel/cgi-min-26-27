# Pavement props

Continue the approved modelling backlog with an original bicycle stand, café table and chair. Use the established generic scripted Blender workflow. These are authored generic designs, not replicas or external model adaptations.

- Builder owns `RunnerGame/Art/assets/pavement_props/`; no shared engine/library changes or commits.
- One inverted-U steel stand, roughly 0.8 m long/high with mounting plates; under 3,000 triangles.
- One round 0.7 m café table at 0.74 m and one chair with 0.45 m seat and roughly 0.82 m back. A table plus two chair instances stays below 6,000 triangles.
- Independent bottom-centred origins, metres, opaque shared 1024 atlas, isolated bake layout, 8 threads and 32 samples. Preserve editable source and actual-export validation.
- Parent verifies exports; independent read-only reviewer inspects actual geometry and engine sheet. One correction batch if necessary.
- Place a café arrangement and repeated bicycle stands on clear pavement in a copy of the installed street scene. Avoid existing props, facades and road lanes. Check the existing bicycle dimensions before placing it beside a stand.
- Show the result in the actual interactive engine viewer before installation. Record source/export/review/install/gameplay states separately.

Van prerequisite completed: user approved the live view; seven runtime files copied with SHA256 checks, solution build clean, and installed street scene rendered successfully (59 instances, 31 meshes, 13 textures).

## Essential gap found by design audit

The agreed game spec requires a head-height duck obstacle. The installed low construction barrier reaches only 0.99 m and does not provide a duck opening. Add a separate original supported overhead barrier in `Art/assets/duck_barrier/`, reusing red/white construction styling. Proposed opening lower edge 1.43 m, crossbar top 1.68 m, interior width about 1.9 m and total feet width at most 2.45 m. Current mounted rider tops are 1.65619 m riding and 1.29515 m ducking. Verify actual exports against these values; collision implementation remains separate. Budget 5,000 triangles, opaque atlas up to 1024. Only bake after pavement props finish. Independent review and live presentation required.

After these assets, the audited first-slice model families are covered. Additional variants are conditional on visible repetition; tram, zones and decorative catalogues remain deferred. The rotating-cube game entry point still needs gameplay integration, which this modelling task does not implement.
