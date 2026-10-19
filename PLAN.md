# Project Plan: RunnerGame (Subway Surfers Inspiration)

## 1. Objectives & Constraints
* **Context**: University Master's course *Computergrafik & Interaktion* (1-semester scope).
* **Inspiration**: Subway Surfers (gameplay mechanics: 3 lanes, jump, slide, dodge obstacles, collect items).
* **Key Requirement**: The student must be able to explain every piece of code in detail during the examination.
* **Architecture Goal**: Keep the codebase organized, clean, modular, and concise (no over-engineering, unnecessary boilerplate, or complex third-party frameworks).
* **Upstream Rule**: [`Engine/`](Engine/) remains strictly read-only; all game code, shaders, and assets reside in [`RunnerGame/`](RunnerGame/).

---

## 2. Core Pillars for Evaluation

### A. Computer Graphics (CG)
1. **Curved World Vertex Shader**
   * Signature endless-runner effect bending the world downwards along the horizon.
   * Modifies vertex position in view space: $y' = y - k \cdot (z_{\text{view}})^2$.
   * Demonstrates understanding of coordinate spaces and vertex shader displacement.
2. **Lighting & Shading**
   * Directional sunlight using Blinn-Phong lighting (ambient, diffuse, specular).
   * Material parameterization (shininess, tints, textures).
   * Distance fog (linear or exponential) in fragment shader to cleanly blend far-off chunks into the background.
3. **Hierarchical Transformations & Animation**
   * Spinning collectibles ($M = T \cdot R(t) \cdot S$), bobbing items, and obstacle motion using transformation matrices.

### B. Software Engineering (SE)
1. **Engine Lifecycle Adherence**
   * Strict separation of simulation (`FixedUpdate`), input/animation (`Update`), and drawing (`Render`) using [`Engine.Application`](Engine/Application.cs).
2. **Object Pooling**
   * Reusing track chunks, obstacles, and pickups to prevent Garbage Collector pauses and maintain 60+ FPS.
3. **3D Collision Detection (AABB)**
   * Mathematically sound, lightweight Axis-Aligned Bounding Box tests between player and obstacles.
4. **Modular Architecture**
   * Single Responsibility Principle across dedicated, easily testable classes.

### C. Game Design (GD)
1. **Responsive Controls**: Immediate lane switching with smooth visual transitions; snappy jump and slide feedback.
2. **Pacing & Progression**: Dynamic speed scaling that increases difficulty over time.
3. **Fail & Restart Loop**: Clear feedback on hit, score accumulation, and quick restart flow.

---

## 3. Architecture & Directory Structure

```
RunnerGame/
├── Assets/                   # 3D models (.obj) and textures (.png)
├── Core/
│   ├── GameState.cs          # States: Menu, Playing, GameOver
│   └── InputHandler.cs       # Input polling and key bindings
├── Gameplay/
│   ├── Player.cs             # Lane index (-1, 0, 1), jump/slide state, position
│   ├── TrackManager.cs       # Object pool, chunk spawning, recycling
│   ├── TrackSegment.cs       # Individual track tile data & obstacle slots
│   ├── Obstacle.cs           # Low hurdle (jump), high barrier (slide), full block (switch)
│   ├── Collectible.cs        # Coins/gems with rotation & pickup detection
│   └── Collision3D.cs        # AABB bounding box definition and overlap tests
├── Rendering/
│   ├── Materials/            # Custom materials (e.g., CurvedWorldMaterial)
│   └── SceneRenderer.cs      # Batching draw calls and camera updates
└── Program.cs                # Application entry point & lifecycle coordinator
```

---

## 4. Phased Milestone Roadmap

### Phase 1: Player Controller & 3-Lane Movement
- [ ] Define player entity with lane positioning (Left: -1, Center: 0, Right: +1).
- [ ] Implement smooth horizontal interpolation between lanes.
- [ ] Implement vertical jump physics (simple gravity arc) and slide action (temporary hitbox contraction).
- [ ] Render a placeholder ground and player mesh.

### Phase 2: Procedural Track Spawner & Object Pooling
- [ ] Design modular track chunks (e.g., fixed length along the Z-axis).
- [ ] Implement an `ObjectPool<TrackSegment>` to spawn segments ahead and recycle behind the player.
- [ ] Establish constant or accelerating forward movement along the track.

### Phase 3: Obstacles & Collision System
- [ ] Implement 3D AABB struct (`Min`, `Max` vectors) for player, obstacles, and collectibles.
- [ ] Define obstacle variations:
  - **Low barrier**: Requires jumping over.
  - **High barrier**: Requires sliding under.
  - **Blockade**: Requires switching lanes.
- [ ] Detect collisions in `FixedUpdate` and trigger `GameOver` or score increment.

### Phase 4: Graphics & Custom Shaders
- [ ] Implement custom `CurvedWorldMaterial` with GLSL vertex displacement.
- [ ] Add distance fog to the fragment shader.
- [ ] Apply directional Blinn-Phong lighting and specular highlights to all scene elements.
- [ ] Add hierarchical model animations (spinning coins, bobbing items).

### Phase 5: Polish & Game Loop
- [ ] Add score tracking (distance survived + collectibles gathered).
- [ ] Implement gradual speed ramp-up over time.
- [ ] Implement game-over state and clean restart mechanism.
- [ ] Code review, code cleanup, and documentation for oral exam preparation.

---

## 5. Notes & Future Revisions
*(Place for ideas, visual theme changes, or mechanic tweaks to be discussed later)*

