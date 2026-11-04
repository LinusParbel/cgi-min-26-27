# Cone hat editable source

`cone_hat.blend` contains the existing civilian rig with a baked 53-bone action,
frames 1–673 at 24 fps. Open it in Blender 5.2 to edit the road cut's character
motion. Runtime playback samples the exported 30-second mesh clip.
The runtime's last 49 samples reuse the same mounted pose, holding the final
body action while the scene track completes the thirty-second handoff.
The combined export template is hidden; the rigged source meshes are visible.
Scene-level positions, cone motion and cameras are authored in the runtime
`Assets/Animations/ConeHat/scene.json`, separate from the local character action.

The specification and acceptance criteria live only in
[animation.md](../../../Assets/Animations/ConeHat/animation.md).
Runtime meshes, clip data and sound cues live beside that document.

This is new animation of existing project characters, not a newly adopted
character model. Rider sources and their provenance remain in
`../scooter_rider/`; officer source records remain in `../ordnungsamt_pursuer_v2/`.
The civilian, officer and prop licences/attributions in `RunnerGame/CREDITS.md`
still apply. Runtime exports reference the existing atlases without copying them.

Local ignored scripts `build_road_cinematic.py`, `road_motion.py`,
`generate_audio.py` and `validate_export.py` author and check the deliveries.
They are deliberately not required to run a clean checkout.
`provenance.json` records source/delivery hashes.
