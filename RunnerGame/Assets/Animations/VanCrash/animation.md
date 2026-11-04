# The street gives up

Concept selected by the user on 2026-11-03. The user approved one immediate,
terminal van collision, including on the first hit. Other hazards retain their
existing rules. Status: implemented and technically checked; renderer keyframes
reviewed. The user approved the delivered preview with "looks good" after reviewing
the six-second video with sound. Integration into the other game work is pending.

[Current storyboard](storyboard.svg) · [Review](review.md) · [Sound sources](audio-sources.md)

## Intent and sequence

A six-second cartoon failure. The rider hits a parked delivery van; the street
responds as though it has had enough. The van remains absurdly unmoved. The joke
must read muted, without text or dialogue explaining it.

| Time | Action | Camera | Sound |
|---|---|---|---|
| 0–0.45 | Abrupt stop against rear of van; rider recoils, elbows bend. | Ease out of chase into a three-quarter full-body view. | Hollow metallic impact, short rattle. |
| 0.45–1.50 | Rider recovers, looks offended; jagged cracks spread under scooter. | Show rear of van, rider and ground together. | Asphalt crackle. |
| 1.50–2.30 | Two road flaps give way beneath rider; van stays on intact road. | Hold framing so the hole is unmistakable. | Crunch and falling debris. |
| 2.30–3.30 | Rider hangs impossibly above the hole, looks down, arms spread; legs pedal. | Hold the pause. | Quiet, then a small questioning squeak. |
| 3.30–4.45 | Rider drops feet first with flailing limbs; scooter follows a little later. | Stay above ground; do not chase the body underground. | Descending whistle; scooter rattle. |
| 4.45–6.00 | Empty hole, van still parked; one last piece of road falls. | Hold the aftermath. | Distant soft thump, delayed tiny stone tick. |

Timing and exact poses are implementer defaults, subject to visual review.
No gore, injury detail, dialogue, or full-map destruction.

## Runtime and gameplay handoff

- Real accepted van contact starts the scene exactly once, including during
  ordinary obstacle invulnerability. Van remains a solid terminal obstacle.
- Freeze distance, coins, score, traffic and pursuit progression at contact.
  Keep the collision van's actual position and rider lateral/vertical state.
- Side hits rebound the rider/scooter behind the van over 1.1 seconds before
  the road opens, preserving intact road beneath the parked van. Duck contacts
  blend from the installed crouch into the crash action over 0.7 seconds.
- Disable lane/jump/duck input during the scene. Completion enters Caught;
  show a van-specific game-over status. No automatic restart or resumed run.
- Esc/focus loss pause scene and audio. Focus return alone cannot resume.
  Enter/Esc resume; R clears scene/audio and returns to Ready from any beat.
- Street mode only: pedestrian maps generate planters instead of vans; do not
  add vehicles or change their map/gameplay behavior for this scene.
- Add a repeatable preview and timestamp capture path using the same collision
  code and renderer as normal play; label preview controls in the README.

## Assets and ownership

Reference shared DeliveryVan, ScooterVoi and ScooterRider models and rider atlas.
Author connected limb motion from the existing rider rig, with recoil, head
reaction, reaching arms and kicking legs; rigid translation alone is insufficient.
Scene-specific road geometry, rider clip and audio belong here. Editable source
and provenance belong in `Art/assets/van_crash/`. Local Python tools are ignored.
The existing road must actually have an opening: do not cover intact geometry
with a dark decal and move the rider through it.

Sound is deliberately original synthesized cartoon foley, without speech;
document creation, ownership and processing in audio-sources.md. Cue from scene
time, respect mute, stop on reset and pause without replaying earlier sounds.

## Acceptance and evidence

1. First-hit van contact triggers once; non-van two-hit rules remain unchanged.
2. Collision snapshot and score stay frozen; scene ends at six seconds in Caught.
3. Pause, focus loss, resume and restart behave correctly at multiple beats.
4. Road visibly cracks and opens beneath the rider; van remains on solid ground.
5. Recoil, downward look, air pause, kicking and separate scooter drop read muted.
6. Shared appearance is preserved; no obvious mesh tears, limb disconnects or
   intact road occluding the hole. Review close and normal-speed captures.
7. Impact/crack/drop/thump/tick synchronize; mix has no clipping or stale cues.
8. Build, relevant suites, real renderer keyframes and normal-speed video/audio
   accompany review.md. Numeric checks do not establish subjective acceptance.

User review is the final acceptance gate. Do not commit or push without request.
