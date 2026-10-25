# Deterministic runner behaviour verification

Run `dotnet run --project RunnerGame.Tests --no-restore` after `dotnet restore RunnerGame.Tests/RunnerGame.Tests.csproj --ignore-failed-sources -p:NuGetAudit=false`.

This console harness links gameplay source directly, without OpenGL, runtime assets, or test packages. It returns a nonzero exit code on any failed check. Fixtures use reflection to clear generated traffic and set speed; no fixture-only production API was introduced.

## TDD evidence

Before implementing the simulation, the API-only stub produced 12 behavioural failures: start movement, lane interpolation, jump apex, duck/fastfall, swept cap-speed collision, physical lane switching, low-obstacle jump clearance, high-barrier clearance, coin scoring, hit immunity, recovery, and pause/resume. Restart and the initial coarse generation check passed vacuously against the stub; those checks were strengthened after implementation to require generated traffic and a surviving 400-second run through the speed cap. First implementation passed all 16 checks without compiler warnings. Later checks cover lateral crossing and deterministic grouping of identical fixed ticks. Those additional checks were added after implementation and are regression checks, rather than claimed red/green cycles.

## Collision and timing decisions

- Player collider half-width is .30 m and longitudinal half-length .80 m, including the scooter. Rider height includes hair: 1.674661 m standing and 1.316786 m ducking, each offset by current jump height.
- Cone: .23 m half-width/length, .55 m tall. Bin: .35 m half-width/length, 1.0 m tall. Pothole: .65 m half-width, .60 m half-length, low hazard volume up to .12 m. Barrier: .95 m half-width, .25 m half-length, underside at 1.43 m. Car: .90 m half-width, 2.2 m half-length, 1.6 m tall. Van: 1.0 m half-width, 2.7 m half-length, 2.6 m tall.
- Jump is a 1.4 m apex parabola with .7 s flight. Duck lasts .8 s and fast fall descends at 12 m/s. Lane transitions linearly interpolate the actual position over .15 s; a new direction starts from the current physical position.
- Longitudinal collision sweeps every object across the player's interval. Internal slices of at most .002 s bound lateral and vertical motion; lateral intervals use positions at longitudinal entry/exit. Vertical bounds conservatively include both slice endpoints (at most 2 ms early contact). There is no target-lane shortcut.
- World movement starts at 12 m/s and rises .06 m/s per second to 30 m/s. `Speed` reports cruise speed; `EffectiveSpeed` reports actual movement speed, including the .55 multiplier for one second after a hit. Distance therefore reflects actual slowed travel. `Score` is whole metres plus ten per coin.
- First impact gives one second immunity and a ten-second pursuit window. A later eligible impact within that window catches the player. Contacts during immunity are ignored. Pause and ready freeze all simulation state; caught freezes further ticks. Restart returns to ready and reproduces the original seed.

## Generation and limits

Rows are spaced 24 m apart, start 40 m ahead, and fill a 220 m horizon. Each row blocks two lanes and places a three-coin line in its safe lane. The safe lane changes by exactly one adjacent lane per row, reversing at the outer lanes; seeded initial lane/direction and obstacle choices keep restart deterministic. At the 30 m/s cap, rows arrive .8 s apart. A route follower can wait until the previous row's full 4 m coin line and longest 2.7 m van tail clear, then switch within .15 s before the next row. Old objects are removed beyond +15 m.

After independent review, tests were written to reject stationary camping and require a public effective movement speed. Before the revision they failed with `one lane remains permanently safe` and `effective speed missing`. After implementing adjacent route changes and `EffectiveSpeed`, all 18 checks pass without warnings. The route follower additionally runs 120 seconds at 30 m/s for each of three seeds, verifies zero impacts, collects every trailing coin, and maintains fewer than 100 listed objects. Separate camping checks prove all three stationary lanes eventually get caught for each seed. The route-follower regression passed before the change because the old static route was also reachable; the camping regression provides the red/green evidence for the changed generation behaviour.

This first playable uses coin lines rather than arcs and a conservative ping-pong path rather than advanced random route templates. Street chunk rendering/recycling belongs to the renderer.
Fixed ticks are deterministic for the same seed and input sequence regardless of how render frames group those ticks. Arbitrary variable `Step` sizes are supported for collision safety but exact floating-point equivalence across different timestep sizes is not promised. Runtime should call `.02f` as agreed.

The harness verifies gameplay only. Full application build, model placement, visual collider alignment, focus/input ordering, rendering and live play are parent integration checks.


## Contact visibility regression

A final integration regression was written before changing obstacle consumption: a real car impact had to leave the object Active for rendering. It failed with 'hit obstacle hidden'. Obstacles now retain Active until recycling and carry an internal HitConsumed flag; coins still set Active=false on collection. A separate slow-speed long-van contact spans more than one second, proves immunity expiry cannot hit the same object twice, and proves a distinct subsequent cone still catches the player. Final harness: 20 passing checks, warning-free build. The visibility check supplied red/green evidence; the sustained-contact check also passed before the change because old Active=false already prevented repeat damage.

## Pedestrian environment profile

`RunSimulation(int seed = 2026, bool pedestrian = false)` preserves the classic default. The pedestrian profile converts generated cars/vans into planters and potholes into cones, after the original random draw; seeded positions, IDs, three provisional lanes, safe routes and coin lines remain identical. `Planter` is appended after `Coin`, preserving existing enum values and the original six-way obstacle draw.

Planter collision uses the existing source asset's .925 x .925 x 1.279 m dimensions: .4625 m half-width/length and 1.279 m top. Fixtures straddle lateral and longitudinal collision edges, check feet immediately below/above the top, and demonstrate clearance at the real jump apex. It is a jumpable obstacle, not an oversized vehicle substitute.

TDD command, both red and green: `dotnet run --project RunnerGame.Tests/RunnerGame.Tests.csproj`. Before production edits, all original 20 checks passed and the three new checks failed with `pedestrian constructor missing`, `planter kind missing`, and `pedestrian constructor missing`. After implementation, all 23 checks pass, exit code 0, without warnings. The profile checks cover seeds 1, 7 and 2026, deterministic restart, identical classic/profile route layout, exclusion of road hazards throughout generation, and 120 seconds per seed at 30 m/s with no impact and collection of trailing coins. Full renderer, route and input integration remain parent verification work.

Pedestrian strip clearance revision: public `LaneSpacing` is 1.5 m for pedestrian mode and remains 2.5 m for classic mode. Generated centres, coins and interpolated movement use that spacing, giving pedestrian centres at -1.5, 0 and +1.5 m and player footprint extending to +/-1.8 m. The three positions are provisional paths, not painted lanes. Profile comparison now checks identical logical lane indices rather than identical physical X positions.

TDD command for this revision: `dotnet run --project RunnerGame.Tests/RunnerGame.Tests.csproj --no-restore`. Red: the original 20 checks and planter collision check passed; profile layout, the new strip/movement check, and the narrow route follower failed against the old 2.5 m spacing. Green: all 24 checks pass, exit code 0, without warnings. The cap-speed follower uses public `LaneSpacing` and still verifies three seeds over 120 seconds each with zero impacts and trailing coins collected. `Move` stores a logical lane index; `Tick` applies spacing to its physical destination.
