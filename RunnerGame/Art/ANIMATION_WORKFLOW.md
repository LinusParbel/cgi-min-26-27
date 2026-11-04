# Game animation workflow

Use this workflow for a new game animation or a substantial revision to an
existing one. The per-scene `animation.md` remains the source of truth for what
that particular scene should do; this document describes how to get from that
brief to an animation that reads well in the running game.

For the required folder layout and ownership, follow the animation conventions
in the root `AGENTS.md` and `RunnerGame/Assets/Animations/README.md`.

## 1. Understand the scene before building it

- Inspect the game startup, renderer, current runtime assets and relevant
  character or prop sources. Identify what already plays in the real game and
  which path a preview or capture uses.
- Agree on the scene's purpose, tone, duration, gameplay mode, start and end
  state, and what must remain unchanged. Keep unrelated map or gameplay work
  out of scope unless requested.
- Write or update the scene's `animation.md` before detailed authoring. Record
  the intended action, shot sequence and timing, camera, audio cues, asset
  dependencies, gameplay handoff, implementation status and unresolved
  decisions.
- Turn user feedback into observable acceptance criteria. Say what must be
  visible or audible, and what evidence will show it. Distinguish planned,
  implemented, technically checked, visually reviewed and user accepted work.

## 2. Block the story and staging

- Make a storyboard or timed shot list before refining character motion. Show
  who is in frame, where they are, how far apart they are, what the camera
  reveals and when each action happens.
- Check that the joke, emotion or dramatic change reads without sound. Preserve
  enough screen time for reactions and transitions; don't rush straight from
  setup to payoff.
- Block positions, camera and rough timing in the game renderer. Fix staging,
  distance, framing and continuity before spending time on fine rig work.
- Keep one clearly identified current storyboard linked from `animation.md`.
  Label superseded images as historical or remove them from the active links so
  old timings cannot be mistaken for the current cut.

## 3. Animate contact and locomotion, not just transforms

- A walk or run needs a deforming gait. Do not create locomotion by translating
  a static character or by cycling a few visibly repeated poses.
- Drive footfall phase from distance travelled or a consistent gait clock.
  Check planted stance, lift and swing at normal playback speed, including a
  side view. Keep the body motion and step sounds in time.
- Keep limb chains connected. Check evaluated hands, feet and the visible mesh
  against props and ground; bone targets and numeric rig measurements alone do
  not prove contact looks right.
- Plan prop interactions in order: approach, grip, lift or move, release, and
  settle. Check head clearance, grip changes, foot placement and final pose in
  close views as well as in the wide shot.
- Use camera motion and cuts to reveal information deliberately. Check spacing
  and screen direction across cuts, then check the handoff into gameplay for a
  jump in actor, camera, speed or controls.

## 4. Diagnose visual defects at the right layer

When an image looks wrong, preserve the screenshot or frame and trace the full
render path before choosing a fix. A see-through surface can come from distinct
causes:

1. Material opacity or blending settings.
2. Alpha values in the texture, including the actual UV region used by the
   visible surface.
3. Missing or cut-away geometry, open surfaces, normals or depth behavior.
4. Camera angle, occlusion, z-fighting, lighting or shadows that only resemble
   transparency.

Inspect the source mesh and its modifiers as well as the exported runtime mesh.
Fix the editable source or generation step, regenerate the runtime asset, and
review the result from the same camera and game renderer. Do not stop after a
material change if the symptom remains.

## 5. Make sound part of the action

- Cue footsteps, impacts, prop handling and movement from the action they
  describe, not from arbitrary frame counts. Review timing against the motion.
- Prefer suitable human-recorded performances and recognizable real-world
  effects when they improve the scene. Synthetic or processed audio is a
  deliberate choice; don't assume changing speed or volume alone makes a voice
  sound natural.
- Record source links, creator, license and processing in the scene's
  `audio-sources.md`. Keep runtime audio beside the scene and don't ship
  unlicensed or undocumented source material.
- Review the complete mix at normal playback speed. Check intelligibility,
  repeated cues, overlaps, levels, clipping and pause/skip/restart behavior.

## 6. Integrate and review in the real game

- Connect the scene through its normal runtime path. A rendered preview is not
  proof that the game starts or plays the scene; inspect the startup/loading
  path and launch the actual game when possible.
- Build after changing runtime code or generated assets. Use the real renderer
  for a full-speed video and a contact sheet of key beats. Add close captures
  for hands, feet, face/head fit, prop geometry and transitions where needed.
- Review the full motion at normal speed; contact sheets cannot prove gait,
  acting or sound quality. Check the captured cue log or timeline alongside the
  mix.
- Compare the evidence with each acceptance criterion. Record failures and
  unknowns in `review.md`; do not mark visual or audio criteria passed because
  a build, export or numerical check succeeded.
- When feedback points to a defect, update the scene brief or acceptance
  criteria if needed, identify the responsible layer, fix the source, rebuild
  and capture again. Check that the fix did not break adjacent beats or the
  gameplay handoff.

## 7. Keep sources, runtime data and review records aligned

- Put the editable Blender/source project and provenance in
  `RunnerGame/Art/assets/<animation_id>/`. Put scene-specific runtime meshes,
  clips, scene data and audio beside the scene's `animation.md` under
  `RunnerGame/Assets/Animations/<AnimationName>/`.
- Keep shared characters, props, textures and reusable animation clips in their
  existing model folders. Do not copy a shared asset into a scene folder just
  to make authoring convenient; create a scene-specific variant only when the
  scene requires a real change.
- Keep local generation and review scripts under existing ignored rules. Make
  the editable source and export process agree with the checked-in runtime
  output. Refresh hashes, source notes and validation reports after changing
  generated assets.
- Update the active storyboard, `animation.md`, `review.md`, README commands
  and provenance together when the cut changes. Remove stale counts, timings or
  preview links from active documentation.
- Do not commit or push without the user's explicit instruction. User review is
  the final acceptance gate for subjective animation and audio quality.

## Lessons from the cone-hat opening

The first cut was too short, staged the officer too close, and used sliding or
repeated poses instead of readable walk/run cycles. Clear shot timing, greater
separation, continuous motion, better hand contact and a longer reaction made
the story easier to read. Footstep and scooter sounds needed source and timing
review; repeated synthetic calls needed an escalating delivery and a human
recorded chase shout. The cone also showed why visual diagnosis must include
geometry: its texture alpha was fully opaque, but a deep Boolean cut removed
part of the lower wall. The durable fix was to reduce the source cutter and
re-export the runtime mesh.
