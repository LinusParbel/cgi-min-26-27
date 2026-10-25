# Officer v2 — smoother run checkpoint

User reported unnatural hand/leg movement and asked for frame analysis followed by correction. Supersedes the 24-frame run preview.

- New GIF: `RunnerGame/Art/assets/ordnungsamt_pursuer_v2/previews/officer_v2_run_smooth.gif`, also copied to `officer_v2_run.gif`. 40 frames, uniform 20 ms/frame, total 800 ms, 960×640 synchronized three-quarter/side views, 8,666,109 bytes.
- Same editable animation source: `officer_v2_run_preview.blend`, frames 1–40 at 50 fps, duplicate endpoint keyed at 41. Neutral `officer_v2.blend` hash remains unchanged.
- Old GIF preserved at `previews/run/run_before_smoothing.gif`; old frame analysis at `motion_analysis_before.json`; all 24 old side frames contact sheet at `all_frames_before.jpg`; old generation script at `checkpoints/animate_run_before_smoothing.py`.

## Root causes and corrections

Analyzed every old frame plus saved-rig per-frame joint positions. The old per-frame boot-minimum correction moved the entire rig, causing roughly 5 cm torso position changes around frames 9–12 and 21–24. This jolted hands as well. Alternating 30/40 ms GIF durations added timing judder. Hip height and ankle paths were independently specified, then reconciled by whole-body snapping.

Now hip height is a continuous analytic cycle, root Z stays zero, and each ankle gets a small evaluated sole correction through a fresh leg IK solve. Planted ankle Y travels backward at constant velocity; the return path preserves tangent continuity. Feet run slightly closer under the hips. Elbows flex through the stride, wrists have a small lag, shoulders counterrotate against the pelvis, and fingers use a relaxed fist. Rendering uses 40 uniformly timed frames without changing cycle duration.

## Fresh evidence

- `analyze_run.py`: pelvis peak acceleration reduced from about 47.9 to 5.88 m/s²; wrists from about 53.9 to 20.08 m/s². Left/right wrist results symmetric. Planted ankle speed 2.1249987–2.1250010 m/s. Knee bend 14.3–132.5 degrees.
- `verify_run.py` exit 0: all 41 poses have sole contact/clearance within 1 mm, knee flex >12°, unchanged bone lengths, finite transforms, correct equipment parenting and loop endpoint matrix error exactly 0.
- `check_motion_smoothness.py` was observed failing on the original torso jolt, and passes on final data/GIF: peak torso <15 m/s², wrist <35 m/s², steady planted ankle and uniform GIF timing.
- `make_run_gif.py` exit 0: 40 frames, 800 ms, all durations 20 ms, neutral source SHA unchanged.
- Final multi-phase front/side contact sheet inspected: `previews/run_contact_sheet.jpg`.

Still a procedural in-place preview with a rigid chest carrier, not motion capture or installed gameplay animation. No runtime assets, neutral model, engine code, commits or pushes changed.
