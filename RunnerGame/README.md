# Hannover Rush Hour — first playable

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

These console harnesses require no external test framework; a failed check returns a nonzero exit code:

```powershell
dotnet run --project RunnerGame.Tests
dotnet run --project RunnerGame.InputTests
dotnet run --project RunnerGame.Rendering.Tests
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

First visual priorities for the original street mode are ground/contact shadows, hit feedback and reducing visible facade repetition. That mode has gamma-correct lighting and distance fog, with a flat sky. Daylight shadow maps are implemented in the Hannover map mode. Normal maps, audio and an on-screen HUD remain future work. Gameplay collider bounds intentionally simplify detailed meshes. No engine or approved art files were changed for this integration.

## Geographic Hannover map candidate

From the repository root:

```powershell
dotnet run --project RunnerGame -- --map RunnerGame/Art/assets/hannover_pedestrian_blockout/out --overview
```

**Enter** starts riding from Hauptbahnhof and switches to the chase camera. **Tab** switches between chase and overview; opening the overview pauses an active run. **Enter** resumes riding, **R** resets. The finite route ends at Steintor. The other runner controls remain unchanged. Run without `--map` to see the original street mode.

This is a grey geographic blockout, not finished facade art. It follows the upper south-east side of the promenade and turns through Kröpcke toward Steintor. Three steering positions are provisional and spaced 1.5 m apart; the pedestrian paving has no painted lanes. Cars, vans and asphalt damage are excluded from the pedestrian profile. The existing first-hit/second-hit pursuit mechanics remain; the proposed offence/introduction sequence is not implemented yet.

Professor-facing sources, licensing, method, AI assistance and accuracy limits: `docs/art/HANNOVER_MAP_SOURCES_AND_METHOD.md` and its self-contained printable HTML companion. Central and map-folder credits accompany the derivative. Imported city buildings are CC BY4.0 material, not manually authored project buildings.

Additional checks:

```powershell
dotnet run --project RunnerGame.RouteTests -- RunnerGame/Art/assets/hannover_pedestrian_blockout/out/route.json 714.276088
python RunnerGame/Art/assets/hannover_route/validate.py
python RunnerGame/Art/assets/hannover_pedestrian_blockout/verify.py
```

The last command reproduces and validates the candidate; it requires the archived sources and local Python geometry dependencies documented by the builders. Route tests require only .NET and also check all three movement paths for folds. The map remains a candidate under Art; it has not replaced the installed runtime asset collection.

### Public-realm revision v2

```powershell
dotnet run --project RunnerGame -- --map RunnerGame/Art/assets/hannover_public_realm/out --inspect 245
```

This opens near Kröpcke for architectural inspection. While ready/paused: **PageUp/PageDown** moves100m along the route; **right mouse drag** orbits; **mouse wheel** zooms. **Tab** shows the entire area. **Enter** returns to normal riding; **R** restarts. Capture a particular location with `--inspect metres --capture output.bmp`.

V2 contains full public-space paving, contextual ground, revised promenade openings and a718.405m route. Forty-one trees and two first-pass architectural facades are included. Much of the city is still grey massing. It has project-owned daylight shadows; the original street rendering defaults remain unchanged. The revised lower floors/walls and route are checked independently. Attribution and unverified details are recorded in the professor-facing note, not presented as a finished realistic city.
