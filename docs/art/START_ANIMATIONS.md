# Opening animation ideas

Status: concept backlog. No opening animation or audio is implemented by this
document. The chosen concept is approved; timing, animation details and the
technical implementation still need to be worked out.

## Chosen opening: cone hat

**Concept ID:** `cone_hat`

**Selection:** chosen by the user on 2026-11-02.

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

## Alternative openings

These remain ideas, not selected or scheduled work. Preserve them so another
opening can replace the cone scene or join a future selection of intros.

| Concept ID | Premise | Comedy beat | Additional needs |
|---|---|---|---|
| `litter_bin` | The rider throws a cup beside a bin, at the officer's feet. | They point accusingly at a pigeon before fleeing. | Cup, throw/drop, accusation gesture; pigeon if shown. |
| `flowerbed_shortcut` | The rider takes a shortcut through a flowerbed past a "Betreten verboten" sign. | They try to reverse through their exact footprints, then crunch a flowerpot. | Flowerbed, sign, pot, backward steps and crunch cue. |
| `pigeon_feeding` | The rider feeds pigeons beneath a prohibition sign. | One breadcrumb summons an absurd cloud of birds; an officer's whistle interrupts. | Sign, feeding gesture, animated pigeons and wing sounds. |
| `poster_moustache` | The rider draws a moustache on a public poster. | They notice the officer in the glass reflection and hide a marker that still squeaks. | Poster, marker, drawing and hiding gestures; reflection or another readable reveal. |
| `cafe_chair` | The rider takes a cafe chair to use as a scooter seat. | They notice the officer, carefully replace and straighten the chair, then bolt. | Chair carrying/placing, scooter-seat gag and reaction. |

## Keeping openings interchangeable

Design direction for later implementation, not an existing engine feature:

- Keep the chosen opening identified by its concept ID, initially `cone_hat`.
- Give each opening its own staged actions, prop requirements, camera cues and
  audio cues, rather than embedding the cone gag into normal running gameplay.
- End every opening at the same handoff: rider mounted, scooter moving along
  the active route, officer pursuing, chase camera ready and player control
  enabled. Scene staging must be checked for each supported map or street mode.
- Define the handoff's exact positions, speed and pursuit state during technical
  design. It must preserve a fair start rather than accidentally count the
  opening as a gameplay collision or damage event.
- When adding an idea, assign a new concept ID and add its entry above. When
  switching openings, update the chosen concept and its selection record here.
- A random intro pool, player selector, skip/replay controls and alternate
  openings are possible future features; none are included merely by recording
  this direction.

Before building, settle duration, staging location, camera shots, animation
method, sound sourcing and how first play, restart and skipping should behave.
Then write the implementation plan for the selected opening.
