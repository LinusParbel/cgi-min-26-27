# Hannover Rush Hour — Design Spec

**Date:** 2026-10-16 · **Status:** design agreed in brainstorming; asset-pipeline spike pending
**Source ideas:** `RunnerGame/Hannover_Rush_Hour_Game_Design_and_3D_Asset_Plan.md`
**Research:** `reports/Blender asset pipeline for OBJ runner.md`

## Context and constraints

- University CGI course project; team of 2 (Blender beginners); ~4–6 weeks from 2026-10-16.
- Graded on graphics techniques, a playable game, and own 3D models. **Full AI use is allowed.**
- Built on the course engine (C#/OpenTK): OBJ + one PNG per mesh, Phong, one point light, no text/UI,
  audio, collision, shadows, transparency or skeletal animation. Engine edits stay small and additive.
- Look: **semi-realistic** (real textures per asset), not blocky low-poly.

## 1. Gameplay rules (v1.0)

- **World model (approach B):** the player stays at the origin and only moves in X (lanes) and Y
  (jump/duck); road chunks, obstacles and coins scroll towards +Z and are recycled behind the camera.
  Camera, sun and shadow volume are fixed.
- **Controls:** A/D or ←/→ lane; Space/W/↑ jump; S/↓ duck (in the air: fast fall); Esc pause; R restart.
- **Movement (initial values, tuned in play):** 3 lanes, 2.5 m wide at x = −2.5/0/+2.5; lane switch
  ≈0.15 s; jump ≈1.4 m apex, ≈0.7 s airtime (in `FixedUpdate`); duck 0.8 s at half collider height;
  speed 12 m/s rising to a cap of ≈30 m/s.
- **Obstacle classes:** *low* (cone, bin, pothole → jump or switch), *high* (barrier at head height →
  duck or switch), *blocking* (car, van, later tram → switch only).
- **Patterns:** hand-written row templates such as `[low, free, blocking]`, a few rows per 20 m chunk.
  A validator rejects rows without a passable lane and sequences that force a two-lane switch within
  too little reaction distance. Randomness only chooses the next template; harder templates are
  weighted up with distance.
- **Coins:** lines and arcs over jumpable obstacles; 10 points each; spin and bob.
- **Pursuer (2-hit rule):** any collision = hit → stumble (short slowdown, 1 s invulnerability, hit
  flash) and the officer appears right behind the player. No hit for 10 s → officer falls back out of
  view. Second hit within those 10 s → caught → run ends.
- **Score:** distance in metres + coin points, shown in the window title
  (`Hannover Rush Hour — 1234 m | 56 coins | 18 m/s`; on game over `CAUGHT! Press R to restart`).

## 2. Rendering

- **`RunnerLitMaterial`** (`RunnerGame/Materials/RunnerLit/`), used for almost everything: per-asset
  texture × tint, Phong from a directional late-afternoon sun, shadow-map lookup with 3×3 PCF,
  exponential distance fog blending into the horizon colour, gamma-correct lighting (texture → linear,
  light, → gamma).
- **Sky:** large gradient backdrop behind the track; fog colour = horizon colour. Far plane ≈150 m,
  fog fully dense by ≈120 m, chunks spawn at ≈140 m (no visible pop-in).
- **Shadow mapping (engine, additive, upstream-PR candidate):** `Engine/OpenGL/ShadowMap.cs`
  (framebuffer + 2048² depth texture); fixed orthographic light volume ≈±12 m in X and from the camera
  to ≈60 m ahead, shadows fade out beyond; renderer gains a depth-only `DrawShadowCaster(mesh, model)`
  with a built-in depth shader and fills `uLightSpace`/`uShadowMap` only when a shader declares them
  (same pattern as `uCameraPosition`); viewport restored after the shadow pass.
- **Frame order:** shadow pass (player, obstacles, coins, buildings) → clear → sky → world.
- **Fallback:** blob shadows (soft dark disc under player/obstacles, ≈0.5 day).
- **Add-on:** normal mapping (needs tangents) after shadow mapping, if time allows.

## 3. Asset pipeline

- **Sources per asset:** (1) download CC0/CC-BY realistic models (Poly Haven, Sketchfab CC-BY);
  (2) AI text/image-to-3D (e.g. Meshy/Tripo, Hyper3D/Hunyuan via Blender MCP) for missing items;
  (3) AI-assisted building in Blender (MCP / headless scripts) with Poly Haven CC0 textures for
  Hannover-specific items (Kröpcke clock, road chunks, facades).
  Never Sketchfab Standard/Editorial or Synty (not redistributable in a public repo); avoid NC/ND.
- **Conversion tool** (headless Blender): import GLB/FBX/OBJ → join → decimate to a triangle budget →
  unwrap → bake base colour (+ AO) into one PNG → export OBJ (−Z forward, Y up, triangulated,
  normals + UVs, no MTL, origin bottom-centre, object at world origin) → preview render.
  Usage target: `convert_asset input.glb --tris 8000 --tex 1024`.
- **Characters:** realistic static poses swapped by state — rider (riding + ducking pose; lean by
  rotating the whole model), officer (2–3 running poses as flipbook + bob). Scooter wheels are separate
  OBJs with origin on the axle.
- **Style gate:** v0.2 starts with a style-test street slice (road, facade, scooter, bin, car) viewed in
  our engine; mass production only after the look is approved.
- **Folders:** `RunnerGame/Assets/` (runtime OBJ + PNG only), `RunnerGame/Art/scripts/`,
  `RunnerGame/Art/previews/`, `RunnerGame/Art/ASSETS.md` (register), `RunnerGame/CREDITS.md` (TASL).
- Kenney CC0 only as v0.1 placeholders.

## 4. Code structure, testing, versions

- **Cleanup:** namespace `Example` → `RunnerGame`, `CubeWindow` → `RunnerGameWindow`.
- **`Gameplay/` (no OpenGL):** `Player`, `Track`, `PatternLibrary`, `PatternValidator`,
  `ObstacleSpawner`, `Collision`, `Pursuer`, `RunState`.
- **`Rendering/`:** `SceneRenderer` (shadow → sky → world), model registry (each OBJ + PNG loaded once).
- **`Materials/`:** `RunnerLit/`, `Sky/`.
- **Tests:** `RunnerGame.Tests` (xUnit) for pattern validator, collision incl. duck height, 2-hit rule,
  jump arc. Done = warning-free build + green tests + played.

| Week (2026) | Version | Content |
|---|---|---|
| 1 · until 25 Oct | Setup + v0.1 greybox | Blender 5.2 + MCP (remove 4.2); all gameplay rules with cubes, score in title, restart |
| 2 · until 1 Nov | v0.2a look | conversion tool, style-test slice, RunnerLit with fog + sky + gamma |
| 3 · until 8 Nov | v0.2b assets | road chunks, facades, bin, cone, barriers, car/van, coin, scooter |
| 4 · until 15 Nov | v0.3 showcase | shadow mapping, Kröpcke clock, rider + officer poses |
| 5 · until 22 Nov | v1.0 submission | tuning, fixes, CREDITS/ASSETS, README, gameplay video, release build |
| 6 · until 29 Nov | buffer / add-ons | normal mapping, start/result screens, saved high score, tram, sound, 2nd zone |

**Cut lines:** shadows → blob shadows; Kröpcke → simplified silhouette; officer → single pose.
v0.1 gameplay is never cut.
**Split:** person A = code (gameplay, then shadows); person B = assets (sourcing, conversion, style
test, Kröpcke). Interface between them: OBJ + PNG in `Assets/`. Feature branches → PR into `main`,
tag per version.
