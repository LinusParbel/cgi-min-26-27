# Van crash editable sources

`van_crash.blend` contains the existing civilian rider rig with the newly authored
crash action, frames 1–73 at 12 fps. The renderer interpolates exported vertices.
The action covers recoil, downward head reaction, spread arms and alternating
leg kicks. Scene-level camera, road hinges, hover, rebound and falling motion
live in `Rendering/VanCrashRenderer.cs`, separate from the local rig action.

The source was opened from the committed `cone_hat/cone_hat.blend` to preserve the
installed civilian atlas topology. No unfinished work from the other checkout
was copied. Original civilian identity, MakeHuman Community CC0 asset evidence
and source provenance remain in `../scooter_rider/` and `RunnerGame/CREDITS.md`.
Shared rider/van/scooter runtime models and textures remain in their model folders.

Scene exports: `Assets/Animations/VanCrash/rider.vcr`, `duck-start.vcr`, `void.png`
and `crash.wav`. The duck endpoint is exported from the installed shared duck OBJ
without altering it. `provenance.json` and the runtime validation JSON record hashes.
The solid dark PNG and sound are original generated project assets, CC0-1.0.

Ignored local tools: `build.py` (Blender 5.2), `audio.py` (Python 3). They are not
runtime dependencies. The blend contains the baked editable rig action; runtime
exports and source/license records are delivered with this change.

Requirements: [animation.md](../../../Assets/Animations/VanCrash/animation.md).
Evidence and limitations: [review.md](../../../Assets/Animations/VanCrash/review.md).

## Officer ticket revision — 2026-11-04

`officer_ticket.blend` adds a separate baked action from the existing officer rig,
frames 1–133 at 12 fps: run, brake, planted lean, pocket reach, ticket grip and
release. It uses the installed shared `CHR_Ordnungsamt.png` atlas without copying
or repainting it. Original officer attribution and source licences remain in
`../ordnungsamt_pursuer_v2/` and `RunnerGame/CREDITS.md`.

Exports are `officer-ticket.vclip` and `officer-ticket-hand.json`. The latter
records the evaluated right-hand grip in the same local coordinates as the clip,
so the ticket stays attached before release. `ticket-validation.json` and
`ticket-provenance.json` record dimensions, measured joint gaps and hashes.
The new fictional `ticket.png` is original code-drawn project art, CC0-1.0.

Local ignored `build_ticket.py` loads only the character/tool definitions from
the existing local cone authoring script; it does not execute or regenerate that
scene. Its `repair_ticket_floor.py` finishing pass keeps measured sole clearance
aligned in the runtime clip, baked source and grip track. `make_ticket.py` draws
the paper design; `audio.py` generates the full new
eleven-second mix. Editable Blender scenes and runtime exports remain usable
without any local Python tooling. Both editable van-scene blend files have
explicit exceptions in the Art ignore rules; generation/review Python remains local.
