# Hannover Rush Hour — first playable

The chosen opening is specified in
[Animations/ConeHat/animation.md](Assets/Animations/ConeHat/animation.md); other ideas
live in [Art/ANIMATION_IDEAS.md](Art/ANIMATION_IDEAS.md). The road-only
cone-hat opening plays before road-mode gameplay. Hannover map mode does not
play it.

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

Collect tokens for ten points each. Jump or change lanes around low hazards; duck or change lanes around the overhead barrier; change lanes around cars and vans. A van contact immediately ends the run with the collapsing-road animation. A street-mode cone contact triggers the seventeen-second airborne ticket ending. For other hazards, the first hit slows the world and brings the officer behind you. A second hit within ten seconds ends the run; ten clean seconds clear pursuit. Losing focus pauses automatically, with explicit resume required. Window title shows state, points, distance, coins, effective speed and FPS.

## Road opening animation

The straight road features a stylized Hannover landmark district: Neues Rathaus
overlooks a broad forecourt on the left, with Kröpcke Uhr in a separate square
on the right. Benches, planters and trees furnish the openings in the shopfront
rows. The district repeats every 420 m during a run; the Rathaus uses 55% scale
to fit the street composition. These reuse the installed shared monument models.

The 30-second cone-hat opening plays once before a road-mode run. A fresh key
press after it starts skips; Esc pauses and Enter resumes. The scene uses the
existing rider and officer rigs, continuous walk/run clips, shared model
textures, contact shadows and sourced and authored sound. The specification,
acceptance criteria and review record are in `Assets/Animations/ConeHat/`.

Capture a deterministic muted review recording from the repository root:

```powershell
.\RunnerGame\bin\Debug\net10.0\RunnerGame.exe --record-intro docs/art/previews/cone-hat-road-v3.3 --mute
```

It writes 744 frames at 24 fps, an offline WAV mix and cue log. The preview
folder is ignored; it is generated for local review and is not a runtime asset.

## Van collision

The street-mode [van crash](Assets/Animations/VanCrash/animation.md) is implemented:
any van contact ends the run with an eleven-second collapsing-road and
officer-ticket gag. The rider looks down, regains the scooter grip, and falls
with it as one unit. The officer then brakes at the hole, peers down and drops
a ticket into it. The late stone cube and its tick have been removed.
Cones now have their own airborne ticket ending. The remaining hazards keep the
stumble/pursuit rules; their selected one-hit endings are subsequent work. `R` resets; Esc/focus loss pause motion and sound.

From the repository root:

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
.\RunnerGame\bin\Debug\net10.0\RunnerGame.exe --van-crash-preview --crash-film docs/art/previews/van-ticket-sync-frames --mute
ffmpeg -y -framerate 30 -i docs/art/previews/van-ticket-sync-frames/frame-%04d.bmp -i RunnerGame/Assets/Animations/VanCrash/crash.wav -c:v libx264 -crf 19 -pix_fmt yuv420p -c:a aac -shortest docs/art/previews/van-ticket-sync.mp4
```

`--crash-time` selects 0–11 scene seconds after a real collision. Contact variants
use actual movement/jump/duck and the normal collision path. Film export writes
331 renderer BMP frames at 30 fps and stays silent; the encoding command muxes
the authored sound at the same scene origin. It does not record device loopback.
[Review notes](Assets/Animations/VanCrash/review.md) separate transport tests,
renderer checks and subjective acceptance.

## Cone collision: Special delivery

The street-mode [cone ending](Assets/Animations/ConeCrash/animation.md) is implemented.
On the first accepted cone contact the front wheel catches its base, the scooter
flips and throws the rider skyward. The camera follows that launch, then moves
to the officer running up and jumping after the already rising rider. One passing
slap sticks a ticket to the upper back. The officer falls away while the camera
follows the rider's continuous flight to a twinkle. There is no mid-air hold or
street-return cut; the scene ends at seventeen seconds.
Jumping cleanly above a cone avoids the scene. Pedestrian maps keep two-hit cones.

```powershell
dotnet run --project RunnerGame -- --cone-crash-preview
```

Esc / focus loss pauses scene and audio; Enter / Esc resumes; R resets. The preview
uses real swept contacts and bypasses the opening. R returns to ordinary seeded
Ready gameplay; rerun the command to repeat the isolated collision.

After building, use the installed executable or the .NET 10 host:

```powershell
.\RunnerGame\bin\Debug\net10.0\RunnerGame.exe --cone-crash-preview --capture docs/art/previews/cone-ticket.bmp --crash-time 7.3 --mute
.\RunnerGame\bin\Debug\net10.0\RunnerGame.exe --cone-crash-preview --crash-contact Side --capture docs/art/previews/cone-ticket-side.bmp --crash-time 7.3 --mute
.\RunnerGame\bin\Debug\net10.0\RunnerGame.exe --cone-crash-preview --crash-film docs/art/previews/cone-film --mute
```

`--crash-contact` accepts Rear, Side, Duck and Air. Air is an early low jump that
still contacts the cone; a sufficiently high jump clears it. `--crash-time`
accepts 0-17 seconds for this scene. Film capture writes 511 frames at 30 fps,
including the terminal frame; mux with `Assets/Animations/ConeCrash/crash.wav`.
`--crash-distance metres` stages either crash preview at a later street district
without altering normal gameplay. The current local review video is `docs/art/previews/cone-crash-v12.mp4`; current
keyframes and limits are listed in [review.md](Assets/Animations/ConeCrash/review.md).

## Verification

These console harnesses require no external test framework; a failed check returns a nonzero exit code:

```powershell
dotnet run --project RunnerGame.Tests
dotnet run --project RunnerGame.InputTests
dotnet run --project RunnerGame.Rendering.Tests
dotnet run --project RunnerGame.AnimationTests
dotnet run --project RunnerGame.AudioTests
dotnet run --project RunnerGame.RouteTests
dotnet run --project RunnerGame.MapRenderTests
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

The renderer reuses installed meshes and textures. Intro playback streams
sampled rider and officer deformation through one dynamic mesh each; versioned
clips alias repeated poses to reduce storage. A representative gameplay view
uses 37 cached meshes, 16 textures and about 212 draws. This is a workload count,
not a benchmark of sustained frame rate. The title exposes FPS for the user's
machine.

First visual priorities for the original street mode remain hit feedback and
reducing visible facade repetition. That mode has gamma-correct lighting,
distance fog, a flat sky and contact shadows. Daylight shadow maps are
implemented in Hannover map mode. Gameplay collider bounds intentionally
simplify detailed meshes.

## Geographic Hannover map candidate

From the repository root:

```powershell
dotnet run --project RunnerGame -- --map RunnerGame/Assets/Maps/HannoverPedestrianBlockout --overview
```

**Enter** starts riding from Hauptbahnhof and switches to the chase camera. **Tab** switches between chase and overview; opening the overview pauses an active run. **Enter** resumes riding, **R** resets. The finite route ends at Steintor. The other runner controls remain unchanged. Run without `--map` to see the original street mode.

This is a grey geographic blockout, not finished facade art. It follows the upper south-east side of the promenade and turns through Kröpcke toward Steintor. Three steering positions are provisional and spaced 1.5 m apart; the pedestrian paving has no painted lanes. Cars, vans and asphalt damage are excluded from the pedestrian profile. The existing first-hit/second-hit pursuit mechanics remain in this map mode; the implemented cone opening and van ending currently belong to street mode.

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

### Aerial street environment

The procedural street now has closed building depth, roofs, parapets and roof
fixtures behind its existing shopfronts. A batched district adds complete nearby
blocks and paving outside the Rathaus and clock plazas. Broad ground and the
extended cinematic road prevent the street appearing as a floating strip.
Fog follows the active sky color, including the blue cone-flight sky, so distant
landmarks fade into the background instead of becoming gray silhouettes.
All geometry reuses the existing shared shopfront and street atlases. The accepted
actor motion and approved audio are retained. Geometry is code-authored in
Rendering/StreetCityGeometry.cs; source notes are in Art/assets/street_city/.
## Render visibility diagnostics

Camera and shadow culling are enabled by default in street and map modes.
Street district buildings use smaller spatial batches. The normal street
pursuer skips clip decoding and GPU updates when neither the camera nor its
visible shadow needs the actor; gameplay pursuit continues independently.
Authored cinematic actors still sample their animation, with current deformed
bounds used to filter draw submissions.

Use `--no-culling` for an otherwise identical comparison capture or playtest.
It disables colour, shadow and pursuer visibility rejection, without changing
the gameplay clock or geometry detail. Compare Release builds on the same
machine. See [specification and validation](../docs/superpowers/specs/2026-11-08-render-visibility.md).
