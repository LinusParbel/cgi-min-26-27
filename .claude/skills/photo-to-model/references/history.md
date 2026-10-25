# History: what each model taught

The skill improves by modelling real Hannover objects with it; every mistake that cost rounds became a rule (`lessons.md`), a tool or a
test. Long version: `docs/handoff/2026-10-18-photo-to-model-handoff.md`.

| Model | Class / loop | Installed | Tested | Changed in the skill |
|---|---|---|---|---|
| Voi scooter (`scooter_voi`) | vehicle, moving parts, budget 8k | `Models/Fahrzeug/ScooterVoi` | side view, wheels as separate parts, pivots, camera fit | spec with a source per value; builder + reviewer agents; stop format; token routing (one image per round, model per step) |
| Neues Rathaus (`rathaus_hannover`) | facade, symmetric, ~24.5k | `Models/Wahrzeichen/NeuesRathaus` | profiles, shape vocabulary, sections sheet | detail class at Gate A; 50/50 blend + `--zoom` + `--sections`; `camera_z_range`; profiles; `builder_brief.md` shape vocabulary; "prove a test can fail". Estimated ~15 rounds -> 2-3 (not measured) |
| Kröpcke-Uhr (`kroepcke_uhr`) | ornate, replica, ~24k, 2048² | in progress (legs part left, review, Gate C) | parts loop, two key photos, glass, lens shift + level fit | parts workflow (same-named sections, `crops`, `--part`); mutate build not spec; surface tests; loop on both photos; zoom before counting; glass baking; `geom_probe.py`, `mutation_check.py`, `compare.py --errors --starts` |
| Navy commuter bike (`bike_commuter`) | replica, ~15.7k, 2048² | `Models/Fahrzeug/BikeCommuter` | photo build after downloaded Bushido/PyBullet models were rejected (rough, licence unknown) | route B needs a licence check before work; `--mutate-spokes` style tests led to `mutation_check.py` |
| Ordnungsamt officer v2 (`ordnungsamt_pursuer_v2`) | adopted MakeHuman/MPFB base (CC0), 73.7k per pose x 40 poses | `Models/Charakter/Ordnungsamt` | route B for anatomy; baked pose sequence | route B reference; frame-count budget; provenance.json |

## Not yet tested by any model
- Route B on a non-human object, and a measured token comparison A vs B.
- Curved or organic shapes (wheelie bin, tram body): the shape vocabulary in `builder_brief.md` is facade/ornament shaped.
- Objects without a clean side view or with only one usable photo.
- The `sections` loop on its own for a `medium`/`backdrop` object (every model so far ended in the parts loop).
- A model where the user raises the class at a later gate.
- Proposed twice, not built: a joint fit of key dimensions and both cameras (would remove the remaining two-photo contradictions).

Run these through `evals/evals.json` and log the metrics there; they are the evidence for the next change to this skill.
