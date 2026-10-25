# Officer v2 hand orientation correction

User identified unnatural fist/hand angles in the smoothed run GIF.

## Cause and correction

The old hand rotation reused the shortest-arc forearm aiming quaternion, which did not constrain anatomical hand roll. Its wrist lag was also applied about the hand's local X axis. Frame inspection showed the raised fists rolled palm-down and drooping.

`animate_run.py` now builds an anatomical frame from the wrist-to-middle-knuckle direction and pinky-to-index direction. It maps that frame onto the moving forearm, with thumb side up and a small inward inclination. Secondary wrist motion is 2 degrees about the world sagittal axis. Finger curls, stride, elbow motion and model are retained.

## Outputs and checks

- Latest preview: `RunnerGame/Art/assets/ordnungsamt_pursuer_v2/previews/officer_v2_run_natural_hands.gif`; standard and smooth GIF aliases are also updated by `make_run_gif.py`.
- Editable animation: `officer_v2_run_preview.blend`.
- `verify_hands.py`: all 41 keyed poses, maximum wrist angle 1.99243 degrees, minimum thumb-up alignment 0.97993. Uses anatomical landmarks rather than the tiny hand bone's axis.
- `verify_run.py`: sole checks, bone lengths, equipment transforms and zero loop seam error pass.
- `analyze_run.py`: pelvis/wrist trajectory metrics unchanged by the orientation correction.
- Initial three-quarter and side rendered poses inspected before full rendering.

This remains a procedural preview. Neutral source and runtime assets are not modified.
