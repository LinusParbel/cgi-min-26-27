# Kr?pcke key facade overlay

Two complete world-coordinate building finishes, with architectural geometry measured from licensed historical photos. Source shells ensure the grey LoD2 surfaces remain behind opaque materials. No brands, advertising, photograph pixels, alpha, or normal maps.

- Magis corner: building_0307, ID_70b50309-6ff3-339a-86ff-888669208df5. Source dimensions 27.39 ?24.65m bbox; podium7.63m, mainwall22.92m, narrow highwing27.89m. Four continuous upper window ribbons, cream bands, glazed stair drum and rounded corner interpreted from2014photo. Exact current frontage and hidden returns are not verified.
- Kr?pcke-Center: building_0271, ID_0a25725c-24e1-3239-8d49-0b0bb20eb212. Source footprint4368.4m?. Rebuilt facade29.1m high, five upper window rows and doubleheight ground glazing, pale limestone piers. Source2010 main walls22.57m predate redevelopment2009?2013; the new closed envelope deliberately supersedes that outdated height.

## Runtime

Copy only `out/KroepckeFacades.obj`, `.mtl`, `.png`, `_parts.json` together. Add `KroepckeFacades_parts.json` to map `extraManifests`. Pivot remains zero; vertices already aligned to X=E?550000, Z=5803000?N, groundY=?1. Do not recenter or rotate. City source ground height is normalized independently per building exactly as hannover_public_realm.

## Reproduce and inspect

`python RunnerGame/Art/assets/kroepcke_facade_details/build.py`

`python RunnerGame/Art/assets/kroepcke_facade_details/verify.py`

`blender --background --factory-startup --python-exit-code 1 --python RunnerGame/Art/assets/kroepcke_facade_details/preview.py`

Generator uses Python,numpy,Pillow,lxml and existing local Shapely dependencies. No bake or image downloads. Blender preview uses8threads24samples and writes editable blend plus three-quarter views. Engine preview is parent integration work.

## Known differences

Magis round corner joins a continuous outside skin projecting about2m from the source parcel boundary on two visible sides; this is an interpreted architectural replacement envelope, not a claim that the official footprint contains that curve.

Photo03/04 are2014, source LoD2 is2010; this is a photo-informed architectural reconstruction, not a surveyed2026 replica. Magis facade proportions remain constrained by the old parcel envelope; rounded skin2.04m radius and stairdrum1.68m radius are interpreted additions. Its unphotographed returns continue the known ribbon treatment. Center2014 six-storey facade takes precedence over obsolete source wallheight. Source rooftop configuration on Magis is retained, so its rear silhouette differs from photo04. No fit RMS claim is made: the source and photos depict different epochs, and exact camera fitting would falsely imply surveyed correspondence.

`verification.json` proves indices, finite coordinates/normals/UVs, opaque atlas, winding, nondegenerate triangles, ground contact and budget. `spec.json`, `wall-measurements.json`, labeled grids and `refs.json` document measurement/provenance.
