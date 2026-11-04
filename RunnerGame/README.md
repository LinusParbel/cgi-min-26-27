# Hannover Rush Hour — first playable

The chosen opening is specified in
[Animations/ConeHat/animation.md](Assets/Animations/ConeHat/animation.md); other ideas
live in [Art/ANIMATION_IDEAS.md](Art/ANIMATION_IDEAS.md). This is planned work;
the current game still starts with the controls described below.

Run from the repository root:

```powershell
dotnet run --project RunnerGame
```

Click the game window and press **Enter** or **Space** to start. The initial view waits for input.

| Key | Action |
|---|---|
| A / D or left / right | Change lane |
| Space / W / up | Jump |
| S / down | Duck; fast fall while airborne |
| Esc | Pause / resume |
| Enter while paused | Resume |
| R | Reset to the ready state |
| Window close button / Alt+F4 | Close |

Collect tokens for ten points each. Jump or change lanes around low hazards; duck or change lanes around the overhead barrier; change lanes around cars and vans. The first hit slows the world and brings the officer behind you. A second hit within ten seconds ends the run; ten clean seconds clear pursuit. Losing focus pauses automatically, with explicit resume required. Window title shows state, points, distance, coins, effective speed and FPS.

## Verification

The street-mode [van crash](Assets/Animations/VanCrash/animation.md) is implemented:
any van contact ends the run with a six-second collapsing-road gag. Other hazards
keep the existing stumble/pursuit rules. The rider hangs above the hole, looks
down, kicks, then drops before the scooter; a distant thump and final stone tick
finish the scene. `R` returns to Ready; Esc/focus loss pause motion and sound.

From the van-crash worktree root:

```powershell
dotnet run --project RunnerGame -- --van-crash-preview
```

Add `--mute` for silent playback. Normal runs trigger the same scene through real
swept van contacts. Pedestrian maps continue to substitute planters for vans.
The preview starts the run approaching one van; after R, normal seeded gameplay
is restored. Re-run the command for the same immediate preview.

Repeatable renderer evidence (after building):

```powershell
.\RunnerGame\bin\Debug\net10.0\RunnerGame.exe --van-crash-preview --capture docs/art/previews/van-crash-hang.bmp --crash-time 2.8 --mute
.\RunnerGame\bin\Debug\net10.0\RunnerGame.exe --van-crash-preview --crash-contact Side --capture docs/art/previews/van-crash-side.bmp --crash-time 2.8 --mute
.\RunnerGame\bin\Debug\net10.0\RunnerGame.exe --van-crash-preview --crash-contact Duck --capture docs/art/previews/van-crash-duck.bmp --mute
.\RunnerGame\bin\Debug\net10.0\RunnerGame.exe --van-crash-preview --crash-contact Air --capture docs/art/previews/van-crash-air.bmp --mute
.\RunnerGame\bin\Debug\net10.0\RunnerGame.exe --van-crash-preview --crash-film docs/art/previews/van-crash-frames --mute
ffmpeg -y -framerate 30 -i docs/art/previews/van-crash-frames/frame-%04d.bmp -i RunnerGame/Assets/Animations/VanCrash/crash.wav -c:v libx264 -crf 19 -pix_fmt yuv420p -c:a aac -shortest docs/art/previews/van-crash.mp4
```

`--crash-time` selects 0–6 scene seconds after a real collision. Contact variants
use actual movement/jump/duck and the normal collision path. Film export writes
181 renderer BMP frames at 30 fps and stays silent; the encoding command muxes
the authored sound at the same scene origin. It does not record device loopback.
[Review notes](Assets/Animations/VanCrash/review.md) separate transport tests,
renderer checks and subjective acceptance.

These console harnesses require no external test framework; a failed check returns a nonzero exit code:

```powershell
dotnet run --project RunnerGame.Tests
dotnet run --project RunnerGame.InputTests
dotnet run --project RunnerGame.Rendering.Tests
dotnet run --project RunnerGame.AnimationTests
dotnet run --project RunnerGame.RouteTests
dotnet run --project RunnerGame.MapRenderTests
dotnet run --project RunnerGame.AudioTests
dotnet build CgiMin.sln
```

Actual GPU captures (BMP, using the same game renderer):

```powershell
.\RunnerGame\bin\Debug\net10.0\RunnerGame.exe --capture docs/art/previews/runner-first-look.bmp
.\RunnerGame\bin\Debug\net10.0\RunnerGame.exe --capture docs/art/previews/runner-duck.bmp --duck
.\RunnerGame\bin\Debug\net10.0\RunnerGame.exe --capture docs/art/previews/runner-caught.bmp --advance 12
```

Capture advance uses the real simulation and input controller with fixed .02-second ticks. It does not control a live interactive window. Captures demonstrate rendering; automated harnesses check behaviour. User playtesting supplies the final pacing/readability judgment.

## Current implementation and next tuning

Gameplay is independent of OpenGL. The first traffic generator changes the safe route between adjacent lanes in rows 24 m apart, with deterministic restart and a speed cap of 30 m/s. This deliberately conservative pattern set should be tuned after playtesting; it is not a complete difficulty system. Coins currently form straight lines and spin; arcs/bobbing and richer patterns remain future work.

The renderer reuses installed meshes and textures, draws one rider pose at a time, and samples four officer animation poses to limit startup memory. A representative first view uses 37 cached meshes, 16 textures and about 212 draws. This is a workload count, not a benchmark of sustained frame rate. The title exposes FPS for the user's machine.

First visual priorities for the original street mode are ground/contact shadows and reducing visible facade repetition. That mode has gamma-correct lighting and distance fog, with a flat sky. Daylight shadow maps are implemented in the Hannover map mode. Normal maps, general gameplay audio and an on-screen HUD remain future work. Van-crash audio is implemented on Windows. Gameplay collider bounds intentionally simplify detailed meshes. The crash adds a fixed-topology vertex upload method to the engine Mesh; existing shared art bytes remain unchanged.

## Geographic Hannover map candidate

From the repository root:

```powershell
dotnet run --project RunnerGame -- --map RunnerGame/Assets/Maps/HannoverPedestrianBlockout --overview
```

**Enter** starts riding from Hauptbahnhof and switches to the chase camera. **Tab** switches between chase and overview; opening the overview pauses an active run. **Enter** resumes riding, **R** resets. The finite route ends at Steintor. The other runner controls remain unchanged. Run without `--map` to see the original street mode.

This is a grey geographic blockout, not finished facade art. It follows the upper south-east side of the promenade and turns through Kröpcke toward Steintor. Three steering positions are provisional and spaced 1.5 m apart; the pedestrian paving has no painted lanes. Cars, vans and asphalt damage are excluded from the pedestrian profile. The existing first-hit/second-hit pursuit mechanics remain; the proposed offence/introduction sequence is not implemented yet.

Professor-facing sources, licensing, method, AI assistance and accuracy limits: `docs/art/HANNOVER_MAP_SOURCES_AND_METHOD.md` and its self-contained printable HTML companion. Central and map-folder credits accompany the derivative. Imported city buildings are CC BY4.0 material, not manually authored project buildings.

Additional checks:

```powershell
dotnet run --project RunnerGame.RouteTests -- RunnerGame/Assets/Maps/HannoverPedestrianBlockout/route.json 714.276088
```

Route tests require only .NET and also check all three movement paths for folds. Python model generation and review scripts are local, ignored tooling and are not required to run the game. Runtime map packages live under `Assets/Maps/`; generation sources remain under `Art/assets/`. See `Assets/Models/README.md` for the asset folder convention.

### Public-realm revision v2

```powershell
dotnet run --project RunnerGame -- --map RunnerGame/Assets/Maps/HannoverPublicRealm --inspect 245
```

This opens near Kröpcke for architectural inspection. While ready/paused: **PageUp/PageDown** moves100m along the route; **right mouse drag** orbits; **mouse wheel** zooms. **Tab** shows the entire area. **Enter** returns to normal riding; **R** restarts. Capture a particular location with `--inspect metres --capture output.bmp`.

V2 contains full public-space paving, contextual ground, revised promenade openings and a718.405m route. Forty-one trees and two first-pass architectural facades are included. Much of the city is still grey massing. It has project-owned daylight shadows; the original street rendering defaults remain unchanged. The revised lower floors/walls and route are checked independently. Attribution and unverified details are recorded in the professor-facing note, not presented as a finished realistic city.
