# Ordnungsamt character preview

User authorised the first neutral-pose preview on 2026-10-18. This is a visual prototype, not an installed game asset.

- Build an original, cap-free stocky adult with a moustache, short hair and determined brows.
- Use navy service jacket/trousers, light blue shirt, black footwear, shoulder radio and original ORDNUNGSAMT labels. Garment cut is an artistic approximation, not a verified Hannover uniform replica.
- Keep body surfaces continuous within each garment/limb; use shaped cross sections rather than stacks of spheres.
- Save an editable Blender scene and render front, side, rear and face views.
- Check mesh bounds, evaluated triangles, finite vertices and readable lettering, then inspect the actual image.
- Show the preview for character feedback before producing running poses or installing exports.

Implementation stays in this asset directory. Shared libraries and engine code remain untouched. No commit requested.

## Running-pose revision

The first three poses were rejected as unrealistic. Fixed-height cuts through sparse meshes pinched knees and elbows, rotated boots with shins, and produced a symmetric middle pose. Rebuilt limbs as dense ring surfaces along explicit two-bone chains (thigh 0.395 m, shin 0.385 m), with ankle pitch independent of the shin and eight distinct cycle phases. Joint length and finite-coordinate assertions run during each build. Two phases have a small flight clearance. Artistic gait approximation; not motion capture. Review the animated loop before engine export.

Technique reference: https://www.nsca.com/education/articles/kinetic-select/movement-analysis-and-biomechanics-for-endurance-sports/ (support placement); https://dxpprod.nsca.com/education/articles/kinetic-select/factors-determining-agility-speed/ (shoulder-led arm swing).
