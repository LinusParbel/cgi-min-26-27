# Van ticket aftermath plan

Approved premise: officer runs up, stops at the hole, peers down, then drops a
ticket after the rider's fall. The scene-specific requirements and timed shots
are in `RunnerGame/Assets/Animations/VanCrash/animation.md`.

- [x] Extend simulation/audio/capture clocks to eleven seconds; first observe
  the new duration test fail, then retain pause/reset behavior through the aftermath.
- [x] Add distance-driven officer approach and hand/falling-ticket math, with
  endpoint, release-continuity and opening-clearance checks.
- [x] Author and numerically validate connected officer rig poses, planted stop,
  look-down and prop grip; save editable source and hand track.
- [x] Integrate officer/ticket rendering and aftermath framing in the real renderer.
- [x] Extend original foley with approach, scuff, handling and flutter; record sources.
- [x] Capture normal-speed video and keyframes; inspect hand, soles and release.
- [x] Run all seven harnesses, independently review the change, update scene review.

Runtime build: zero warnings/errors. All seven harnesses pass, including every
officer frame's floor clearance and late-beat audio/control pause. New source,
clip, grip-track and audio hashes verified. Current eleven-second MP4 and contact
sheet supplied. Follow-up feedback was resolved by sharing the rider/scooter
fall transform and riding contacts, and removing only the late stone cube/tick.
The user accepted the corrected cut with "okay looks good". Updated preview:
`docs/art/previews/van-ticket-sync.mp4`.

Scope is the van's ticket aftermath. The broader selected one-hit policy for
other hazards and their officer ending are subsequent work, not silently treated
as implemented here. Following preview approval and playtesting, the user requested
cleanup and push of the current feature work.
