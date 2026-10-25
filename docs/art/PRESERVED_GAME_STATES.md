# Playable checkpoint before further map work

Saved on 2026-10-25 in `preserved-game-states/2026-10-25-before-map-work/`.

From the repository root, double-click:

- `Play-Original-Streets.cmd`: original endless street game, road lanes, traffic and shopfronts.
- `Play-Hannover-Map.cmd`: new finite Hannover pedestrian map, starting at Hauptbahnhof.

When the local checkpoint exists, both launch the frozen executable and installed assets, independent of future builds. The map files are copied into the checkpoint as well. On a fresh checkout without that local folder, the launchers build and run the corresponding development mode using the .NET 10 SDK. Enter starts; A/D steer, Space jumps, S ducks, Esc pauses, R restarts.

The checkpoint includes a gameplay/engine source ZIP, credits, and SHA-256 inventory. All copied runtime and map files were compared with their originals by SHA-256. Both saved modes were checked with actual OpenGL captures.

This is a local checkpoint excluded from Git, not an external backup. Copy the entire checkpoint folder elsewhere to back it up. Art authoring sources remain in the main workspace; the ZIP preserves application/engine source, not the complete art research archive.

Normal development still supports both modes: no `--map` uses the original streets; `--map RunnerGame/Art/assets/hannover_public_realm/out` uses the evolving Hannover map.
