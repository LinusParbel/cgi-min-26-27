# Officer v2 run GIF checkpoint

User requested an animation GIF showing walking or running. Created a running preview appropriate to the pursuer; no further appearance changes or runtime installation.

- GIF: `RunnerGame/Art/assets/ordnungsamt_pursuer_v2/previews/officer_v2_run.gif` — 960×640, 24 synchronized two-view frames, 800 ms seamless cycle, 5,188,058 bytes. Three-quarter and side views.
- Editable source: `officer_v2_run_preview.blend`, separate from the unchanged neutral `officer_v2.blend` (source hash recorded and verified).
- `animate_run.py`: loads neutral source; attaches currently rigid accessories to corresponding bones preserving rest transforms; solves two-bone leg IK on continuous ankle paths; opposite arm swing, relaxed fist curl, modest torso lean/hip rotation, actual evaluated boot-sole contact and flight clearance. Keys frames 1–25, with frame 25 matching frame 1; playback range 1–24 at 30 fps. Saves before rendering. `-- --check` renders four main phases; default renders 24 frames from each camera.
- `verify_run.py`: independently opens saved animation; all 25 poses pass actual sole-ground/clearance check (1 mm tolerance), bone lengths preserved, finite matrices, representative rigid equipment stays fixed relative to its assigned bones, loop endpoint matrix error exactly 0. Reports: `previews/run/rig_validation.json`.
- `make_run_gif.py`: common palette, durations [30,30,40] ms ×8, 24 frames, 800 ms. Verifies neutral source hash unchanged; writes `gif_validation.json`. Contact sheet: `previews/run_contact_sheet.jpg`.

Vest and labels rigidly follow spine_03; belt/pouches pelvis; sleeve shields upper arms; cargo pockets thighs; boot laces feet; individual facial hair/creases head. Existing MPFB weights still drive human, wardrobe, shoes, eyes, brows, hair and teeth. Rest file and v1 runtime are untouched. The run is an in-place motion review, not exported gameplay animation or cloth simulation. No commit or push.
