# Measure and compare (steps 2 and 4)

Contents: sections and parts · measuring · spec.json / refs.json · camera and fit · the compare loop · reading the results

## Sections and parts

A *section* is a named box in a key photo around one distinct part (tower, dome group, gable, wheel, handlebar, glass, legs...).
Write boxes into refs.json: `"sections": {"<name>": [x0, y0, x1, y1]}` in photo pixels, cut tight so the part fills the box.
- **sections loop:** boxes only in the key photo you loop on.
- **parts loop:** EVERY key photo gets the same names. The same boxes are then used three times:
  1. measure: a 1:1 grid of the box (`grid --crop <box> --step 10`);
  2. build: `python RunnerGame/Art/lib/photo_tools.py crops A` writes `A/previews/crops/crop_<part>_<NN>.png` (2x, every key photo);
     the builder brief names exactly those files for the part it works on (<= 2 images);
  3. check: `BL --python RunnerGame/Art/lib/compare.py -- A --part <part>` -> `A/previews/part_<part>_r<k>.png`, one row per key photo:
     photo | model colour | 50/50 blend. A part is done when NO row shows a double image. Worst part first.

## Measuring (step 2)

Pick a ruler with a known real size (wheel diameter, published facade length, tower height, a standing person for scale only).
Measure **each section on its own 1:1 grid** BEFORE the first build, and record a **profile**, not one number: the width at 4-6
heights from bottom to top (gable, roof, spire, cap, tower = a list `[[z, width], ...]`), plus the features on it (window axes x,
rows z0-z1, arches, pediments with their own width). Read the printed LABELS on the grid, not positions on the displayed image.
```
python RunnerGame/Art/lib/photo_tools.py grid A/ref/NN.jpg A/previews/grid_NN.png [--crop x0,y0,x1,y1] [--step 50]
python RunnerGame/Art/lib/photo_tools.py color A/ref/NN.jpg x0,y0,x1,y1          # median patch -> LINEAR rgb
python RunnerGame/Art/lib/photo_tools.py measure A ref/NN.jpg A/measure_NN.json   # prints metres per pair
```
Zoom 1:1 (crop x2) on a part BEFORE counting repeated elements. Sample colours on flat shaded areas, not sunlit ones.
Read landmark pixels from the grid into that photo's `landmarks` in refs.json (`{"name": [x, y]}`).
`measure_NN.json` = `{"ruler": ["lm_a","lm_b",metres], "pairs": {"wheelbase": ["front_axle","rear_axle"], ...}}`.

## Formats

`spec.json` (metres, degrees, linear colours; every value has a `source`):
```
{"ruler": {"photo": "ref/17.jpg", "from": "lm", "to": "lm", "metres": 0.254, "note": "..."},
 "detail_level": "replica", "tri_budget": 25000, "tex_res": 2048, "workflow": "parts",
 "dims":   {"wheel_d": {"value": 0.254, "source": "ruler"}, ...},
 "colors": {"paint": {"linear": [r, g, b], "source": "ref/02.jpg box 740,500,760,550"}, ...}}
```
`refs.json`: `{"photos":[{file,title,author,licence,source_url,size:[w,h],view,key,landmarks:{name:[x,y]},camera,camera_z_range,
lens_shift,sections}]}`. A re-fetch keeps view/key/landmarks/camera by title.
`build.py` follows `scooter_voi/build.py`: `build(spec) -> dict[str, list[Object]]` (parts, e.g. `body`, `wheel_front`); numbers only via
`spec.d("name")` / `spec.c("name")`; `import photo_lib as pl` (`pl.al` = asset_lib; `pl.tube`, `pl.arc_shell`, `pl.landmark`); an
`LM_<name>` empty (`pl.landmark(name, loc)`) for every landmark in refs.json. Smoke test:
`BL --python A/build.py -- --preview /abs/path/A/previews/preview.png`.

## Camera and fit (step 4)

Needs a rough `camera` per key photo: `{"loc":[x,y,z],"look_at":[x,y,z],"lens_mm":26,"roll_deg":0}`. Straight-on perspective-corrected
photos get `"lens_shift": true` (fit then also solves lens shift and keeps the view level; without it a plain camera fakes the
shift with a far telephoto). Set `"camera_z_range": [lo, hi]` from where the photo was taken.
```
BL --python RunnerGame/Art/lib/compare.py -- A ref/NN.jpg --fit              # fit camera to landmarks, save to refs.json
BL --python RunnerGame/Art/lib/compare.py -- A ref/NN.jpg --errors           # signed landmark errors (numbers only)
BL --python RunnerGame/Art/lib/compare.py -- A ref/NN.jpg --errors --starts  # many start cameras; use when the fit goes telephoto
```
Signed errors: `+dx` = model too far right, `+dy` = model too low. A fit that always lands on a far telephoto means that photo's
landmarks contradict the model: re-read them on a zoom (a 30 px misread corner cost 15 px RMS) before changing the model.

## The compare loop

```
BL --python RunnerGame/Art/lib/compare.py -- A ref/NN.jpg --sections   # ONE sheet, a row per section: photo | colour | 50/50 blend
BL --python RunnerGame/Art/lib/compare.py -- A --part <name>           # parts loop: one part in all key photos
BL --python RunnerGame/Art/lib/compare.py -- A ref/NN.jpg [--zoom x0,y0,x1,y1]   # outline overlay (+ _blend, _blend_zoom at full res)
```
- Done = no section/part shows a double image (ghost edge, offset window, protruding step). The landmark RMS is only a pre-check:
  it is partly circular (landmarks and fit use the same photo) and blind inside the silhouette; the blend sees windows, gables, pinnacles.
- For a ghost you cannot place, crop the model panel of the sheet at that spot (model-only view).
- Heights of set-back parts (domes, finials) come from the more distant/higher photo, front edges from the straight-on one.
- When an engine view contradicts the blend, suspect the tool first (far plane, normals) and check with numbers (OBJ bounds).
- Derive spec corrections, rebuild, repeat. Each round: change numbers in spec.json, never geometry by hand.
