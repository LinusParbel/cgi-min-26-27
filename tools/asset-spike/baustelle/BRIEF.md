# Baustelle props — shared brief for all asset agents

Project: "Hannover Rush Hour", a 3-lane endless runner (uni CGI course) on a minimal C#/OpenTK engine.
Look: **semi-realistic** German street props. Everything below is binding for every agent.

## Engine constraints

- The engine loads **one OBJ + one PNG per mesh** (v/vt/vn/f; `.mtl` ignored; no vertex colours,
  no PBR, no normal maps, no transparency, back-face culling ON → flipped normals = invisible faces).
- Lighting is simple Phong with one point light; texture colours are displayed as-is (no sRGB
  conversion). So all surface detail must live in geometry + the baked colour texture.
- Objects pass the camera at 12–30 m/s, seen mostly from the front and slightly above, 5–40 m away.
  Silhouette, colours and the big graphic patterns matter most; tiny details matter little.

## Pipeline (use it, don't reinvent it)

- Blender: `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`, run **headless only**:
  `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup --python <your_script.py>`
- **Never use the `mcp__blender__*` tools** — they drive the user's live Blender, shared by everyone.
- Shared library: `tools/asset-spike/asset_lib.py` (read it first). Do NOT edit it. If you need
  something different, write a helper in your own script and mention it in your report.
  Key functions: `clear_scene`, `material` (weathered; `image=` for artwork via the `src` UV layer),
  `flat`, `emissive_look`, `box`, `cyl` (cylinders/cones, any axis), `image_plane`, `set_src_uv`,
  `join_all`, `bake_and_export`, `render_previews`, `import_obj`, `tri_count`.
- Example of the style bar: `tools/asset-spike/gen_wheelie_bin_v3.py` (German wheelie bins) and its
  result `tools/asset-spike/out/comparison_v3.png`.
- Engine check (the ground truth!): render your exported asset with the course engine:
  `dotnet tools/asset-spike/SpikeViewer/bin/Debug/net10.0/SpikeViewer.dll <obj> <png> <out_prefix> 0,30,160`
  → writes `<out_prefix>_0.png`, `_30.png`, `_160.png` (angle = model rotation; 0 = front towards camera).
  Do not rebuild or modify SpikeViewer.

## Conventions

- Blender is Z-up, 1 unit = 1 m, real-world dimensions.
- The **front** of a prop faces **-Y** in Blender (that side faces the runner camera in the game).
- `bake_and_export` moves the origin to the bottom centre and the object to the world origin
  (unless `keep_origin=True`). Export axes are handled by the library (−Z forward, Y up).
- Names: `PROP_<Name>[_<variant>]`, e.g. `PROP_Leitbake_rechts`. Texture 1024² unless stated.
- Your files only: script(s) in `tools/asset-spike/baustelle/`, outputs in
  `tools/asset-spike/out/baustelle/<your_asset>/`. Never touch other agents' files, the repo's
  game code, or git (no commits).
- `transform_apply()` in Blender applies location+rotation+scale by default — `box()`/`cyl()` handle
  this correctly; be careful in your own code. Decals/stickers need ≥1 mm offset from the surface.
- Long Cycles bakes are normal (1–3 min); run Blender in the foreground with a long timeout.

## References

- Contact sheet + photos: `tools/asset-spike/ref/baustelle/` (`contact_sheet.png`, `NN.jpg`,
  `index.tsv` with titles/licences). Reference photos are for viewing only, never baked into assets.
- Official StVO sign graphics (public domain, OK to bake into textures): `tools/asset-spike/ref/signs/`
  `z123.png` (Zeichen 123 Arbeitsstelle, RGBA, transparent outside the triangle),
  `z605.png` (Zeichen 605-10 Leitbake 1000×250, Aufstellung rechts), `z600.png` (Zeichen 600-34
  Absperrschranke 250×1600), `z610.png` (Zeichen 610-40…43 Leitkegel variants).
- Only the Leitkegel agent may query the Wikimedia API (rate limits!), via
  `bash tools/asset-spike/fetch_refs.sh <out_dir> <n_per_query> "query" ...` (it paces itself).

## Warnleuchte (warning lamp) is a separate asset

The yellow warning lamp is modelled once by its own agent and placed by the game on top of carriers.
- Lamp OBJ origin = the bottom centre of its mounting clamp (the point that sits on the carrier).
- Carrier agents (Leitbake, Absperrschranke) do **not** model the lamp. Instead they write
  `mounts.json` next to their OBJ: `{"mounts": [{"x": .., "y": .., "z": ..}]}` in **Blender
  coordinates of the exported object** (origin bottom centre), one entry per lamp position (on the
  top edge, centred on the board/rail thickness).

## Quality loop (mandatory, token-budgeted)

Build -> bake/export -> ONE engine sheet (`bash tools/asset-spike/engine_sheet.sh <prefix> <sheet.png>`) ->
compare with the reference -> fix. **Max 3 iterations**; stop as soon as the checklist passes.
Image rules: one engine sheet per iteration, never re-read old iteration images (delete them), previews at
`size=384`, use numbers (bounds, tris, texel colours via `python -I`) instead of extra screenshots.
Checklist:
1. Silhouette and proportions match the reference (compare ratios).
2. Real dimensions within +-10 % of the spec.
3. Front faces -Y; at angle 0 in the engine you see the front.
4. No missing faces (flipped normals), floating parts, z-fighting, intersecting parts.
5. Artwork sharp, not mirrored, correct colours in the ENGINE sheet.
6. Weathering plausible and subtle.
7. Triangle budget and texture size respected.

## Report (your final message)

- Files produced (absolute paths): script, OBJ(s), PNG(s), preview sheet(s), engine screenshots, mounts.json.
- Real dimensions, triangle counts, texture sizes per variant.
- Iteration log: what you saw wrong each round and what you changed.
- Remaining known issues / ideas, honestly.
