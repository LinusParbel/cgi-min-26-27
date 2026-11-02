# Cone Hat Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans
> to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Deliver the approved 12-second cone intro, with real character motion,
sound, camera staging and a clean transition into the existing game.

**Architecture:** Author motion on the existing Blender rigs. Export a compact
fixed-topology vertex clip, sample it through one dynamic mesh, and leave the
existing gameplay meshes intact. A deterministic intro controller owns time,
input and named cues; both renderers place the same sequence in their environment.

**Tech stack:** .NET 10, existing OpenTK 4.9.4/OpenGL 3.3, OpenAL, Blender 5.2,
local ignored Python authoring/export scripts. No general skeletal engine rewrite.

**Spec:** [animation.md](animation.md), including AC01–AC14 and [storyboard.svg](storyboard.svg).

## Global constraints

- Duration 12 seconds, tolerance ±0.5 s; eye-contact silence at least 0.50 s.
- Input, skip, pause, focus and restart follow the approved playback contract.
- Intro does not advance distance, scoring, hazards or damage.
- Visual officer following is independent of the second-hit pursuit timer.
- Existing shared models/textures/clips stay in their current model folders.
- Scene exports and audio belong here; editable sources/provenance belong in
  `RunnerGame/Art/assets/cone_hat/`. Python stays ignored.
- Street mode and both shipped maps must pass. Impact/beep sync within 100 ms.
- Do not mark visual/audio acceptance from unit tests alone.

## Review focus

- Holding Start, or resuming with Enter, must not also skip; test in Task 1.
- Pause/focus loss at cue boundaries must not duplicate sounds; test in Tasks 1/4.
- Skip/restart during a compressed-frame load must not leak buffers; test in Task 3.
- Tab/inspection and capture paths must not bypass intro input rules; test in Task 5.
- Missing audio device must preserve playability and report the limitation; test
  in Task 4 and verify actual audible playback before accepting AC09.

## Ownership and interfaces

New runtime code uses `RunnerGame/Animation/` for controller, clips and scene data;
`RunnerGame/Audio/` for the small OpenAL playback adapter;
`RunnerGame/Rendering/ConeIntroRenderer.cs` for scene draws.
Tests use a console harness `RunnerGame.AnimationTests/`, matching existing tests.
These are application source folders, not runtime asset folders.

- `IntroInput(bool Focused, bool StartDown, bool PausePressed, bool RestartPressed)`.
- `IntroPhase`: Ready, Playing, Paused, Complete.
- `IntroTransition(bool Reset, bool Handoff, bool PauseChanged)`.
- `ConeIntroController.HandleInput(IntroInput)` and `Advance(float seconds)` return
  `IntroTransition`; expose `Phase`, `Time`, `ShotId`. Completion emits once.
- Construct controller with `IReadOnlyList<IntroCue>` from scene.json; validate
  finite times in [0,12], unique IDs and sorted order before playback.
- `IntroCue(string Id, float Time, string Sound)`; controller drains newly crossed
  events with `DrainCues()`. No skipped backlog is played.
- `ConeIntroSample`: rider/officer/scooter/cone transforms, camera position/target,
  cone visibility and wheel rotation in a shared local stage frame.
- `ConeIntroScene.Sample(float seconds)` returns `ConeIntroSample` from scene data.
- `VertexClip.Open(string path)`, `Sample(float seconds, Span<Vertex> destination)`,
  `Dispose()`; two decoded sample frames retained at most.
- `IntroAudio` consumes cue events and exposes `SetPaused`, `Reset`, `SetVolume`,
  `Dispose`; inject `IIntroAudio` in tests rather than requiring a sound device.

### Task 1: Deterministic intro playback and input

**Files:** Create `RunnerGame/Animation/ConeIntroController.cs`,
`IntroInput.cs`, `IntroCue.cs`; create `RunnerGame.AnimationTests/Program.cs`
and `RunnerGame.AnimationTests.csproj` referencing RunnerGame.

- [ ] Write failing tests: Ready remains idle; start plays; held start never skips;
  release/new press skips; 12 s completes once; invalid/nonfinite deltas reject.
- [ ] Add failing tests: pause/focus freeze time, Enter resumes without skip,
  focus return does not resume, R resets, each shot boundary has correct ShotId,
  crossing several cues emits each once, skip discards backlog.
- [ ] Run `dotnet run --project RunnerGame.AnimationTests`; confirm missing API failure.
- [ ] Implement the interfaces above. Clamp time at 12; reject negative/NaN time.
  Handle reset before other input, then focus, pause/resume, then start/skip.
- [ ] Run tests to PASS and commit controller/harness.

### Task 2: Rigged acting, staging data and export

**Files:** Local ignored `Art/assets/cone_hat/build.py`, `export.py`,
`cone_hat.blend`; tracked scene files here: `scene.json`, `rider.vclip`,
`officer_idle.obj`, `officer_react.obj`, `asset-validation.json`.

**Consumes:** S01–S08, current rider rig and installed texture atlas; controller times.
**Produces:** fixed-topology rider clip and named actor/prop/camera/cue tracks.

- [ ] Author all eight beats on the civilian rig using planted-foot IK and
  hand targets for cone/handlebar contacts. End exactly at the installed riding
  pose; retain shared atlas UVs through the existing evaluated-mesh mapping.
- [ ] Stage the cone broad opening around the head; select cone variant from
  measured fit. Animate release/rocking and a cleared riding corridor.
- [ ] Author officer idle/reaction on its rig, then join existing run-cycle motion.
  Fit shared officer atlas UVs; do not duplicate existing run frames or textures.
- [ ] Export rider at 24 samples/s (289 samples including both endpoints).
  Use `VCL1`: little-endian counts/fps, static UV/index data, indexed offsets to
  separately Deflate-compressed frames of float32 positions and normals.
  Store byte layout/version and coordinate conversion in `asset-validation.json`.
- [ ] Keep only adjacent decoded frames in runtime; do not create hundreds of OBJ
  files/GPU meshes. Measure disk size and decode cost before finalising export.
- [ ] Write and run local validators for fixed topology, atlas UV identity,
  finite coordinates/normals, hand/foot contact landmarks, frame counts and
  final-pose agreement. Record outputs and hashes in asset-validation.json.
- [ ] Produce Blender contact-sheet/preview evidence for S01–S08 and contact
  details. Correct visible clipping/sliding before accepting export; commit exports.

### Task 3: Bounded clip playback and drawing support

**Files:** Create `RunnerGame/Animation/VertexClip.cs`, `ConeIntroScene.cs`;
modify `Engine/OpenGL/Mesh.cs`; extend animation harness with clip fixtures.

**Consumes:** Task 2 format and scene.json. **Produces:** sampled mesh and scene state.

- [ ] Write failing tests for endpoints/interpolation, finite normalized normals,
  wrong magic, truncated/oversized counts, invalid indices, unsafe paths, invalid
  frame offsets and decompression size limits. Limit vertex count to 100,000,
  index count to 600,000 and decoded frames to their exact declared size.
- [ ] Test sampling after seek, repeated same time, skip/reset disposal and
  adjacent-frame cache bound. Run harness and confirm failures before implementation.
- [ ] Implement clip reader and static scene tracks. Sample independently of
  render rate; interpolate positions and normalize interpolated normals.
- [ ] Add `Mesh.UpdateVertices(Vertex[] vertices)` retaining topology and buffer
  size; use buffer subdata and reject changed vertex count/disposed access.
- [ ] Extend byte-preservation rule in `.gitattributes` to animation runtime
  files. Validate export/readback with real clip, run tests, build and commit.

### Task 4: Named audio cues and playback

**Files:** Create `RunnerGame/Audio/IIntroAudio.cs`, `IntroAudio.cs`,
`PcmWave.cs`; add `audio/*.wav`, `audio-sources.md` here and sound mapping in scene.json.

**Consumes:** Task 1 cue stream. **Produces:** pausable cue/ambience playback.

- [ ] Write failing tests with fake audio output for event ordering, one-shot
  deduplication, pause/resume, reset/skip cleanup, mute/volume and missing device.
  Test WAV size/encoding rejection and invalid paths in a pure parser.
- [ ] Produce original procedural sound effects for footsteps, plastic cone,
  throat-clear-like interruption, beep, takeoff and quiet city-like ambience.
  Record authorship, synthesis method and file hashes; no external recordings.
  German speech remains optional and is not a required dependency.
- [ ] Implement OpenAL playback with the already installed OpenTK binding;
  verify exact API signatures against local package documentation. Decode PCM
  WAV safely, dispose buffers/sources/context, and degrade cleanly without device.
- [ ] Add command options `--mute` and `--volume 0..1`; test validation.
  Check sound quality and timing in-engine, not just synthesized file existence.
- [ ] Run harness and real-device listen/capture, correct cues and commit.

### Task 5: Street and map integration, camera and gameplay handoff

**Files:** Create `RunnerGame/Rendering/ConeIntroRenderer.cs`; modify
`IRunnerScene.cs`, `SceneRenderer.cs`, `PedestrianMapRenderer.cs`, `Program.cs`;
create `RunnerGame/Animation/OpeningSequence.cs`; extend harness/integration tests.

**Consumes:** controller, sampled clip/tracks and audio adapter. **Produces:** playable intro.

- [ ] Test orchestrator with fake scene/audio and real RunSimulation: every
  shot-boundary skip equals natural completion, no score/distance/hazard/damage
  advancement, handoff once, no stale movement input, restart clears all state.
- [ ] Implement `OpeningSequence` as the owner of controller/audio. Keep
  RunSimulation Ready until completion; start once and clear queued inputs.
- [ ] Change scene render call to accept optional intro sample. Render environment
  but hide normal rider/scooter/hazards while intro actors own the shot. Include
  actors in map shadow draws and restore normal camera/material state afterwards.
- [ ] Anchor street stage at local route start; map stages use route start,
  tangent/right vectors and groundY. Verify real clearances, then save per-map
  stage offsets in scene.json. Correct anchors if geometry obstructs action.
- [ ] Show officer behind during subsequent play independent of pursuit timer,
  retaining capture mechanics. Confirm clean escape does not remove visual officer.
- [ ] Preserve Tab/overview/inspection outside intro; during playback Tab and
  inspection must not bypass pause/input ownership. Extend tests for these paths.
- [ ] Add deterministic capture options `--intro-time 0..12` with `--capture`,
  and `--record-intro <folder>` for fixed-step frames plus cue log/offline WAV mix.
  Preserve old `--advance` gameplay capture semantics and document option conflicts.
- [ ] Run animation, gameplay, input, rendering, map-metadata and route harnesses;
  capture S01–S08 and handoff in all three environments; correct defects and commit.

### Task 6: Acceptance review and delivery

**Files:** Update `animation.md`, `RunnerGame/README.md`, scene audio/provenance
records and a criterion review record beside this plan. Evidence media stays ignored.

- [ ] Run `dotnet build CgiMin.sln -p:NuGetAudit=false` and all existing harnesses;
  run both actual route inputs. Record exact commands/results.
- [ ] Record the entire sequence with audio in street and both maps. Inspect
  silent readability, foot plants, cone/hand/head contacts, mount and camera blend.
- [ ] Check required cue timings (impact/beep within 100 ms), absence of clipping,
  pause/focus behaviour, and clean skip/restart on a real window/audio device.
- [ ] Measure frame time and bounded clip memory; correct playback stalls rather
  than hiding them behind the capture path.
- [ ] Review AC01–AC14 individually; record pass/fail, evidence paths, reviewer/date
  and limitations. Leave failed or unevidenced criteria open.
- [ ] Request an independent whole-change review, address material findings,
  then commit/push and report what was actually verified.

## Plan self-review

All eight shots and AC01–AC14 map to the tasks above. State/cue tests do not
substitute for rig/contact/sound review. Audio device failure permits running
the game, but does not pass the audible delivery criterion. Shared file paths,
restart behaviour and capture compatibility are explicit integration checks.
