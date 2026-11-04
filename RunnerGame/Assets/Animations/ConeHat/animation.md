# Cone hat opening animation

## Current direction

Concept ID: `cone_hat`. **Road mode only.** Hannover pedestrian map integration
is deferred at the user's request on 2026-11-02.
The first 12-second cut was rejected for sliding, an obvious nearby officer,
poor hands and rushed acting. Its recordings are historical, not acceptance
evidence for this revision.

Target: a roughly **30-second cinematic**. This document describes the intended
result; numerical tests alone do not establish that the acting looks good.

[Storyboard](storyboard-road-v4.svg) | [Implementation plan](implementation-plan.md) |
[Other openings](../../../Art/ANIMATION_IDEAS.md) | [Review](review.md)

## Story and tone

The rider casually takes a cone and wears it as a hat. The officer is on patrol
farther down the street, initially outside the frame. The camera reveals them
later. They notice the misuse and call out. Hold the rider's guilty reaction;
the rider removes the cone, attempts a casual walk to the scooter, then breaks
into a run. A small mounting fumble and beep finish the gag before gameplay.

The petty offence, officer's earnest response and rider's attempt to look
innocent carry the humour. No aggressive physical confrontation is needed.

## Shot specification

| Shot | Time | Action | Camera and sound |
|---|---|---|---|
| S01 | 0-4 s | Rider approaches cone; officer patrols far behind, unrevealed. | Moving three-quarter establishing view; ambience and steps. |
| S02 | 4-7 s | Crouch, grip, lift in front of face, place cone over head. | Medium view showing hands/feet; handling scrape. Cone must clear face. |
| S03 | 7-9 s | Proud cone-hat walk; hands release naturally. | Gentle tracking shot. Officer remains outside the early framing. |
| S04 | 9-11 s | Camera reveals distant officer as they finish a patrol step and notice rider. | Background reveal, not an officer already beside the rider. |
| S05 | 11-12.3 s | Officer raises a hand and calls “Hey!” | Pulled-back full-figure officer shot; first call is controlled and carries across the reaction cut. |
| S06 | 12.3-15 s | Rider looks back and holds an awkward guilty reaction. | Reaction shot/slow push; at least one second of quiet after the call. |
| S07 | 15-17 s | Slow removal, innocent look, release beside rider. Cone lands and rocks. | Show head clearance and ground contact; plastic impact on contact. |
| S08 | 17-20 s | After the awkward pause, the officer steps forward while the rider tries to walk away casually. | Wide down-road view; “Stehen bleiben!” is repeated with a firmer, increasingly angry delivery. |
| S09 | 20-24 s | Rider breaks into a run toward the scooter; officer follows after a short delay. | Brief closer officer run shot, then a wide two-shot; a human-recorded German chase call replaces the repeated synthetic voice. |
| S10 | 24-27 s | Reach handlebar, step aboard, brief fumble, settle into riding pose. | Medium side view; shoe/deck contact, kickstand clack and one badly timed beep. |
| S11 | 27-30 s | Scooter accelerates; camera settles behind rider; officer remains well back. | Motor cue, continuous ambience, then player control. |

Intentional shot cuts are allowed at reveal/reaction/mount beats. Moving shots
need eased starts/stops. No accidental camera or character jump at handoff.

## Motion and contact requirements

- Both walk/run cycles deform the rig. The officer holds through the awkward
  pause, then walks forward before running; no frozen officer is translated
  along a path and no four-pose stepping is substituted for a smooth run.
- Gait phase follows distance travelled, with planted stance, heel/toe roll and
  a lifted swing. Review at normal speed and from the side.
- Wrist/elbow and ankle/knee joints remain connected. Solve reachable limb
  targets and adjust pelvis height; never detach hands to reach a prop.
- Hands follow forearms with anatomical roll. Walking hands relax; running
  elbows bend. Wrists cannot hang in one fixed orientation.
- Cone and bar grips use palm/knuckle targets; fingers and visible mesh contact
  must also be checked. A bone-target test is insufficient by itself.
- Cone stays in front of the face while being lifted, then fits over the head.
  Its head opening is limited to the base so the lower cone wall remains solid;
  it reuses the shared texture.
- Worn cone follows the evaluated head shape, including walking and looking
  back. It is fully opaque, with no road or face showing through; it does not
  hover forward or pass through the face.
- Mounting establishes a near-hand grip, then both grips and foot placement.
  End at the installed riding geometry.
- Foot/prop shadows establish contact and persist into gameplay.

## Staging and handoff

### Hannover street setting (2026-11-04)

The straight road now includes the shared Neues Rathaus model across an open
forecourt on the left, at 55% scale, and the shared Kröpcke clock in a larger
square on the right. Shopfront gaps expose both squares; benches, planters and
trees frame the forecourt. This is a stylized Hannover composition rather than
the geographic pedestrian route. Shared assets remain in `Assets/Models/`.
The district repeats every 420 metres and moves with the road during gameplay.
Existing character, camera and sound tracks remain the scene's staging inputs.

Implemented in `Rendering/SceneRenderer.cs`; actual renderer captures reviewed
for the opening, 24-second mounting approach and initial gameplay view. Final visual acceptance and a fresh
full-speed review of the enriched environment remain user review items.
Local evidence: `docs/art/previews/hannover-monuments-intro.bmp` and
`docs/art/previews/hannover-monuments-run.bmp` (repository-root paths).
The clock-square view is `docs/art/previews/hannover-monuments-mount.bmp`.

The 2026-11-04 gap correction encloses both squares with rear and side
shopfront rows, covering the empty background beyond the paving while leaving
the monuments visible from the street. Updated actual-renderer captures:
`docs/art/previews/hannover-squares-enclosed-clock.bmp` (24 s) and
`docs/art/previews/hannover-squares-enclosed-rathaus.bmp` (0 s). Both were
visually reviewed; the rebuild completed with zero warnings and errors.

Corner refinement: square openings now align with the 6 m street façade grid.
Side modules are sized to meet the street row instead of crossing through it;
rear corner joins allow for the models' recessed panels and projecting trim.
All wing rotations remain exact right angles. Updated captures are
`docs/art/previews/hannover-corners-clock.bmp` and
`docs/art/previews/hannover-corners-rathaus.bmp`.

The officer is outside the opening shot and at least 12 m away during the call
and at handoff. Working staging gives roughly 16 m separation at interruption.

The scooter is parked 18 m behind the final gameplay origin. During the last
three seconds it accelerates to that origin, ending at the normal 12 m/s.
Rider, scooter, wheels and camera must agree: no teleport or speed reset.

Extend the road environment behind the normal start so actors and cameras
remain on visible ground. The released cone stays behind the riding start,
outside the escape path, with no gameplay collider.

Intro time cannot advance hazards, scoring, coins or damage. The officer's
visual staging is separate from the first-hit/second-hit timer.

## Controls

- Enter/Space starts; a fresh press after release skips.
- Held Start cannot immediately skip; a resume press cannot also skip.
- Esc/focus loss pauses animation and sound; focus return alone never resumes.
- Enter/Esc resumes. R stops sounds and resets to Ready.
- Completion/skip invoke one clean handoff exactly once, with cleared input.
- Maps keep their ordinary controls and do not play this road cinematic.

## Sound and files

Cues follow action events, not frame counts. Impact follows landing; beep
follows the fumble; steps follow footfalls. Pause/skip/restart cannot duplicate
cues or leave loops behind. Respect mute and volume.

The first calls use locally synthesized German speech, with progressively firmer
delivery as the rider ignores the officer. When the rider runs, use the human
recorded German chase call instead of repeating the synthetic line. Keep calls
spaced so they remain intelligible over footsteps and scooter handling.
[audio-sources.md](audio-sources.md) records production and hashes; voice
performance remains a listening-review point.

Scene files, clips, cone variant and audio live here. Shared textures and scooter
geometry stay in `Assets/Models/`. Editable source is
`Art/assets/cone_hat/cone_hat.blend`; Python tooling stays local/ignored.
[asset-validation.json](asset-validation.json) records export measurements.
VCL2 aliases identical held poses to avoid redundant frame data.

## Acceptance criteria

| ID | Required result | Evidence |
|---|---|---|
| AC01 | All 11 beats read in order, including walking before running; joke reads muted. | Full normal-speed and muted road review. |
| AC02 | Approximately 30 s active playback; deliberate quiet after the call. | Clock tests, capture times, cue log. |
| AC03 | Both characters walk/run smoothly, with grounded stance, lifted swing and speed-matched motion. | Two-character walk/run captures, full recording, and all officer walk samples checked against ground. |
| AC04 | Grip target error below 2 cm; wrist/ankle joint gap below 3 mm; fingers and wrists look natural. | Export measurements plus close contact views. |
| AC05 | Cone clears face, fits evaluated head, remains attached without hovering, and has no visible cut-through in its lower wall. | Head-fit regression and pickup/swagger/reaction views; no road or face shows through the lower cone. |
| AC06 | Officer is outside early framing, revealed later, and at least 12 m away at call/handoff. | Framing/distance checks and full recording. |
| AC07 | Release is continuous; landing/rocking stay on ground outside escape path. | Ground-contact regression and S07 review. |
| AC08 | Cuts are intentional; moving shots ease; camera/rider transition into play has no snap. | S11 plus first second of gameplay. |
| AC09 | Correct hand/bar and foot/deck contact after intended grips/plants; final pose matches riding mesh. | Mount detail and endpoint comparison. |
| AC10 | Call, steps, impact, beep, motor read clearly; impact/beep within 100 ms of visual event; no clipping. | Cue/waveform analysis and listening review. |
| AC11 | Skip/completion enter equivalent clean state once; no intro game progression. | Boundary/state tests. |
| AC12 | Start/hold/skip/pause/focus/restart avoid stale input, duplicates and orphan sound. | State/audio tests; live keyboard review when available. |
| AC13 | Road/cameras avoid scenery, shadows ground actors, maps launch without intro. | Road captures and map smoke checks. |
| AC14 | Current spec/storyboard, source/audio provenance and review commands accompany delivery. | Documentation and clean build checks. |

Record results and limits in [review.md](review.md). Do not mark visual criteria
passed solely because a unit test or an export succeeded.
