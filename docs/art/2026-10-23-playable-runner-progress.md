# First playable runner ledger

User approved moving from modelling into a playable build. Existing agreed gameplay spec and implementation plan define scope. Continue in the established workspace: installed art is largely untracked and required by the game, so a fresh checkout would omit the reviewed inputs. No commits, engine changes or shared-art edits.

Baseline solution builds; a fresh rebuild exposes the existing unused CubeWindow texture warning. Original Python photo-tool suite passes all 14 checks. Replacing the cube entry point removes its warning.

Simulation worker implemented the agreed API, then parent reran the 16 behavioural checks. Independent review found permanent safe-lane camping, focus-loss timing and missing score display. Simulation correction changes safe lanes between adjacent rows; 18 checks pass, including three seeds followed to the speed cap. EffectiveSpeed exposes hit slowdown for the title.

Rendering worker added project-owned gamma/fog material and cached installed meshes/textures. First real GPU capture succeeded: `docs/art/previews/runner-first-look.bmp`. Parent found facade backs facing the street and tree/clock placement conflicts. Renderer correction is underway, reusing current geometry. Camera framing shows player and upcoming hazards clearly; lighting/shadows remain first-pass.

Parent replaced rotating cube entry point with Ready/start, controls, pause/focus handling, restart and deterministic bitmap capture. Pure input-buffer worker is adding fixed-step/focus boundary tests before final integration. Independent review: `docs/art/2026-10-23-runner-review.md`.

Remaining: finish bounded corrections, rerun checks, inspect riding/duck captures and open actual game. No claim of live playtest until the game has been exercised; screenshots alone prove rendering only.

Closeout: all corrections completed and independent re-review PASS. Fresh reviewer runs: gameplay20/20, input8/8, manifest7/7. Parent inspected real riding, duck and caught GPU captures; officer and clock are readable. Hit obstacles now stay visible after contact and cannot deal repeat damage; coins disappear on collection. Facades face inward, tree crowns clear facades, and plaza tiles meet rather than overlap. Production solution builds with zero warnings/errors. Representative render:37 meshes,16 textures,207 draws. README documents controls, checks, honest limits and optimization targets. Live game launch follows; no claim of human playtesting.
