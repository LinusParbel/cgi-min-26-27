# Officer v2 — refined Hannover uniform checkpoint

Supersedes the anatomy-only October 20 preview checkpoint. The user approved the proposed navy service jacket, shoulder tabs/pockets, belt, straighter trousers, black lace-up boots, shorter hair and more mature fictional face, and explicitly requested autonomous reference comparison/iteration before returning for review. Do not repeat that appearance-direction interview.

## Current source

`RunnerGame/Art/assets/ordnungsamt_pursuer_v2/`

- `officer_v2.blend`: packed-texture neutral A-pose, 53-bone MPFB rig. Approximately 119,308 evaluated triangles including curves/individual facial hairs. This is the editable source, not an approved runtime budget.
- `build.py`: current entry point, runs `build_refined.py`. Headless Blender 5.2; append `-- --draft` for lower resolution/sample count. Original anatomy build retained in `build_anatomy.py` with `checkpoints/anatomy_preview.blend`.
- `generate_textures.py`: reproducible ID label and SVG-to-PNG sleeve arms artwork. `source/provenance.json`: incorporated CC0/public-domain assets and reference-only photo sources.
- `fit_labels.py`: fits labels against final evaluated cloth after all parenting/dependency updates; also repairs/rerenders an existing saved scene.
- `verify.py`: independently reopens saved scene; verifies 53 bones, all textures packed, six render views, zipper meshes at front, back label UV/material and 6 mm clearance across all its vertices. Writes `previews/validation.json` with actual evaluated mesh/curve counts and bounds.
- `review_sheet.py`: produces `previews/review_sheet.jpg`. Six full-res PNGs: three_quarter, front, back, face, hand, shoes.

## Visible changes

Closed navy service jacket adapted from official MakeHuman clothing; pale blue inner neckline, shoulder tabs, chest pockets, lower pocket welts, central zipper, sleeve shields with Hannover arms. Dark two-line city labels read “Stadt Hannover / Ordnungsdienst”. Fitted duty belt, closed utility pouches, shoulder microphone/speaker grille and coiled lead. Proper `shoes03` boots with narrowed hidden uppers, clean rubber sole materials, crossed vamp laces/eyelets. Short textured `short01` hair replaces the solid long-sideburn hair mesh. Age/jaw targets, subtle skin pores/creases and tapered individual moustache hairs replace the flat sticker moustache.

## Comparison / repair history

Several render/fix passes were completed autonomously. Initial `male_casualsuit05` blazer rejected for lapels/long hem; the closed jacket uses `male_casualsuit01` geometry instead. Fits caught/corrected: sleeve placement outside cloth, cable crossing armpit gap, lace centers outside the fitted boots, old boot sock uppers penetrating trousers, misplaced blue insert, zipper raycasts reaching the back through the open neck, belt floating away from waist, lettering sinking into cloth folds. Labels now use original generated woven-text textures, not separate glyph meshes, on densely fitted panels.

The final saved-scene checker initially caught back-label clearances between -1.55 and +7.56 mm. The final dependency-state refit corrected all label vertices to 6 mm; the separate saved-file check then passed. Do not remove this regression check. Geometry after fitting remains visually reviewed in affected front/back/three-quarter renders.

## Limits / next work

This is a recognizable, reference-led model interpretation, not a measured replica. The photos show multiple seasonal uniform variants. Exact shoe brand/tread, every seam and pouch layout cannot be established; face is fictional, not a likeness of a photographed officer. Do not claim a perfect 1:1 replica or photorealism.

No run cycle or game bake/export performed. Body/clothing have MPFB weights; accessory/patch/hair-curve deformation and rigid weights still need animation preparation. Blender hair uses alpha cards; the opaque-only engine needs a separate opaque hair solution before baking/export. Optimize the source before agreeing a runtime triangle/texture budget. V1 remains installed and unchanged. No runtime installation, engine edits, shared-tool edits, commit or push was performed.

Recommended next stage after appearance feedback: accessory rigging/deformation checks, then a proper running pose cycle from the rig. Later export static OBJ frames with shared PNG, review in the engine, and obtain runtime-installation approval.
