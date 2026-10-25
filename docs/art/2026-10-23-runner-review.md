# First playable runner independent review — 2026-10-23

Scope: gameplay, runtime entry point, runtime manifest/loading/rendering code and project-owned shader. Read the implementation plan and agreed gameplay section. No GUI launched, no code changed. Parent owns live capture verification.

## Must fix before calling the agreed gameplay complete

1. **P1 — A permanently empty lane bypasses the entire game.** `RunSimulation.Restart` chooses `safeLane` once; `FillTrack` never changes it. Move to the lane containing the coins, then leave all controls alone: the existing `generated safe route survives through speed cap and recycles` test proves an uninterrupted 400-second, >7 km run at 30 m/s. No jump, duck, or subsequent lane decision is needed. This diverges materially from the agreed hand-written row templates and changing sequences; the report acknowledges a scope reduction that the gameplay contract does not authorize. Use a small deterministic set of rows and change the guaranteed route with sufficient reaction distance. Test several seeds for changing safe lanes, an actual survivable sequence, and a bound on required lane movement rather than requiring one globally safe lane.

2. **P2 — Focus loss can still advance gameplay and apply queued input before pausing.** `RunnerGameWindow.FixedUpdate` consumes input and steps without checking `IsFocused`; the focus guard exists only in `Update`. `Engine.Application.OnUpdateFrame` runs up to five 20 ms fixed steps before Update. Reproduce by losing focus while approaching a hazard during pursuit; a pending frame can advance another 3 m at speed cap and catch the player before the pause guard runs. Guard focus before consuming input/stepping (or handle the focus event immediately), clear pending input, and verify that distance, timer, position and phase freeze on the first unfocused fixed tick. Normal queued input otherwise correctly survives Update/FixedUpdate ordering and is consumed once.

3. **P2 — Earned score is never displayed.** `RunSimulation.Score` correctly adds whole metres and 10 points per coin, but `UpdateTitle` includes only metres, coin count and speed. After collecting a coin, the agreed distance-plus-coin score remains invisible, including on caught. Add the computed score to the title while retaining useful telemetry.

## Could fix / explicitly track

- Coin arcs, bobbing, and distance-weighted harder templates are absent; every pickup is in a flat three-coin safe-lane line. The first two are modest visual/gameplay additions; varied safe paths above matter more to the core loop.
- No hit flash; the speed reduction/officer provide some feedback. Not a first-playable blocker on its own.
- `ModelManifest.Resolve` always compares with `OrdinalIgnoreCase`. This is appropriate for this Windows installation, but on a case-sensitive platform `/assets/Models` plus `../models/foreign.obj` can pass containment when the sibling exists. Select comparison according to platform if claiming cross-platform path containment. Lexical containment also deliberately does not resolve symlinks; installed trusted assets do not make that an immediate blocker.
- The console harness links gameplay source only. It does not automatically exercise runtime manifest validation/pivots, input/focus/title integration or resource lifetime; preserve the manual evidence below or add a context-free asset validation harness. Existing frame-grouping test only compares identical 20 ms tick streams, as the report accurately states.

## Checks performed and positive findings

- Ran `dotnet run --project RunnerGame.Tests --no-restore`: all 16 checks passed. These cover cap-speed contact, lateral switching, jump/duck, pursuit, once-only coins, pause/restart, bounded objects and reproducible fixed ticks.
- Collision uses real lateral position, 2 ms subdivisions and swept Z entry/exit. Vertical bounds conservatively include endpoints; the discrepancy is at most a slice. No concrete high-speed missed contact found. Blocking car/van remain taller than the 1.4 m jump.
- Read all 19 installed part manifests and checked all 41 referenced OBJ/PNG pairs: every path exists and remains inside its actual manifest directory. Runtime single cone/bin/officer paths are consistent with registry references. Rooted/traversal references are rejected lexically on Windows.
- Parsed OBJ vertices with converted manifest pivots `(x,z,-y)`. Rider standing/duck maxima are 1.6747/1.3168 m, matching collider constants; scooter Y minimum is 0. Wheel pivots and local rotation order are consistent. Only one rider pose is drawn, although both necessary poses are resident.
- Representative installed mesh world bounds: barrier X ±1.2, Y 0..1.695, Z ±.37; car X ±1.0584, Y 0..1.4857, Z -2.1187..2.1403; van X ±1.2186, Y 0..2.5056, Z -2.83..2.8748. Gameplay bounds are intentionally forgiving and independent of mesh detail. Barrier lintel collider is taller than the mesh to enforce duck/switch, and does not model its side posts; no wholesale mesh-bound replacement recommended.
- Street chunks tile in 20 m increments without gaps; facade/prop work and world objects are bounded. Registry shares meshes/textures and renderer shares one shader source; shutdown disposes cached resources once while context is live, including constructor failure cleanup. Officer residency is limited to four sampled frames. Rendering correctness/performance still requires parent's live captures; no unmeasured frame-rate claim made.
- Ready/start, explicit pause/resume, restart/reseed and caught state are internally coherent. Pausing freezes simulation. Title controls are clear. Gamma decoding/encoding matches linear RGBA8 texture storage; fog and clear colors agree.

Review outcome: changes needed for the three numbered findings. No broader dirty-asset audit was performed.

## Bounded re-review clearance — 2026-10-23

**PASS for the first-playable scope. All three previous must-fix findings are resolved; no new must-fix found in the changed integration.**

- The guaranteed route now moves through adjacent lanes with each 24 m row. Three-seed tests prove stationary camping fails in every lane, and a changing route survives 120 seconds at 30 m/s without hits while collecting trailing coins and keeping bounded/recycled objects. The simple ping-pong route leaves ample margin for .15 s adjacent moves even after the longest vehicle and coin line clear. It remains a deliberately simple first-playable route rather than the full distance-weighted template library.
- Program now delegates every fixed tick to `RunnerControls.Step(dt, IsFocused)`. That checks focus, pauses and clears pending input before any simulation call, closing the prior unfocused fixed-tick window. Update passes all documented keyboard mappings into the same pure controls class. Buffered edges survive frames with no physics and are consumed once. Ready/start, pause/resume, restart and focus behavior have direct tests.
- Title now displays `Score` as points and uses `EffectiveSpeed`, including the hit slowdown.
- Obstacles now set an internal `HitConsumed` flag rather than becoming inactive. They remain visible and keep scrolling until ordinary recycling, without hitting again when immunity expires. Distinct obstacles still cause the second hit. New regressions exercise both properties; coin collection continues to hide only the collected coin.

Fresh verification performed after the final obstacle-contact change:

- `dotnet run --project RunnerGame.Tests --no-restore`: **20/20 passed**.
- `dotnet run --project RunnerGame.InputTests --no-restore`: **8/8 passed**.
- `dotnet run --project RunnerGame.Rendering.Tests/RunnerGame.Rendering.Tests.csproj --no-restore`: **7/7 manifest contracts passed**.

Read the facade yaw, smaller tree placements, clock plaza and hit-contact rendering changes. Viewed `docs/art/previews/runner-caught.bmp`: one rider pose and scooter, visible pursuing officer, clock and readable street/obstacles are present; the facade fronts face the street. Parent owns the live window/capture execution and performance verification.

Residual nonblocking limits from the original review remain: flat coin lines without bob/arcs, simple route difficulty, no hit flash, no shadow mapping, and case-insensitive lexical manifest containment is Windows-specific. The latest title prioritizes score/speed/FPS and state over the former always-visible control reminder; the console and handoff should explain controls. No additional code edits were made by this reviewer.
