# Navy commuter bicycle - reference-model continuation

Continues the existing Batavus Blockbuster Plus photo set and replica-level
specification (25,000 triangle ceiling, 2048-square export atlas, front Blender -Y).
The intended game asset is a recognisable Dutch-style city commuter bicycle:
thin wire spokes, diamond frame, full mudguards, enclosed chaincase, swept chrome
handlebar, black comfort saddle, front cargo rack with tall back and rear carrier.
Wheels remain separate with their origins on their axles for later rotation.

## Measurements and limits

`ref/04.jpg` is the main side reference and `ref/03.jpg` supplies depth/rack detail.
`measure_reference.py` records pixel landmarks, removes the small axle-line roll
and updates `spec.json` and `refs.json`. `measurement_notes.json` records the
conversion. The pre-existing 1.08 m wheelbase is an assumed ruler, not a verified
manufacturer measurement. Most transverse widths and obscured fittings are
inferred. This is a photo-based interpretation, not a measured factory replica.
The saddle and paint values correct the earlier brown/bright-blue placeholders.

`checkpoints/before_photo_build_*.json` preserve the previous specifications.
The old `bike_bushido.glb`, `pybullet/`, assembly script and their preview images
remain untouched exploratory imports. Their geometry is not used in the new
photo-based build; no redistribution/licensing claim is made for those files.

## Provenance

The six reference images are recorded as public domain, by Phillip, with source
links in `refs.json`; see the bicycle section of `RunnerGame/CREDITS.md`. They are
used to observe shapes and colours. No photographic pixels are used in textures.
New geometry is built locally from the measured specification. No paid service
or external 3D generator is used.

## Review boundary

Source shape approved on 2026-10-20. `out/` now contains checked body and two
axle-centered wheel OBJs with one opaque 2048 atlas. Applied bevels bring the
actual export to 15,720 triangles (body 7,680; wheels 4,020 each); the editable
source geometry check reports 15,240 before applied export modifiers. Both fit
the 25,000 ceiling. `check_export.py` verifies actual indices, normals, UVs,
nondegenerate triangles, pivots, floor and atlas opacity. Independent read-only
review passed all six engine views and actual files with no blocking issues.
Thin spokes/cables alias at small screen sizes. This is a still-asset review;
wheel animation and gameplay integration have not been tested or implemented.

Deliverables: `bike_commuter_game_pack.zip`, `bike_commuter_editable_source.zip`,
`previews/engine_review.jpg`. `package_export.py` rebuilds and CRC-checks the ZIPs.
Baked engine view approved and runtime installed on 2026-10-20 in
`RunnerGame/Assets/Models/Fahrzeug/BikeCommuter/`. Five runtime files match export
SHA-256 hashes; evidence is in `previews/runtime_installation.json`. Wheels are
ready for rotation, but gameplay animation/placement remains unimplemented.

First review the frame, wheel and rack silhouette against both key photographs.
Then finish details and export one shared atlas plus body/front-wheel/rear-wheel
OBJ files. Review the baked engine result before runtime installation. No engine
or shared library changes are part of this model work. No commit/push is implied.
