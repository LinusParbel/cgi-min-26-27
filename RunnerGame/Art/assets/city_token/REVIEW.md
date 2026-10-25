# Independent city token review

**PASS — exported asset and two standalone engine views.**

Reviewed Task 6 of `docs/superpowers/plans/2026-10-22-essential-assets.md`, `spec.json`, `build.py`, the actual OBJ/manifest/PNG, and engine images `token_35.png` and `token_180.png`. `REPORT.md` was not present at review time; orientation was checked directly against the build/export contract.

- Actual export: 868 triangulated faces, valid positive position/UV/normal indices, finite coordinates, no zero-area triangles. Minimum triangle area 0.000037739241 m². Unit normals agree with winding (minimum dot 0.996908).
- UVs lie in [0,1], with no zero-area UV triangles. Atlas is opaque RGB, 512 × 512. Manifest references resolve.
- Engine bounds: (-0.16,-0.16,-0.0175) to (0.16,0.16,0.0175) m. Diameter 0.32 m, thickness 0.035 m, exact bounds center (0,0,0); manifest pivot is the center, not the bottom. A grounded placement would need +0.16 m engine Y.
- Both faces have outward-facing raised H geometry, matching upright bars and crossbar; the symmetric H remains correctly readable from either side. Bronze/gold face, raised rim and H read clearly in both inspected engine views.
- Source front is Blender -Y. Source vertical spin axis Z maps to engine Y; spin is a yaw around the centered vertical diameter. The face normal maps to engine ±Z and is not the requested vertical spin axis.

**Must fix:** none for this asset scope.

**Could fix:** none required; no cosmetic expansion recommended.

Pickup-distance readability in the coherent street scene remains the parent batch check; these two close views do not establish it. This review does not grant runtime installation approval.
