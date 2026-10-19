# Project Guidelines: CGI-MIN (RunnerGame)

## Context & Scope
- University computer graphics project built with C# (.NET 10) and OpenTK 4.9.4 (OpenGL 3.3 Core Profile).
- The primary development target is the `RunnerGame/` project (`RunnerGame/RunnerGame.csproj`).
- **Rule:** Treat `Engine/` as read-only upstream code. Do not edit files in `Engine/` unless explicitly instructed, so future lecture updates can be merged cleanly via Git tags without merge conflicts.
- Implement any custom materials, shaders (`.glsl`), and gameplay components inside `RunnerGame/`.

## Architecture & Frame Loop
- Applications inherit from `Engine.Application`.
- Respect the strict lifecycle separation:
  - `Initialize()`: Load meshes, textures, materials, and configure scene lights (`DirectionalLight`).
  - `FramebufferResized(width, height)`: Handle viewport resizing via `renderer.Resize(width, height)`.
  - `FixedUpdate(fixedDeltaTime)`: Physics, collision checks, and fixed-rate simulation.
  - `Update(deltaTime)`: Player input, camera controls, movement, and animation states.
  - `Render()`: Pure draw calls (`renderer.Clear()`, `renderer.Draw(mesh, material, modelMatrix, camera)`). Do not update state or calculate elapsed time here.
  - `Shutdown()`: Dispose meshes, textures, and renderer resources cleanly.

## Build & Run Commands
- Build solution: `dotnet build CgiMin.sln`
- Run RunnerGame: `dotnet run --project RunnerGame/RunnerGame.csproj`
- Run Example: `dotnet run --project Example/Example.csproj`

