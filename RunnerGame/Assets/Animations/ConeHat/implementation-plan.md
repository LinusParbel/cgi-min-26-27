# Cone hat road cinematic implementation plan

> Native execution, as selected by the user. Use the executing-plans workflow.
> This revision supersedes the original 12-second / three-environment plan.

**Goal:** Replace the rejected cut with the road-only cinematic specified in
[animation.md](animation.md), retaining its controls and clean gameplay handoff.

**Architecture:** Author both character rigs with real deforming walk/run cycles,
distance-driven phases, anatomical wrists and reachable prop targets. Stream
VCL2 pose blocks into one dynamic mesh per character. Scene tracks own staging,
camera, prop motion and cues. Maps do not instantiate the road opening.

**Stack:** .NET 10 / OpenTK, existing OpenGL shadow pass, Blender 5.2, local
ignored Python authoring; OpenAL runtime and PCM sound.

## Constraints and interfaces

- Working cut: 30 s, 11 shots; scene/controller/capture duration must agree.
- Officer remains outside early framing and >=12 m away at reveal/handoff.
- Preserve existing gameplay collision rules. No intro hazard/score progression.
- `ConeIntroController` owns Ready/Playing/Paused/Complete, fresh-press skip,
  cue crossing and exactly-once transition.
- `ConeIntroScene.Sample(time)` supplies actor/prop transforms, camera, rider yaw
  and officer frame/blend values.
- `VertexClip` supports VCL1 and VCL2 (exact pose-block aliases), finite validated
  data, bounded two-frame cache and linear pose interpolation.
- `ConeIntroRenderer` updates both character meshes and references shared textures.
- `OpeningSequence` coordinates the controller, audio and real RunSimulation.
- Runtime files stay here; editable source/provenance under `Art/assets/cone_hat/`.
  Local Python is ignored. Keep each compressed clip below GitHub's file limit.

## Review focus

Held start/resume cannot skip; paused/focus-lost time and cues remain frozen.
Officer must never translate while using a static pose.
Reachable knuckle targets do not substitute for checking visible hand contact.
Head attachment must follow the evaluated cranium rather than an arbitrary bone offset.
Sole clearance must be checked on evaluated boots, not just ankle targets.
Camera cuts must be intentional, and the final acceleration must match gameplay.

## Tasks

### 1. Diagnose and pin the rejected behaviour

- [x] Confirm static officer translation and four-frame run stepping.
- [x] Confirm the fixed wrist aim and short, obvious officer staging.
- [x] Retain existing work; focus new cinematic work on the road.
- [x] Add regression checks for frame aliases, longer timing and officer separation.

### 2. Re-author the scene and character motion

- [x] Stage approach / cone / late officer reveal / call / awkward hold.
- [x] Add nervous walking before the sprint and a longer mount/takeoff.
- [x] Derive gait phase from distance, solve legs and wrists without broken chains.
- [x] Export full interpolated rider motion and officer walk/run/reaction poses.
- [x] Correct evaluated boot-floor clearance and head/face contact regressions.
- [x] Save a complete editable keyframed source and current provenance.

### 3. Runtime playback and road-only scope

- [x] Implement VCL2 aliases with bounds and overlap validation.
- [x] Extend controller, shot IDs, parser and recordings to 30 s.
- [x] Render both actors with interpolated deformation.
- [x] Exclude cinematic setup from map launches and preserve ordinary map controls.
- [x] Extend road scenery behind the stage and reuse the existing shadow pass.
- [x] Verify the cut and gameplay transition in the real renderer.

### 4. Sound and timing

- [x] Preserve pause/skip/reset cue ownership and continuous natural-handoff ambience.
- [x] Produce the officer's German call locally and convert to PCM16.
- [x] Update source records/hashes and review cue times against the 30-second cut.
- [x] Generate a fixed-step recording and offline sound mix for review.

### 5. Acceptance and delivery

- [x] Run animation/gameplay/input/rendering/map metadata/route harnesses and build.
- [x] Inspect the final road sequence, contact closeups, gait and handoff.
- [x] Keep review limitations explicit; never claim acting passes from unit tests.
- [x] Update spec, storyboard, review record and runnable preview instructions.
- [ ] Review the refreshed 30-second preview with the user before committing.
- [ ] Push only after the user explicitly approves it.

## Verification commands

Run from repository root:

```powershell
dotnet run --project RunnerGame.AnimationTests --no-restore
dotnet build CgiMin.sln --no-restore -p:NuGetAudit=false
dotnet run --project RunnerGame.Tests --no-restore
dotnet run --project RunnerGame.InputTests --no-restore
dotnet run --project RunnerGame.Rendering.Tests --no-restore
dotnet run --project RunnerGame.MapRenderTests --no-restore
dotnet run --project RunnerGame.RouteTests --no-restore -- RunnerGame/Assets/Maps/HannoverPedestrianBlockout/route.json 714.276088
dotnet run --project RunnerGame.RouteTests --no-restore -- RunnerGame/Assets/Maps/HannoverPublicRealm/route.json
.\RunnerGame\bin\Debug\net10.0\RunnerGame.exe --record-intro docs/art/previews/cone-hat-road-v3.3 --mute
```

The recording contains 30 s of intro plus 1 s of gameplay at 24 fps, with a
matching WAV mix and cue log. Encode those frames to a review video; raw media
remains ignored. User review of acting and voice remains distinct from code tests.
