# Cone hat road revision review

Revision: road-cinematic-v3.3, 2026-11-03. This pass follows the user's note
that the direction is improving but footsteps, scooter mount audio, cone
translucency, officer calls and walk/run screen time needed work.

## Generated and checked locally

- The controller and scene are 30 seconds with 11 timed beats. The rider clip
  contains 721 samples at 24 fps; the officer clip contains 76 continuous
  sampled poses for reaction, walk and run.
- Blender export reports 4.0 mm maximum rider grip-target error and less than
  0.3 mm wrist/ankle chain gaps. These are rig measurements, not visual approval.
- The scene holds a 3-second two-character walk and a 4-second run. The run
  opens on a closer officer shot, then returns to a wide two-shot before mount.
- Recorded CC0 concrete walking/running and kickstand sounds are used for the
  movement and mount beats. `audio-sources.md` records creators, links and edits.
- The cone now uses the opaque material default, so the road and face cannot
  show through its surface. Its mesh opening is now limited to the base, so the
  lower cone wall is solid. Other materials retain their existing settings.
- Officer speech escalates from the first “Hey!” to progressively firmer
  “Stehen bleiben!” calls, then uses a human-recorded German chase shout.
- `dotnet build CgiMin.sln --no-restore -p:NuGetAudit=false` completed with zero
  warnings and errors after the runtime changes.
- The captured recording has 744 frames at 24 fps: 30 seconds of intro plus one
  second of gameplay, with a matching 31-second offline WAV and cue log.

## Preview

The refreshed video is [`cone-hat-road-v3.3.mp4`](../../../../docs/art/previews/cone-hat-road-v3.3.mp4).
Its contact sheet is in the same preview folder. Review cone opacity and the
officer's escalating calls and chase shout at normal playback speed.

This is ready for the user's next visual and listening review. The contact sheet
cannot establish smooth gait at normal playback speed. The processed synthetic
calls may still need a human performance pass after listening review. No visual
or audio acceptance criteria are marked approved solely from export,
build or numeric checks. This records the local review; see Git history for delivery.
