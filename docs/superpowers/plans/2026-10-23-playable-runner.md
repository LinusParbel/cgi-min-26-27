# Playable runner implementation plan

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans after the user confirms the move from modelling to gameplay.

**Goal:** Replace the rotating-cube entry point with a playable first street using the approved installed models.

**Architecture:** Keep deterministic gameplay independent from OpenGL; a renderer loads each installed mesh/texture once and draws recycled street sections and gameplay objects. Player stays near origin while the world scrolls toward +Z. Preserve the engine and art tools.

**Tech stack:** Existing .NET 10 / C# / OpenTK 4.9.4 course engine, OBJ and opaque PNG assets. No new runtime dependencies.

**Spec:** `docs/superpowers/specs/2026-10-16-hannover-rush-hour-design.md`, gameplay section. This plan covers the first playable integration. Shadow mapping, normal mapping and additional zones remain later rendering work.

**Status:** User approved implementation: "lets start and see how it would look and build it and see what we optimize". Gameplay and rendering implementation underway.

## Global constraints

- No commits, merges or pushes without user instruction. Preserve unrelated dirty work.
- Do not modify exported models, shared art libraries or viewers.
- Use metres, engine Y up, travel toward -Z, three 2.5 m lanes.
- Simulation uses FixedUpdate. Input edges must survive the Update/FixedUpdate ordering in Engine.Application.
- Collision shapes are gameplay bounds, independent of detailed render meshes. Use swept longitudinal checks to avoid tunnelling at the 30 m/s speed cap.
- Render only one rider pose at a time; convert manifest pivots from Blender `(x,y,z)` to engine `(x,z,-y)`.
- Keep input, physics, rendering and resource lifetime separate. Losing focus pauses the run.

## Task 1: Deterministic gameplay and tests

Create `RunnerGame/Gameplay/` and an independent test project/harness. Write failing behavioural tests before implementation.

- Player: lane targets -2.5/0/+2.5, roughly .15 s switch; jump 1.4 m apex/.7 s flight; duck .8 s and fast fall.
- Track: recycle 20 m chunks; deterministic seeded row templates with at least one passable lane and enough reaction distance between required moves.
- Obstacles: low jump/switch, high duck/switch, blocking switch. High collider corresponds to the approved 1.43 m barrier opening. Explicit player heights include rider hair.
- Pickups: lines/arcs, once-only collection, 10 points each.
- Pursuit: first hit slows/stumbles, one-second invulnerability, second hit within ten seconds ends run; recovery after ten clean seconds.
- Run state: speed starts 12 m/s, rises to 30 m/s; distance and coin score; pause freezes simulation; restart clears state and reseeds consistently.
- Tests cover lane limits/switches, jump/duck clearance, swept collisions, pickup once-only, hit immunity/recovery/gameover, row fairness, recycling, pause/restart and deterministic results across frame grouping.

## Task 2: Runtime model registry and rendering

Create `RunnerGame/Rendering/` and project-owned lit materials; leave engine unchanged.

- Read installed manifests/OBJ+PNG with path validation and shared mesh/texture caches. Dispose GPU resources once while context is live.
- Fixed chase camera behind scooter, clear far-plane/fog behaviour and consistent gamma lighting.
- Draw scrolling street/pavement, facade modules, restrained furniture/tree placements, clock backdrop, obstacles and spinning tokens.
- Mount ride/duck pose on scooter, turn wheels, show officer following after a hit. Avoid keeping unnecessary animation frames resident; retain original credits.
- Geometry/load tests verify all runtime references and pivot transforms. Screenshot mode offers deterministic visual verification without changing game rules.

## Task 3: Entry point, controls and live verification

Replace `RunnerGame/Program.cs` cube entry point; preserve original Example application.

- A/D or arrows switch; Space/W/up jump; S/down duck/fast fall; Esc pause; R restart. Window title shows distance, coins, speed, state and concise controls.
- Use a clear initial ready state so opening the window does not kill the player before they focus it.
- Build solution, run gameplay tests, run asset-loading checks and render representative riding/duck/gameover views.
- Independent review checks high-speed collision, input timing, fairness, pause/focus/restart, resource cleanup and model placement. Fix meaningful findings before handoff.
- Open the actual game window for the user, explain game controls (different from the free-camera viewer) and report remaining rendering limits accurately.

## Acceptance

The user can start, avoid low/high/blocking obstacles, collect tokens, see pursuit after a hit, lose on a second timely hit, pause and restart. Installed assets are visible and grounded. Automated behaviour checks and a warning-free build pass. Live rendering is verified; shadow-map work is not implied by this first integration.
