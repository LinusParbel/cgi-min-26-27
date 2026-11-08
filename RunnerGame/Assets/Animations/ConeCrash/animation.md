# Special delivery: cone launch

Selected by the user on 2026-11-07. Street mode only. A cone catches the front
wheel: the scooter flips and throws the rider skyward. The officer jumps after
them, catches up in slow motion, and sticks a ticket onto their back. Full speed
returns and the rider flies away into a cartoon twinkle. Keep the launch simple;
no road destruction, simulated space travel or new physics engine.

Status: v9 motion accepted as "good enough for now" on 2026-11-07.
Flight audio revised after user dissatisfaction; soft-air revision implemented
and technically checked. User approved the new sound and requested a live game
playtest on 2026-11-07. Current combined preview: v12 with the aerial environment revision.
Previous recordings retain their historical motion/audio versions.

[Current storyboard](storyboard.svg) | [Review](review.md) | [Audio sources](audio-sources.md)

## Current timed storyboard - continuous pursuit revision

Feedback 2026-11-07: previous cut hovered and felt unnatural. Follow-up: reduce
the initial launch distance and move to the officer sooner (camera move starts
at 2.05 s and finishes at 2.8 s; initial upward speed halved). The rider must
keep rising. After following the launch briefly, the camera moves to the officer,
who runs, plants and jumps after the already airborne rider. The ticket is a
passing slap during continuous flight. Officer falls away; camera follows rider.
No mid-air pose hold and no return to the street at the end.

| Time | Action | Camera / audio |
|---|---|---|
| 0-1.4 s | Front wheel catches cone; scooter flips and releases rider. | Smooth low sweep into launch follow; clack and rattle. |
| 1.4-2.05 s | Rider flips and keeps climbing; scooter falls behind. | Follow rider upward first; rushing air. |
| 2.05-4.1 s | Officer runs up on the street, plants and springs after rider. | Continuous eased move down to running officer; footfalls and takeoff. |
| 4.1-7.3 s | Officer rises on a continuous jump arc and catches rider. | Follow officer up, then ease into a moving rear three-quarter two-shot. |
| 7.3-7.7 s | One passing ticket slap; hand leaves paper attached. | Moving close shot shows contact and attachment; paper slap. |
| 7.7-10 s | Rider keeps ascending while officer loses height and falls away. | Keep rider framed; allow officer to leave below. |
| 10-16.2 s | Follow rider's continuing flight; gradually fall back for shrinking exit. | Smooth upward/forward pursuit, continuous air. |
| 16.2-17 s | Rider disappears in twinkle; hold the sky. | Same continuous view; twinkle. |

Acceptance: rider has positive vertical velocity throughout flight; officer has
a distance-driven deforming run, continuous takeoff and ballistic airborne path;
contact occurs once in passing without magnetically holding both actors together.
The officer approaches from below without overshooting the reduced rider launch.
The initial throw must carry nonzero upward and angular velocity through release.
The launch overlaps the scooter flip from 1.1 s; shared position, linear velocity
and angular velocity continue into separate rider/scooter motion at 1.4 s.
No completed flip followed by a fresh vertical launch.
The scooter remains above the road throughout its tumble and settles onto its
side using actual full-mesh ground clearance, including wheel pivots and bars.
Camera eye and target remain continuous at all shot boundaries. Review full-speed
motion, not just keyframes. Current implementation follows this brief; review evidence is recorded in review.md.

## Gameplay and controls

First accepted street cone contact starts the terminal scene once, including
during ordinary hazard immunity. Preserve actual cone, rider X/Y and duck state.
Freeze distance, score, traffic and pursuit at impact. Jumping cleanly over the
cone does not trigger it. Other hazards, van scene and pedestrian maps keep their
existing behavior. Scene completion enters Caught without automatic restart.
Esc / focus loss pauses motion and audio; explicit Enter / Esc resumes. R resets.
Clear movement inputs while cinematic owns control. Add a repeatable real-contact
preview, timestamps and film capture through the normal renderer.

## Contact and visual acceptance

- Front wheel visibly meets cone before scooter pivots and rider releases.
- Rider and officer use connected, deforming limbs; no static translated acting.
- Scooter and rider share the initial pivot, then visibly separate at release.
- Officer jump begins on supported street, follows a continuous trajectory and
  catches the rider during the same launch, with slow body motion at contact.
- Ticket follows evaluated hand before contact, meets the upper-back surface,
  and follows the rider thereafter. Camera proves hand withdrawal and attachment.
- Both actors continue moving through the brief contact; rider keeps rising while officer falls away. Departure ends in a visible twinkle.
- Cuts are intentional, actors remain framed, sound follows visible events.
- Build/state tests and numeric contacts are technical evidence; full-speed muted
  and audible renderer recordings plus close frames are required for review.
  User review remains the final acceptance gate.

## Ownership

Scene clips, ticket artwork, audio and tracks live here. Shared rider, officer,
scooter, cone meshes and character atlases remain in their current Models folders.
Editable character source and provenance: Art/assets/cone_crash/. Local Python
authoring/export/review tooling remains ignored. Reuse source character identities
and licences. No commit or push without an explicit user request.

## Sound revision

The current flight uses short soft-air launch sweeps, a quiet air bed with room
for the paper slap, and a distance fade. The old spring chirps and pulsing white
noise have been replaced. Other foley and all motion/camera timing are preserved.
See audio-sources.md for production and exact-stem preservation.

## Unresolved / review

Actor motion and soft-air sound were approved in the previous playtest. The new
aerial environment and its full-speed appearance await visual acceptance. Scope is the cone ending; other small-object endings are future work.
No street-return coda: camera follows the rider after the officer falls away.

## Aerial environment revision

Live playtest feedback 2026-11-07: distant gray landmark silhouettes appeared
against the blue sky; the exposed street and facade backs looked hollow and
empty from above. Fix at the responsible layers: match fog to the current sky,
close facade buildings with depth/roofs, extend visible ground/road, and add
complete surrounding blocks outside the landmark plazas. Preserve the accepted
actor motion, gameplay and approved soft-air sound. Keep scenery present before
the collision so it does not appear abruptly when the cinematic starts.

Acceptance: no gray fully fogged silhouettes against blue sky, no visible open
backs or terrain-strip edges in the airborne shots, preserved plaza/monument
clearance, no new camera/actor discontinuity, and evidence at several run
distances because the landmark district moves through the run. Implemented and reviewed in actual renderer captures at preview distances 0, 250
and 390; the final full-speed cut is v12. Geometric checks alone cannot establish
subjective appearance. Shared-model bytes and accepted motion/audio are preserved.
