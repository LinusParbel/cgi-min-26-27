# Original six-second van crash review — historical

This archived review covers the initially approved cut. The current officer-ticket
revision is assessed in [review.md](review.md).

Branch: `feature/van-crash-animation`, isolated worktree `.worktrees/van-crash-animation`.
Base: `908f190`. Changes are uncommitted. No other checkout's unfinished intro
implementation was copied or changed.

Acceptance update, 2026-11-04: the user responded "looks good" to the delivered
video preview with sound. This records approval of that cut's appearance, timing
and mix; it does not imply an additional interactive playtest or approval to
commit, merge or push. The outstanding user-review notes below describe the
original delivery state and are superseded by this preview approval.

## Technical verification

`dotnet build RunnerGame/RunnerGame.csproj --no-restore -p:NuGetAudit=false`:
passed, zero warnings and errors. All seven console harnesses passed using
`dotnet run --project <project> --no-restore -p:NuGetAudit=false`:

| Harness | Evidence |
|---|---|
| RunnerGame.Tests | 28 checks; immediate van, immunity, side rebound clearance, real rear/side/duck/air previews and existing obstacle rules |
| RunnerGame.InputTests | 10 checks; frozen world/score, scene pause/focus/resume, restart across six action beats, existing input behavior |
| RunnerGame.AudioTests | Actual Windows waveOut device: seek after clock discontinuity, paused sample position, resume, restart, completion and mute |
| RunnerGame.AnimationTests | Existing intro checks; both road-flap normals, deforming clip, crouch endpoint, finite samples/normals, endpoint clamp |
| RunnerGame.RouteTests | Route geometry, arc length, extrapolation and invalid input |
| RunnerGame.Rendering.Tests | Seven existing manifest contracts |
| RunnerGame.MapRenderTests | Existing metadata compatibility/validation and shadow coverage/translation |

The first van/immunity tests were observed failing against the old stumble
behavior. The audio seek regression failed with drift correction removed and
passed after restoration. The flap-normal check failed on the reversed right
surface and passed after correcting winding. New side/duck/air contact fixtures
exercise real simulation movement rather than forcing an animation state.

Initial NuGet restore attempts failed due sandbox TLS/credential restrictions;
the existing packages were restored with approved escalation. Final runs above
passed without restore. No remaining test failure is hidden by that setup issue.

## Real renderer evidence

All media lives in the ignored `docs/art/previews/` area of this worktree:

- `van-crash.mp4`: six seconds, 1280×800, 30 fps, generated from 181 real game
  renderer BMPs and muxed with the authored mix. This is deterministic audiovisual
  timeline evidence, not a loopback recording of the audio device.
- `van-crash-contact-sheet.png`: current frames at 0, .30, .90, 1.80, 2.60,
  3.00, 3.50, 3.83, 4.10, 4.80, 5.30 and 5.90 seconds.
- `van-crash-frames/frame-0000.bmp` through `frame-0180.bmp`: current full cut.
- `van-crash-side.bmp`: 2.8-second side-entry case; opening is behind the van,
  rider/scooter rebounded behind it, van remains on intact road.
- `van-crash-duck.bmp`: crouched collision at time zero, retained in initial pose.
- `van-crash-air.bmp`: airborne collision at time zero, retained above the road.

Keyframe inspection confirmed the opening is actual removed ground, hinged halves
remain attached to its sides, the van does not fall, the rider goes down before
the scooter, and the end holds the empty hole. Rider limbs remain part of the
deforming source mesh in the inspected views; this is not proof of every contact
at every time. Normal-speed subjective acting and audio quality still need user
review of the video or interactive preview.

The first full capture exposed a dark right-hand patch before the crack: its
normal pointed downward. Corrected winding and matching complementary edges
removed that early reveal. In the regenerated time-zero capture, closed-flap
and adjacent-road sample RGBs were `(69,71,73)` and `(68,71,73)`; the small
remaining difference follows lighting position. The old `van-crash-hang.bmp`
predates final framing; it is historical, not the current cut.

## Acceptance assessment

| Criterion in animation.md | Result |
|---|---|
| 1 — immediate van; other obstacle rules | Technically passed, simulation suite |
| 2 — freeze world; six-second Caught endpoint | Technically passed, input suite |
| 3 — pause/focus/resume/reset | Technically passed, input and native audio suites |
| 4 — opening; van support | Keyframes reviewed for rear and side; numeric clearance checked |
| 5 — recoil/look-down/hang/kick/delayed scooter | Implemented; keyframes reviewed; normal-speed comedic readability awaits user |
| 6 — appearance and connected pose/contact | Source rig retained; no obvious tears in inspected rear/side/duck/air views; final subjective approval pending |
| 7 — sound synchronization/mix | Cue timestamps, zero clipped PCM samples, native transport and seek checked; subjective timbre/levels and live audiovisual review pending |
| 8 — build/tests/media/docs | Delivered, with limitations explicitly recorded here |

## Independent review and fixes

A fresh reviewer found audio drifting ahead under dropped fixed-step time,
side-contact openings intersecting the van's support, and duck poses popping
to standing. Fixes: use real frame time for the live cinematic clock plus native
playback-position correction; rebound behind the snapshot van before opening;
blend the exact shared duck endpoint into the authored action. Regression tests
and rear/side/duck/air captures cover those corrections. Reviewer also requested
sound provenance, this review, preview commands and more precise test claims;
those are now supplied. No second independent review was requested.

## Remaining limits

- Only street mode has vans. Pedestrian maps keep their current substitution.
- Sound is deliberate synthesized cartoon foley; no human performance is implied.
- Native sound output is Windows-only. Animation remains usable without an audio
  device or on other platforms, but sound delivery there has not been implemented.
- The scene replaces the street road surface with a flat matching asphalt patch;
  it does not fracture arbitrary map geometry or create a physically simulated
  underground world. The hole is a staged nine-metre dark cavity.
- The source action is 12 fps with interpolation; the rendered delivery is 30 fps.
- The delivered video's motion, mix and comedy have user preview approval.
  Integration with the other checkout and any further interactive playtest remain
  separate from that approval.

Reproduction commands are in `RunnerGame/README.md`. No merge, commit or push
was performed; the worktree is retained for continued visual iteration.
