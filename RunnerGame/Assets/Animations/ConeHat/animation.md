# Cone hat opening animation

Status: chosen concept; animation and audio not yet implemented.

Concept ID: `cone_hat`. Selected by the user on 2026-11-02.

## Scene and intended behaviour

The rider takes a street traffic cone and wears it as a hat. An Ordnungsamt
officer catches them interfering with the street equipment. The offence is
petty and visually obvious; the officer's exaggerated determination makes the
resulting chase funny.

Proposed sequence, to refine before implementation:

1. The rider walks casually toward the scooter and notices a traffic cone.
2. They pick up the cone, put it on their head and swagger a few steps.
3. An officer clears their throat or calls out. The rider freezes and turns
   until the officer becomes visible through the cone opening.
4. A short, awkward pause. The rider slowly removes the cone, pretending
   nothing happened.
5. They drop the cone and sprint to the scooter. The cone wobbles behind them.
6. A brief clumsy mount and an ill-timed scooter beep, then takeoff.
7. The officer runs after them; the camera settles into the gameplay chase
   view and control passes to the player.

Proposed sound cues: city ambience, walking footsteps, cone handling and a
plastic clatter, an officer throat-clear or "Stehenbleiben!", rapid footsteps,
scooter beep and acceleration. Let the pause carry the joke; avoid covering
every movement with a sound effect. Exact cues, voice recording, music and
sound licensing are undecided.

An existing cone model, scooter, riding poses and officer run animation are
starting points. Check that the cone opening and scale work for the gag.
Walking, cone handling, reactions, sprinting and mounting need animation work;
existing assets do not imply that these actions are already supported.

## Transition into gameplay

End with the rider mounted, scooter moving along the active route, officer pursuing, chase camera ready and player control enabled. Starting positions, speed and pursuit state must give the player a fair start; the intro must not count as a gameplay collision or damage event.

## Files and dependencies

This folder owns the cone intro specification and future scene-specific runtime files. Reference shared cone, scooter and character assets in their existing model folders instead of copying them here. Editable sources and provenance belong in `RunnerGame/Art/assets/cone_hat/` when created; local Python tooling remains ignored.

## Decisions still needed

Duration, staging location for supported maps and street mode, camera shots, animation method, sound sourcing, and first-play, restart and skip behaviour. The scene sequence and sound cues above are proposals to refine before implementation.

## Timing proposal for discussion

This is a proposed 12-second cut, not an approved duration or finished clip.

| Time | Action and purpose |
|---|---|
| 0-3 s | Casual approach, pick up cone, put it on and swagger. Establish the scooter nearby so the escape direction reads. |
| 3-6 s | Officer interruption, freeze, eye contact and slow cone removal. Hold the awkward silence long enough for the joke to register. |
| 6-10 s | Drop and wobble, sudden sprint, clumsy scooter mount and badly timed beep. |
| 10-12 s | Pull away, officer starts running, camera blends into the chase view and player control begins. |

Keep the cone's broad opening over the rider's head and test visibility before
committing to a shot through the opening. If the opening hides the face,
stage the officer reveal with a head turn and readable body reaction instead.

## Current implementation findings

Repository inspection on 2026-11-02:

- The game renders exported OBJ poses rather than a skeletal animation system.
  The street renderer samples four officer run poses from the installed set.
- Editable rider files include `rider_rig.blend` and `final_assembly.blend` under
  `Art/assets/scooter_rider/`. Inspect the actual rig before choosing how to
  author the new actions; filenames alone do not establish rig readiness.
- No audio playback implementation was found in the Engine or RunnerGame C#
  code. Sound cue timing needs playback support as well as licensed audio.
- Gameplay currently has Ready, Running, Paused and Caught phases. The intro
  needs an explicit playback and input handoff design so its animation time
  cannot advance gameplay obstacles, scoring or damage before control begins.

Next design step: settle pacing and storyboard, inspect the rider rig and cone,
then choose the clip export and playback approach before implementation.

See [../README.md](../README.md) for the animation folder convention and [../../../Art/ANIMATION_IDEAS.md](../../../Art/ANIMATION_IDEAS.md) for other opening concepts.
