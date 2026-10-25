# Independent review — 2026-10-23

**PASS for the exported visual asset. No must-fix geometry findings.** This review does not validate a functioning duck mechanic, collision, animation transitions or gameplay installation.

## Evidence

- Independently parsed the serialized `out/PROP_DuckBarrier_barrier.obj`: exactly 824 triangles against the 5,000 budget; finite positions, UVs and normals; complete positive in-range v/vt/vn indices; triangle-only faces; nonzero triangle areas; unit normals within 0.01 squared-length tolerance; UVs within [0,1].
- Actual engine-coordinate bounds are X [-1.20,1.20], Y [0,1.695], Z [-0.37,0.37] metres. Bottom contact is Y=0, horizontal origin is centred, full width is 2.40 m and depth 0.74 m. This fits the specified 2.50 m lane and <=2.45 m asset-width contract.
- Independently tested every exported triangle's bounds against the central X (-0.95,0.95) opening below Y=1.43: no intrusion. Source crossbar spans Y=1.43–1.68 with two supported uprights, sockets, braces and weighted bases. Base and socket construction in `build.py` reaches the ground through the bases; the offset bases preserve the opening.
- Opened the actual `previews/engine_sheet.png` (one image). All three engine views show a readable overhead construction obstacle, visible support hardware, grounded weighted bases, and red/white diagonal warning stripes on both faces. This fits the design spec's high obstacle category (duck or switch), as a visual asset.
- Independently opened the output PNG: RGB 512 × 512, opaque when converted to RGBA (alpha extrema 255/255). Manifest resolves one OBJ and one atlas with zero pivot and explicitly declares `gameplay_collider: false`.
- Reviewed original scripted provenance in `BRIEF.md`, `build.py` and `REPORT.md`: generic construction prop, no adopted mesh or photographic texture. Editable source and reproducible generator are present. The generated supports visibly connect; no unsupported floating assembly was observed.

## Actual rider comparison

Read both actual rider endpoint OBJs and their zero-pivot manifests, rather than accepting supplied height claims. Entire exported rider geometry reaches Y=1.674661 m riding and Y=1.316786 m ducking, including hair. The 1.43 m underside therefore leaves **0.113214 m full-mesh duck clearance**, with **0.244661 m riding height overlap**. Rider X extents are ±0.316098 m riding and ±0.335005 m ducking, comfortably inside the ±0.95 m central opening at the shared centred placement. The barrier remains suitable with these more conservative measurements. This establishes static endpoint geometry clearance only; no moving traversal or collider behavior is established.

## Could-fix

`BRIEF.md`, `REPORT.md` and `verify.py` use 1.65619 / 1.29515 m as rider heights, but the rider report identifies these as crown metrics excluding the hairstyle. Qualify those as crown-only measurements or use full exported-mesh maxima above when describing physical clearance. The smaller actual clearance still passes, so this is a documentation/verification precision issue, not an asset blocker.

Only this review file was written. No asset source edits, installation, commits, downloads or gameplay changes were performed.
