# Pitfalls

- Downloads: **curl, not urllib** (old cert store). Wikimedia: project User-Agent, >= 1 s between files; a non-JSON reply = rate limit,
  wait 60 s and retry (`fetch` does this; never hammer). Titles may be non-ASCII (`Bâle`, `ü`): keep them in UTF-8 files, never pass them
  as shell/curl arguments, and expect a garbled Windows console.
- EXIF: reference copies are already transposed; measure and mark landmarks on `ref/NN.jpg` only, never on originals.
- Blender: absolute output paths; headless only; do not use `mcp__blender__*` for builds (the live Blender is shared with other sessions).
- Grid images: read the printed LABELS (source px), not positions on the displayed image; zoom with `--crop` for small parts.
- Near-face perspective: widths/heights of near-side parts read from a side photo are too big; correct after the first compare. Widths
  invisible from the side are estimates - mark them so in `source`.
- Leaning or parked objects bias the camera fit; prefer upright photos as key views.
- A file open in an image viewer can be locked on Windows; close it or write a new name.
- Large objects: the viewer's clip planes scale with the model; for a photo-like engine view use `--pitch 5`. `Camera.FarPlane` defaults to
  100: raise it for long tracks.
- Tapering shapes (gables, spires): build trapezoids/frustums per measured segment, not stacked boxes (box corners show as ghosts).
- A band inside a gable is easily misread as an eave; confirm heights on the 1:1 blend zoom.
- Symmetric objects: measure one half and mirror; small left/right differences in the photo are perspective, not model errors.
- No logos, wordmarks or QR codes (invent plate numbers). No photo pixels in textures; colours come from spec.json.
- Reference photos are CC BY / CC BY-SA: credit every one in `RunnerGame/CREDITS.md`. Only add assets we may share.
- Budgets in the engine: one draw call per mesh, no instancing, no LOD. A `replica` object that appears many times on the track costs
  many times; say so at Gate A when the object will be repeated.
