# Cone launch editable sources

`rider.blend` and `officer.blend` contain the existing project character skeletons
with newly keyed cone-crash actions, frames 1-205 at 12 fps (17 seconds).
The only visible mesh in each file is a skinned copy of that actor's installed
atlas topology. The shared character atlas is referenced by a relative path;
it is not copied into the runtime scene. Source files can be edited in Blender 5.2.

The baseline meshes come from the existing van scene's atlas-preserving clips.
Skin weights were transferred from evaluated source character meshes using nearest
surface vertices, then normalized; the original connected skeleton was baked to
the baseline rest pose. The officer's rigid uniform details receive nearby source
skin weights. Review these details when changing poses substantially. Original
character licences and provenance remain in `../scooter_rider/` and
`../ordnungsamt_pursuer_v2/`, and RunnerGame/CREDITS.md.

The rider action covers recoil, continuous arm/leg flailing and a backward head turn.
The distance-driven run-up reuses ConeHat/officer_motion.vclip at runtime, blending
its standing/run samples into the local crouch before takeoff at 4.1 seconds.
The original frame-one officer bind pose is retained to preserve finger and sleeve
skinning. Grounded crouch samples receive a measured sole-clearance correction;
runtime standing/run samples blend into that crouch before the jump. The
officer action covers crouch, spring, trailing legs, reach, one brief passing paper slap
and hand withdrawal. Body trajectories, initial shared front-wheel pivot, release,
slow-motion pursuit, camera and departure are authored in
`RunnerGame/Animation/ConeCrashMotion.cs`. This separation is intentional: the
Blender actions are local body deformation; the game timeline stages the actors.

Runtime exports: `Assets/Animations/ConeCrash/rider.vclip`, `officer.vclip`,
`rider-contact.json` and `officer-contact.json`. Contact tracks use the same
sampled rig/mesh evaluation as the clips. The back marker is an actual upper-back
mesh vertex; the palm marker comes from the evaluated right-hand bone. The game
places the ticket 14 mm outside the surface and solves a ballistic jump that
meets it once at 7.3 seconds. The officer then pushes away and falls; paper follows
the rider, with no mid-air actor attachment. Continuous camera staging follows
launch, run-up, jump, moving contact and the rider departure.

`validation.json` beside the runtime clips records source weight-transfer distances,
joint-chain gaps, topology counts and clip hashes. These are technical evidence,
not a substitute for renderer motion/contact review. `provenance.json` here records
source and delivery hashes. Ticket artwork and synthesized cartoon foley are
original project work, CC0-1.0; audio details are in the runtime scene folder.

The local repair_skin.py finishing pass reweights four dark hip vertices
accidentally bound to a nearby hand, then re-exports the same keyed source action.
This repair is included in officer.blend and the runtime clip; validation.json
records the repaired vertex IDs and refreshed clip hash.

Local ignored Python: build.py (rig authoring / indexed half-float VCL export),
audio.py (PNG artwork and WAV), fix_source_paths.py (portable atlas references),
contact_sheet.py and video.py (review packaging). No Python or Blender dependency
is added to game startup. The editable rigged sources and runtime output are
retained; local generation scripts are intentionally ignored by repository policy.

Requirements and current storyboard: ../../../Assets/Animations/ConeCrash/animation.md.

## Flight audio revision 2

Current audio uses revise_flight_audio.py after the legacy audio.py source. It
reconstructs and verifies the old mix, retains the exact non-flight stems, and
replaces only launch/jump/wind/fall/departure with soft filtered air. Three local
auditions are produced; soft air is the current default. Running audio.py alone
would restore the old sound. Runtime audio-sources.md and audio-validation.json
record this revision. Motion files are unchanged.

## Delivery packaging

The officer clip uses existing VCL2 identical-frame aliases: 205 samples share
162 unique compressed frame payloads. All decoded frame bytes are unchanged.
This reduces the asset from 128,029,201 to 101,684,047 bytes for repository delivery.
