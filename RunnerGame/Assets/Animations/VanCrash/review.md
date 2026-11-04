# Officer-ticket revision review — 2026-11-04

The user requested this gag after approving the original van fall. The new
eleven-second cut is implemented and technically checked. Following feedback,
the rider/scooter fall is synchronized and the late stone removed; the user
accepted the correction with "okay looks good". The [original review](review-original.md) is historical.
Work is in `feature/photo-to-model` alongside the preserved cone-intro work.
After the playtest the user requested cleanup and push. Source and runtime files
are included in the feature-branch delivery; local review media remain ignored.

## Current renderer evidence

Street mode, 1280×800, actual game renderer:

- `docs/art/previews/van-ticket-sync.mp4`: full eleven-second video, 30 fps, with the
  authored mix. It is encoded renderer evidence, not audio-device loopback.
- `docs/art/previews/van-ticket-sync-contact-sheet.png`: current acting overview.
- `docs/art/previews/van-ticket-sync-frames/frame-0000.bmp` to `frame-0330.bmp`: all
  331 current frames, including approach, braking, peering, grip and release.
- `docs/art/previews/van-ticket-side.bmp`: side collision, held ticket at 7.4 s.

Inspected rear-contact frames at 5.8 s (planted look-down), 7.3 s (held ticket),
8.2 s (released paper), the contact sheet and the side grip frame. The ticket is
visibly connected to the right hand and readable as a ticket; it continues into
the opening after release. The officer stays on intact road. The closer camera
retains the hole and van during the handoff. No obvious mesh tears were found in
these views. Keyframes alone do not establish normal-speed acting or sound quality;
the video/interactive preview is supplied for that user review.

### Synchronized-fall correction

The screenshot defect came from separate fall starts (3.3 s and 3.57 s), separate
rotations, and continued leg kicking during the drop. Both actors now consume
one shared translation/rotation/visibility sample. The rider eases back into the
existing riding contacts over 3.0–3.3 s, preserving foot/deck and hand/bar contact
through the shared fall. A regression test failed at 3.4 s with the old delay
restored, then passed with the shared transform. The reviewer found no material
issues in the transition or renderer consumption.

The requested small box was the late stone primitive, not the hole. Only that
post-fall draw and its 5.70 s tick were removed; the opening, flaps, walls, early
collapse debris and officer/ticket timing remain. Current renderer frames 111
(3.7 s) and 159 (5.3 s) show the rider still on the scooter during descent and no
late cube in the aftermath. The full 331-frame corrected cut and MP4 were saved.
Animation and native audio regressions pass; the mix remains eleven seconds with
zero clipped samples. User visual acceptance was recorded after this correction.

Reproduce after building:

```powershell
.\RunnerGame\bin\Debug\net10.0\RunnerGame.exe --van-crash-preview
.\RunnerGame\bin\Debug\net10.0\RunnerGame.exe --van-crash-preview --capture docs/art/previews/van-ticket-grip.bmp --crash-time 7.3 --mute
.\RunnerGame\bin\Debug\net10.0\RunnerGame.exe --van-crash-preview --crash-contact Side --capture docs/art/previews/van-ticket-side.bmp --crash-time 7.4 --mute
.\RunnerGame\bin\Debug\net10.0\RunnerGame.exe --van-crash-preview --crash-film docs/art/previews/van-ticket-sync-frames --mute
ffmpeg -y -framerate 30 -i docs/art/previews/van-ticket-sync-frames/frame-%04d.bmp -i RunnerGame/Assets/Animations/VanCrash/crash.wav -c:v libx264 -crf 19 -pix_fmt yuv420p -c:a aac -shortest docs/art/previews/van-ticket-sync.mp4
```

## Technical and source verification

The extended-duration test failed against the old six-second clock, then passed
with the eleven-second scene and matching WAV/capture duration. Pause/reset
coverage now includes the late paper-flutter beat. Native Windows waveOut checks
cover late seeking/pausing plus reset, completion and mute.

The initial rig export found a 7 mm ankle-chain gap. Lowering the planted pelvis
to keep targets reachable corrected the final evaluated chain; wrist/ankle gaps
are now below 0.001 mm. A new all-133-frame check then caught sole penetration at
frame 31. A measured clearance finish, up to 7.713 mm, now updates the runtime
vertices, baked source pelvis and evaluated hand track together. Minimum vertex
height is zero, and the all-frame floor check passes.

See [ticket-validation.json](ticket-validation.json) and matching Art provenance
for hashes and measurements. New source is `Art/assets/van_crash/officer_ticket.blend`;
runtime action/grip are `officer-ticket.vclip` and `officer-ticket-hand.json`.
Shared character atlases, rider clip, scooter and van bytes remain unchanged.
Paper artwork and added foley are original project work. The eleven-second PCM
mix measures -1.724 dBFS peak, zero clipped samples; sources and cue times are in
[audio-sources.md](audio-sources.md).

Verification includes all seven harnesses: gameplay, input, animation, native
audio, route, rendering contracts and map metadata/shadows, plus a runtime build.

## Acceptance assessment

| Requirement | Result / evidence |
|---|---|
| Original fall retained | Current renderer frames and existing collision checks |
| Eleven-second terminal flow | Simulation/input checks, frame count, WAV duration |
| Run, brake, supported stop, look down | Rig action, all-frame clearance, renderer review and user preview acceptance |
| Connected grip and release | Evaluated hand track, actual release/opening checks, rear/side captures |
| Flutter enters hole | Release continuity and trajectory checks, released-paper frames |
| Readable camera | Rear and side views reviewed; extreme lanes checked numerically, not separately captured |
| Sound and controls | Cue report, zero clipping, native transport and late pause/reset checks; preview accepted |
| Source/provenance | Editable blend, clip/grip track, source notes and hashes |

A fresh reviewer found no material semantic bugs. Targeted measurements put
planted soles behind the near edge and the transformed release grip inside the
opening. Disposal and duration-derived audio/capture timing were also inspected.

The officer action uses 12 fps keys with interpolation. The hole remains a staged
cavity; no general destruction or physics system is added. Interactive sound
remains Windows-native. The selected one-hit policy for other hazards and their
shared officer ending are subsequent work: this delivery is the van-ticket part.
