# Kröpcke Uhr candidate verification — 2026-10-22

The existing build.py/spec.json were preserved. The previous OBJ had 23,942 triangles; a fresh export of the current source has 23,410, so the stale export was replaced.

- Headless Blender 5.2.2: `--python RunnerGame/Art/tests/blender_test_kroepcke.py`: **26 tests passed**. Includes surface profiles, open pedestal gaps, hood depth and export checks.
- `compare.py -- <asset> ref/01.jpg --errors`: RMS **25.4 px / 2.14% of photo width**; largest errors: side dial (+40.5,-19.6), back crown (-31.2,+18.1), front dial (-28.4,-21.1). Signed errors are model minus photo.
- `compare.py -- <asset> ref/04.jpg --errors`: RMS **10.4 px / 0.97%**; largest dial error (-17.4,+10.5). A fitting NumPy empty-slice warning was emitted; command completed successfully.
- `build.py -- --export`: three runtime outputs in `out/`: `PRP_KroepckeUhr_body.obj`, `PRP_KroepckeUhr.png`, `PRP_KroepckeUhr_parts.json`.
- OBJ and engine independently report **23,410 triangles**, below the 25,000 budget. Atlas **2048×2048**. Dimensions **2.47×2.47×6.11 m**, ground at zero; one body part, zero pivot.
- Existing AssetViewer rendered five views `previews/final_engine_{game,0,35,90,180}.png`. The game camera is a close detail view and crops the tall object; the 17-degree view also clips the rod. These are not complete silhouette approval views.
- Complete object with margin: **`previews/final_review_full.png`**, rendered by the existing viewer at yaw 35, `--pitch 50`. No viewer changes. `final_engine_sheet.jpg` retains the five initial views for comparison.

Independent read-only review found no geometry/export blockers. Remaining could-fix items: simplified relief figures, dome ribs, hood/profile and pedestal moldings; opaque stylized reflections. The second key photo remains above the 1.5% RMS target and uses a 200 mm camera fit; a low RMS on the other photo does not establish a perfect replica. Legs round-two sheet was inspected: broad widths/openings match, fine moldings are approximate.

Approved by the user on 2026-10-22 ("clock is find lets do the next essentials"). Installed under `RunnerGame/Assets/Models/Wahrzeichen/KroepckeUhr/`; SHA256 of all three runtime files matches the verified source export. Register updated without replacing prior entries. No source edits or commit. Existing clock photo credits retained.
