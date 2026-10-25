# Route B: adopt a free-licensed base model and modify it

Use this instead of building from scratch when scripting the shape is the expensive part and a base with a clear licence exists.
The same gates, budgets, review and export apply; only steps 1-3 of the flow change.

Contents: when to choose it · licence gate · process · budget · what the two earlier runs showed

## When to choose it (Gate A, after the photos and the shortlist; you recommend, the user decides)

| Situation | Route |
|---|---|
| A specific real thing that must be recognisable (landmark, a given tram, the Hannover bin) | **A: photos** - no downloaded model is the right one |
| Organic or anatomical shapes (people, animals, trees) where scripting costs many rounds | **B: adopt** (officer v2: MakeHuman/MPFB base + clothes) |
| A generic but detailed category (a city bike, a bench) where a clearly licensed model exists | **B: adopt**, then match colours/proportions to the photos |
| Textures, materials, HDRIs | take CC0 (Poly Haven) directly, no model route needed |
| B chosen but the base needs many changes to look like the real object | **Hybrid**: adopt, then run the normal measure/compare loop on the parts that matter |

Out of scope: AI 3D generators (the user rejected them) and anything without a verifiable licence.

## Licence gate (hard stop before any work)

Read the licence on the **source page**, not the file name or a forum post. Record it before opening the model.
| Licence | Use |
|---|---|
| CC0 / public domain | yes |
| CC BY | yes, credit in `RunnerGame/CREDITS.md` |
| CC BY-SA, NC, ND, "free download", unknown, "personal use" | no - ask the user first (the game and its models are shared) |
Software licence and asset licence are separate (MPFB addon code vs its CC0 assets). Check every extra asset individually.
Write `A/provenance.json`: per source `url, author, licence, retrieved (date), sha256 of the download, what we changed`. The reviewer checks it
against CREDITS.md. Keep raw downloads in `.model-research/<name>/` (untracked); only the modified derivative goes into the asset folder.

## What the photos do in route B

The shape comes from the base; photos only say what to change (colours, clothing and fitting details, lettering, proportions) and check the
result. Default is a light match: colours into spec.json, then one or two photos against the model in the blend sheet. Hybrid (landmarks +
compare loop) only on parts that must match a specific real object. No photo pixels in textures.

## Process

1. **Scout after the photos, download after Gate A.** The photo pack comes first and sharpens the search (exact model, generation, proportions,
   colours). Shortlist <= 3 candidates from thumbnails and the source page: link, licence, triangle count, difference to the photos. Download
   only the one the user picks at Gate A. Search with the library's site or the Blender MCP `search_assets` (read-only; never build in the shared live scene).
   Download with curl. Do not re-download what `.model-research/` already holds.
2. **Inspect headless** (tri count, bounds, parts, materials, orientation, scale). Decide what to keep; drop hidden and interior faces, props you do not need.
3. **Normalise.** 1 unit = 1 m, ground at z 0, facing (-Y props, +Y vehicles), transforms applied, separate parts with pivots on their axes.
4. **Reduce to the budget** (class table in `SKILL.md`). Do not decimate faces/hands/wheels blindly: check visually first, as the officer run did.
5. **Match the real thing** if it must resemble one: colours from spec.json (photo samples), proportions via the usual `refs.json` landmarks and
   `compare.py`; only the parts that matter, not a full parts loop.
6. **Texture and export** with `bake_shared_and_export` (one shared atlas). No logos, no photo pixels.
7. **Review and gates** as in `SKILL.md`; the reviewer also checks `provenance.json` and CREDITS.

## Budget: count frames, not just meshes

The engine loads every OBJ as its own mesh and has no skeletal animation. An animated character is a sequence of baked poses, so the
budget is `triangles per pose x poses`. Officer v2 ships 73,710 triangles x 40 poses; decide at Gate A how many poses and what total is acceptable
(and whether a smaller class fits the game camera), instead of discovering it at install.

## What the two earlier runs showed

- **Officer v2 (adopted base, approved and installed 2026-10-20):** MPFB base + CC0 clothes gave correct anatomy, hands and shoes, which the
  scripted v1 never reached. It still took many sessions (fitting, uniform, vest, labels, run cycle, 40 poses). Token saving versus a scripted
  build is **not measured**; log rounds and tokens for the next run.
- **Bike (downloaded Bushido glb + pybullet parts, not used):** the files were rough and their redistribution licence was never established, so the
  bike was scripted from photos instead. Lesson: check the licence and look at the model at inspect time, before investing; a download that fails the
  gate costs a round, not a model.
