# First playable renderer

`SceneRenderer(assetsRoot)` expects the installed `Assets` directory, with a live OpenGL context. Call Resize, Render and Dispose on that context's thread. Rendering reads simulation properties only.

Implemented project-owned linear-light diffuse/specular shading with encoded PNG decode and output encode, matching distance fog and sky, fixed chase camera, recycled 20 m streets and 6 m facade bays. Pavement furniture, trees and the clock stay outside the playable lanes. Every object kind maps to an installed asset. Scooter wheels rotate around converted installed pivots; exactly one ride/duck pose is drawn. Four sampled officer frames face engine -Z after pursuit begins. Tokens spin around engine Y.

Each distinct OBJ and texture path has one GPU cache entry. Constructor failure cleans partially created resources; repeated Dispose is harmless. Diagnostics expose MeshCount, TextureCount and the latest DrawCount. Static scene is approximately 170 draws plus obstacles (vehicles use five parts each); no pedestrians or dense repeated landmark geometry.

`ModelManifest` is graphics-independent: Read validates file references, relative path containment and finite 3-coordinate pivots, then converts Blender `(x,y,z)` to engine `(x,z,-y)`. Its public methods support parent asset contract tests. All runtime references were inspected against installed files. `dotnet build RunnerGame/RunnerGame.csproj --no-restore` succeeded after gameplay contract arrived; the only warning was from the old cube Program.cs awaiting replacement by parent.

Visual verification remains the parent entry-point/screenshot task. Shadows and normal maps are outside this first playable integration. Four officer frames are a deliberate memory/initial-load tradeoff and produce a coarse gait.

First screenshot feedback corrected facade facing (right -90 degrees, left +90), reduced street trees to .60 scale, and reserved a facade gap with an extra reused pavement mesh around the clock. Trees within five metres of that square are omitted. No asset geometry changed.

`dotnet run --project RunnerGame.Rendering.Tests/RunnerGame.Rendering.Tests.csproj --no-restore` passes seven graphics-independent behavioural checks: known pivot conversion and path resolution, absolute paths, traversal, malformed and nonfinite pivots, and traversal embedded in a manifest. The harness references the actual runtime helper.
