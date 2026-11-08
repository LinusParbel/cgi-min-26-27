# Render visibility and animation work

Status: implemented and technically validated, 2026-11-08; user playtest pending.
User requested a specification,
task execution and validation as work proceeds. No commit or push requested
for this implementation yet.

## Problem and intended behaviour

The street's aerial environment currently submits entire 420-metre districts,
including buildings outside the view. The normal pursuer also decodes and
uploads a dense animated mesh while behind the chase camera. Keep the full
environment available in memory, but submit geometry only when a rendering
pass needs it. Gameplay simulation must remain independent of visibility.

Baseline and methodology: [performance analysis](../../art/previews/performance-20261108.md)
(local ignored evidence). Intel Iris Plus, 1280×800, Release synchronized
render medians: street 61.29 ms, ticket shot 48.35 ms. These are diagnostic
render timings, not live gameplay FPS.

## Design

- Conservative axis-aligned mesh bounds, transformed for rotation, translation
  and nonuniform scale. Test all six OpenGL clip planes using the engine's
  row-vector matrix convention. Intersecting bounds remain visible, including
  near-plane crossings and a camera inside a building.
- Camera and light visibility are separate. Camera rejection never removes a
  caster from the light pass. Continue refreshing shadows; no stale map cache.
- Divide district building geometry into spatial groups, retaining the exact
  detailed meshes, roof closures, plaza exclusions and texture coordinates.
  No animation-time switch that suddenly spawns the surrounding city.
- Static street models and props use the same per-pass bounds tests. Shared
  shadow rendering also filters map casters. Map colour rendering is evaluated
  separately rather than assuming a street-only change covers the whole game.
- Before sampling the normal animated pursuer, test a conservative bound for
  its complete run cycle at the intended transform against camera and light.
  Hidden actors keep their simulation/gait clock; re-entry samples the current
  time without replaying skipped frames. Visible shadow casters still animate.
- Initial scope leaves authored cinematic actor sampling active. Filter their
  draw submissions using bounds updated with deformed vertices. Preserve cone
  and van timing, contact, sounds and gameplay transitions. General cinematic
  animation skipping requires validated full-motion bounds and is a follow-up,
  not implied by enabling geometry culling.
- No occlusion queries, streaming/unloading, physics culling, reduced shadow
  resolution or simplified building models in this iteration.

## Tasks and acceptance evidence

- [x] T1: bounds/frustum maths with tests for all six planes, plane crossing,
  rotated/scaled bounds, camera-inside and offscreen shadow caster retention.
- [x] T2: pursuer visibility before sampling; counters distinguish skipped
  animation from skipped colour draws. Validate normal hidden and close states,
  then hidden-to-visible re-entry at the current gait time.
- [x] T3: spatial city chunks and independent camera/light filtering of static
  models, props and animated mesh submissions. Verify chunk union preserves
  original geometry counts/bounds and protected landmark plazas.
- [x] T4: shadow and map integration; validate map rendering and prevent camera
  culling from deleting offscreen casters. Retain van opening geometry.
- [x] T5: repeat comparable Release timings and allocation measurements; capture
  street, opening, van and cone key shots, district wrap and aspect ratios.
  Compare the full cone sequence frame-by-frame for culling-induced popping.
  Report technical and visual evidence separately; normal-speed user playtest
  remains subjective acceptance.

Target: substantial improvement over the street baseline (at least 30% lower
median on the same local diagnostic), essentially no per-frame clip allocation
when the pursuer is not needed, fewer submitted colour/shadow triangles, no
missing visible geometry or shadows. Treat draw-count changes alone as
insufficient evidence. Record failures and remaining limitations here.

## Validation record

Specification created before runtime changes. All five implementation tasks
technically complete; subjective playtest acceptance remains open.

### Automated and runtime checks

- Release game build: no warnings/errors.
- `RunnerGame.Rendering.Tests`: 2,062 visibility checks plus 176 existing
  manifest/geometry checks passed. Includes a full vertex/normal/UV multiset
  comparison of the spatial chunks against the original combined district;
  every integer run-cycle sample 35–75 fits the conservative pre-sampling bound.
- `RunnerGame.Tests`: all gameplay contracts passed, including pause/restart,
  deterministic fixed ticks, pursuit recovery, collisions and both crash triggers.
- `RunnerGame.AnimationTests`: clip, timeline/contact, camera, audio and opening
  handoff checks passed. Shared clip/texture/mesh bytes were not changed.
- `RunnerGame.MapRenderTests`: metadata and translated shadow-space checks passed.
- Runtime hidden/visible/hidden/visible pursuer check passed. Re-entry GPU vertex
  positions exactly equal a fresh clip sample at current simulation time
  (maximum position error zero); rendering leaves simulation time/distance alone.
- Ten real-game screenshot pairs with culling on/off are pixel-identical:
  street, opening at 17 s, cone at 1.8/2.8/7.3/12 s with distance 390, cone at
  8.5 s across district distances 419/421, van opening at 3.7 s, map inspection
  at distance 100. Contact sheet reviewed: roofs, ticket, skyline and hole remain.
- Full cone sequence: 511 paired frames at 30 Hz, distance 390, zero differing
  frames or colour channels. This checks every sampled frame for introduced
  disappearing geometry/shadows; it does not establish subjective acting quality.
- Ten additional paired shots at portrait (0.6) and wide (2.4) viewport aspect
  ratios are pixel-identical at 0/2.8/7.3/12/16.5 seconds.

### Performance

Same Intel Iris Plus, Release, 1280×800, 30 warm-up/90 measured frames per case,
VSync off, fixed 1/60 simulation, traffic excluded, synchronized GL.Finish render
timing. Swap, simulation, audio and cold loads are excluded. This run compares
the same spatial geometry with visibility enabled/disabled. It also repeats
street cases in reverse order to check order sensitivity.

| Case | Culling disabled median | Enabled median |
|---|---:|---:|
| Street | 67.10 ms | 24.61 ms |
| Street, reverse-order repeat | 56.59 ms | 21.42 ms |
| Ticket shot, 6.5–8 s | 59.54 ms | 27.62 ms |

Street render medians improve by about 63% in both orderings. Render-thread
allocation falls from 3.776 to 0.0209 MiB/frame. All 90 measured hidden-pursuer
frames skip sampling (zero pose updates). Average submitted colour/shadow
triangles drop from 3.58 million combined to 1.01 million (0.71 colour + 0.30
shadow). Ticket allocation remains approximately 0.79 MiB/frame because authored
cinematic animation still runs. These are render timings, not live-game FPS.

Local ignored evidence: `docs/art/previews/perf-visibility-20261108.json` and
`docs/art/previews/visibility/` (comparisons, contact sheet, timeline/re-entry
results). The local diagnostic harness is under `tools/asset-spike/out/perf-probe`.
Repeat captures with the game's `--no-culling` option to disable both passes and
the pursuer sampling gate without changing geometry or the simulation clock.

### Limits and next decisions

- Bounds culling is conservative: it does not detect buildings hidden behind
  other buildings. No GPU occlusion queries or streaming were introduced.
- Maps receive per-part colour/light filtering, but their large authored city
  meshes were not repartitioned. Smaller map batches can be evaluated separately.
- Normal street pursuer shadow influence is swept down to -0.5 m, covering the
  street/pavement receiver region. This special check is not used in the van
  hole, maps or either cinematic; those keep independent light-frustum casters.
- Cinematic pose updates remain active. General animation skipping and reduced
  vertex-clip allocation are later work requiring complete animated bounds.
- Assets remain loaded; this optimizes frame work, not cold startup or RAM use.
- User real-time playtest, including camera resizing and both cinematics, remains
  the final subjective acceptance check. No motion/audio edits or new push.
