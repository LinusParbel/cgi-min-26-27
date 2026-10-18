# Free, redistributable 3D asset sources and provenance documentation for "Hannover Rush Hour"

Research date: 2026-10-16. "Verified" means: checked on the live source page or, for Kenney, by downloading the actual ZIP and listing / reading its files (License.txt, OBJ, MTL, PNG). Engine reminder: our `ObjLoader` reads `v`/`vt`/`vn`/`f` only (extra `v x y z r g b` vertex-colour fields and `g`/`usemtl` lines are simply ignored — checked in `Engine/Geometry/Loaders/ObjLoader.cs`), `.mtl` is ignored, so one OBJ = one mesh = one texture.

## Kenney kits (City Kit Roads / Commercial / Suburban / Industrial, Car Kit, Train Kit, Mini Skate, Mini Characters, Platformer Kit, Modular Buildings, Retro Urban Kit)

### Takeaway
Kenney is the best fit for our engine: every kit checked is CC0, ships OBJ + FBX + GLB, and (except Retro Urban Kit) every OBJ uses one material `colormap` pointing to a single shared 512×512 `Textures/colormap.png` palette — exactly the "one OBJ + one PNG" our engine needs, with no Blender work required to get a first render. Kenney even has a modern tram, a scooter, static characters, coins, traffic cones, construction barriers, delivery vans and a garbage truck.

### Cited Findings
**License (all kits)**
- Kenney support page: "all game assets on the asset pages are public domain licensed (CC0)"; usable commercially; credit not required, but the Kenney logo must not be used — [Kenney Support](https://kenney.nl/support)
- `License.txt` inside the City Kit Roads 2.2 ZIP (creation date 10-10-2026): "License: (Creative Commons Zero, CC0) http://creativecommons.org/publicdomain/zero/1.0/ … You can use this content for personal, educational, and commercial purposes. Support by crediting 'Kenney' or 'www.kenney.nl' (this is not a requirement)" — [City Kit Roads ZIP](https://kenney.nl/media/pages/assets/city-kit-roads/74288c9459-1791628607/kenney_city-kit-roads.zip) (downloaded and inspected)
- Each asset page states "Creative Commons CC0" — [City Kit Roads](https://kenney.nl/assets/city-kit-roads), [City Kit Commercial](https://kenney.nl/assets/city-kit-commercial), [City Kit Suburban](https://kenney.nl/assets/city-kit-suburban), [Car Kit](https://kenney.nl/assets/car-kit)
- The asset web pages do NOT list file formats or contents; those facts below come from downloading the ZIPs.

**Formats and texture approach (verified from ZIPs)**
- Every kit checked has `Models/FBX format/`, `Models/GLB format/`, `Models/OBJ format/` folders; the OBJ folder contains `Textures/colormap.png` (512×512) and every inspected `.mtl` is just `newmtl colormap / Kd 1 1 1 / map_Kd Textures/colormap.png` — City Kit Roads, City Kit Commercial 2.1, City Kit Suburban 2.0, Car Kit, City Kit Industrial 2.0, Train Kit, Mini Characters, Mini Skate, Platformer Kit, Modular Buildings (ZIPs from the respective kenney.nl asset pages)
- OBJ vertices are written as `v x y z 1 1 1` (with trailing vertex colours, all white); the `construction-cone.obj` has only 4 `vt` entries — i.e. UVs point at flat colour swatches in the palette texture (inspected file inside [City Kit Roads ZIP](https://kenney.nl/media/pages/assets/city-kit-roads/74288c9459-1791628607/kenney_city-kit-roads.zip))
- Car Kit OBJs contain several groups (e.g. `delivery.obj`: `door`, `wheel-front-right`, `wheel-front-left`, `wheel-back-right`, `wheel-back-left`, `body`) but all use the single `colormap` material; `delivery.obj` = 2,476 faces — [Car Kit ZIP](https://kenney.nl/media/pages/assets/car-kit/1a312ec241-1775131960/kenney_car-kit.zip)
- Exception: Retro Urban Kit OBJ folder has 23 separate textures (`asphalt.png`, `bars.png`, `concrete.png`, `dirt.png`, `doors.png`, …), so models there are not single-palette — [Retro Urban Kit](https://kenney.nl/assets/retro-urban-kit)

**Contents relevant to us (OBJ names, verified from ZIPs)**
- City Kit Roads (v2.2, page lists "90×" files; 98 models): `construction-barrier`, `construction-cone`, `construction-fence`, `construction-light`, `dumpster`, `light-curved`, `light-curved-double`, `light-curved-cross`, `light-square(-double/-cross)` (street lamps), `traffic-light`, `traffic-light-hanging`, `road-sign-stop/street/warning`, `road-straight`, `road-straight-half`, `road-crossing`, `road-intersection`, `road-side`, `road-bridge`, `tile-low/high/slant`, `electricity-pole*`, `sign-highway*` — [City Kit Roads](https://kenney.nl/assets/city-kit-roads)
- City Kit Commercial (v2.1, "Fixed problem skyscraper E"): `building-a`…`building-n`, `building-skyscraper-a`…`e`, `low-detail-building-a`…`n`, `low-detail-building-wide-a/b`, `detail-awning(-wide)`, `detail-overhang(-wide)`, `detail-parasol-a/b`; extra `Models/Textures/variation-a.png`, `variation-b.png` colour variants — [City Kit Commercial](https://kenney.nl/assets/city-kit-commercial)
- City Kit Suburban (v2.0 "Completely remade"): `building-type-a`…`u`, `fence*`, `driveway-*`, `path-*`, `planter`, `tree-large`, `tree-small`; variations a/b/c textures — [City Kit Suburban](https://kenney.nl/assets/city-kit-suburban)
- Car Kit (v3.1, first released 2022): `ambulance`, `delivery`, `delivery-flat`, `van`, `truck`, `truck-flat`, `garbage-truck`, `firetruck`, `police`, `taxi`, `sedan`, `sedan-sports`, `hatchback-sports`, `suv`, `suv-luxury`, `tractor*`, `race*`, karts, `cone`, `cone-flat`, `box`, `debris-*`, `wheel-*` — [Car Kit](https://kenney.nl/assets/car-kit)
- Train Kit: `train-tram-modern`, `train-tram-classic`, `train-tram-round`, `train-electric-city-a/b/c`, `train-electric-subway-a/b/c`, plus rails/track pieces. Preview of `train-tram-modern` shows a modern low-floor tram with pantograph (only a 64 px preview was inspected) — [Train Kit](https://kenney.nl/assets/train-kit)
- Mini Skate: `scooter` (preview looks like a kick scooter, 820 faces, single group), `character-skate-boy`, `character-skate-girl` (OBJ groups `body-mesh` + `head-mesh`, ~722 faces, ~0.78 units tall), `bench`, `benches`, `fence`, `ramp`, `skateboard` — [Mini Skate](https://kenney.nl/assets/mini-skate)
- Mini Characters: `character-female-a`…`f`, `character-male-a`…`f` (OBJ = `body-mesh` + `head-mesh`, 723 faces), accessories (`aid-glasses`, `aid-sunglasses`, …), wheelchairs — [Mini Characters](https://kenney.nl/assets/mini-characters)
- Platformer Kit: `coin-gold`, `coin-silver`, `coin-bronze`, `star`, `heart`, `jewel`, `key` (collectibles) — [Platformer Kit](https://kenney.nl/assets/platformer-kit)
- Modular Buildings: facade pieces (`building-window*`, `building-door*`, `building-corner*`, `roof-flat-*`, `roof-gable*`, `detail-ac-a/b`, `door-*`) and sample houses/towers — [Modular Buildings](https://kenney.nl/assets/modular-buildings)
- City Kit Industrial 2.0: `building-a`…`t`, `chimney-*`, `shipping-container-a/b/c`, `detail-tank*`, `water-tower`, `solar-panel-*` (one mtl has a `colormap-specular` second material but same PNG) — [City Kit Industrial](https://kenney.nl/assets/city-kit-industrial)
- Full list of Kenney 3D kits (category pages) includes also `3d-road-tiles`, `building-kit`, `fantasy-town-kit`, `furniture-kit`, `mini-market`, `nature-kit`, `racing-kit`, `toy-car-kit`, `blocky-characters` — [Kenney 3D assets](https://kenney.nl/assets/category:3D)

### Inferences
- Kenney OBJ + `colormap.png` should load in our engine unchanged (load OBJ with `ObjLoader`, load `colormap.png` with `Texture.FromFile`, use the textured lit material). One colormap texture can be shared by all Kenney meshes from the same kit (and likely across kits — not verified that all colormaps are identical; compare files before sharing).
- Because UVs map to palette swatches, recolouring (e.g. tram to ÜSTRA green-silver, bins to Hannover colours) can be done by painting a modified copy of `colormap.png` or moving UVs in Blender — a cheap, gradeable "modification".
- Wheelie bin is NOT in the Kenney kits checked (only `dumpster`); a wheelie bin is a good from-scratch model.
- Kenney characters are low-poly "mini" style (≈0.8 m tall at 1 unit = 1 m); scale/pose adjustments needed. OBJ is static by nature, so rigging in FBX/GLB is irrelevant.

### Gaps
- Exact rest pose of Mini Skate / Mini Characters OBJs (T-pose vs. standing) was not visually verified (only 64 px previews). Whether a character can be posed on the scooter needs a Blender check.
- Did not verify that colormap.png files are byte-identical across kits.

## Quaternius packs

### Takeaway
All Quaternius packs are CC0 (no attribution required), offered as FBX/OBJ/Blend (newer MegaKits: FBX/Blend/glTF). But the city-relevant packs (Modular Streets, Public Transport, Cars) are marked "Textured: ✗" — they use per-material flat colours, which our engine cannot show (it ignores `.mtl`), so each model must be baked/re-UV'd to a palette PNG in Blender before use.

### Cited Findings
- FAQ: all models are CC0; credit appreciated but not required; free for commercial, educational and personal use and may be modified; formats Blend and FBX; "most" packs use a single Atlas Texture (image with coloured squares), some use individual materials — [Quaternius FAQ](https://quaternius.com/faq.html). The FAQ does not explicitly mention redistribution or vertex colours.
- Modular Streets Pack: 25 models, Animated ✗, Textured ✗, Formats FBX OBJ Blend, License CC0 — [Modular Streets](https://quaternius.com/packs/modularstreets.html)
- Public Transport Pack: 12 models, Textured ✗, FBX OBJ Blend, CC0 — [Public Transport](https://quaternius.com/packs/publictransport.html)
- Cars Pack: 8 models, Textured ✗, FBX OBJ Blend, CC0 — [Cars](https://quaternius.com/packs/cars.html)
- Ultimate (Textured) Buildings Pack: 76 models, Textured ✓, FBX OBJ Blend, CC0 — [Ultimate Buildings](https://quaternius.com/packs/ultimatetexturedbuildings.html)
- Buildings Pack (9 models), Simple Buildings (10), Simple Nature (13), Modular Train (15), Background Posed Humans (28 static posed people) — all FBX OBJ Blend, CC0 — [Buildings](https://quaternius.com/packs/buildings.html), [Simple Buildings](https://quaternius.com/packs/simplebuildings.html), [Simple Nature](https://quaternius.com/packs/simplenature.html), [Modular Train](https://quaternius.com/packs/modulartrain.html), [Background Posed Humans](https://quaternius.com/packs/backgroundposedhumans.html)
- Downtown City MegaKit: 315 modular pieces for "Boston/NYC style city blocks", Textured ✓, Formats FBX Blend glTF, CC0; "60-70% of my pack is completely free" (Standard), the paid Source version adds engine projects, a fake-window-interior shader and "vertex color controlled wear"; download via site or itch.io — [Downtown City MegaKit](https://quaternius.com/packs/downtowncitymegakit.html)
- Full pack index (includes many animated/rigged character packs that are useless to us) — [Quaternius](https://quaternius.com/)

### Inferences
- "Background Posed Humans" (static posed figures, CC0) is the most promising Quaternius source for a static rider/pedestrians, but contents/poses were not inspected.
- Downtown City MegaKit is US-style (Boston/NYC) and partly paywalled; less suitable for Hannover look than Kenney.
- Quaternius flat-colour models need a Blender "bake material colours to a palette texture" step — a manageable but real extra task for beginners.

### Gaps
- Exact contents of Public Transport (whether it includes a tram/bus) and the texture setup of each pack's OBJ (multi-material vs atlas) were not downloaded/verified (downloads go through site buttons/itch.io).

## Poly Pizza, Poly Haven, ambientCG, OpenGameArt, Sketchfab, itch.io, Synty

### Takeaway
Poly Haven and ambientCG are CC0 (textures/HDRIs, Poly Haven also models) — ideal for asphalt/cobblestone/brick PNGs. Poly Pizza mixes CC0 and CC-BY 3.0 per model (license shown on each model page). Sketchfab has many CC-BY models (attribution + "changes indicated" required) but its Standard / Free Standard / Editorial licenses forbid redistributing raw files, so they cannot go into a public repo. Synty's EULA forbids sharing source files outside the team — not usable in a public repo.

### Cited Findings
- Poly Haven: HDRIs, textures and 3D models are CC0; no credit needed; "can redistribute them"; logos, example renders, user renders and site text are NOT CC0; scraping/data mining prohibited — [Poly Haven License](https://polyhaven.com/license)
- ambientCG: all assets (and preview renders) under CC0 1.0 Universal; may include raw files in e.g. a video game; credit optional, suggested text "Created using <asset name> from ambientCG.com, licensed under the Creative Commons CC0 1.0 Universal License." — [ambientCG License](https://docs.ambientcg.com/license/)
- Poly Pizza ToS: downloaded models fall under "the Creative Commons license that applies at the time of download"; Poly Pizza claims no ownership; scraping/ML extraction forbidden — [Poly Pizza ToS](https://poly.pizza/docs/tos)
- Sample of 25 Poly Pizza model pages (searches tram, scooter, trash can, traffic cone, street lamp): CC-BY 3.0 models offered OBJ + GLTF downloads; CC0 1.0 ("Public Domain") models offered FBX + GLTF — e.g. [tram result](https://poly.pizza/m/0ivy-FxYrz9), [scooter result](https://poly.pizza/m/0lBe-ApqJs4), [trash can result](https://poly.pizza/m/02uQ-GYZm1k), [CC0 traffic cone](https://poly.pizza/m/4mrO9ueiQr), [CC0 street lamp](https://poly.pizza/m/0lxF8Dl1jU). Third-party credits commonly cite "Poly by Google [CC-BY] via Poly Pizza" — [search summary](https://alternativeto.net/software/poly-pizza/about/) (secondary)
- OpenGameArt allows CC0, CC-BY 3.0/4.0, CC-BY-SA 3.0/4.0, OGA-BY 3.0/4.0, GPL 2.0/3.0; check each asset's "Copyright/Attribution Notice"; CC-BY-SA derivatives must use the same license; cites FSF view that game code and media are separate and need not share a license — [OpenGameArt FAQ](https://opengameart.org/content/faq)
- Sketchfab Standard license: you may not distribute the asset as a standalone file or make it available for third parties to download/extract (2.2(b), 2.2(h)); Editorial adds no commercial/promotional use — [Sketchfab Licenses](https://sketchfab.com/licenses). The API lists a "Free Standard" label on some free downloads (e.g. [Electric Scooter by assetfactory](https://sketchfab.com/3d-models/6e0e699c36e140608c58b2d4489b39ab)), which is a Standard-type license, not CC.
- Sketchfab auto-converts every downloadable model to glTF/GLB and USDZ in addition to the original upload format; login required to download — [Sketchfab glTF/GLB/USDZ help](https://help.sketchfab.com/en/articles/16152669-gltf-glb-and-usdz), [Sketchfab glTF](https://www.sketchfab.com/features/gltf), [download guide](https://www.digitalcitizen.life/how-to-download-sketchfab-models/) (secondary)
- Synty EULA: "You must not share the source files of any Assets outside your team"; no open-source exception; "Asset" definition includes free downloads — [Synty EULA](https://syntystore.com/pages/end-user-licence-agreement)

### Inferences
- For a public GitHub repo: CC0 (Kenney, Quaternius, Poly Haven, ambientCG, CC0 Poly Pizza) is safest; CC-BY is fine with proper attribution; CC-BY-SA is usable but our modified version must be CC-BY-SA too; Sketchfab Standard/Free Standard/Editorial and Synty are out.
- CC-BY Poly Pizza models (mostly ex-Google Poly) come as OBJ — convenient, but usually multi-material flat colours → bake to one PNG.
- Sketchfab models must be converted from glTF/FBX to OBJ in Blender and often have high poly counts and PBR texture sets.

### Gaps
- itch.io free 3D packs were not researched individually (licenses vary per pack; must be checked per page). A search hit "Cartoon City Free" by ithappy (cars incl. delivery van, OBJ/FBX/glTF) on [Superhive](https://superhivemarket.com/products/cartoon-city-free) — license not verified.
- Poly Pizza model titles/authors in the sample were not recorded; the per-format pattern (CC-BY→OBJ, CC0→FBX) is from a 25-page sample only.

## Specific items: e-scooter, Hannover tram, wheelie bin, Kröpcke clock, Neues Rathaus, Marktkirche, rider

### Takeaway
Nothing downloadable exists for the ÜSTRA TW2000/TW3000, the Kröpcke-Uhr or the Neues Rathaus as standalone models. CC-BY models exist for the Marktkirche (122k faces), the historic Kröpcke station, e-scooters, wheelie bins, a static scooter rider and stylized coins on Sketchfab. The City of Hannover publishes an official LoD1/LoD2 city model (all buildings incl. Rathaus/Marktkirche as block/roof shapes) under CC BY 4.0 — usable as a proportion reference or blockout. Recommendation: build Kröpcke clock, tram livery and Rathaus silhouette ourselves.

### Cited Findings (Sketchfab facts from the public Sketchfab API v3, `downloadable=true`, checked 2026-10-16)
- Marktkirche Hannover by ishan.bs2015, CC BY 4.0, 122,001 faces, no animation — [Sketchfab](https://sketchfab.com/3d-models/marktkirche-hannover-e63339930f074de1a1100cb24ad747c6)
- "Train Station Hannover Georgstraße / Kröpcke" (from around 1950) by tryfield, CC BY 4.0, 22,155 faces — [Sketchfab](https://sketchfab.com/3d-models/train-station-hannover-georgstrae-kropcke-7dccdd36c4a54032ab560cb54358edff)
- "City Model for Hannover" by QuintusHortensiusHortalus, CC BY 4.0, 16,267 faces; made for the Empire: Total War mod Imperial Splendour, historical/demolished buildings — [Sketchfab](https://sketchfab.com/3d-models/city-model-for-hannover-c9c365fe37ff425fa31dec79bc3b8a67)
- Searches "kröpcke", "kropcke uhr", "neues rathaus", "new town hall hanover", "tw3000", "üstra", "hanover tram", "mülltonne" returned no relevant downloadable model (Sketchfab API); web search found no downloadable TW2000 model — [TW 2000 Wikipedia](https://en.wikipedia.org/wiki/TW_2000) (TW 2000: 25.82 m long, 2.65 m wide, design Herbert Lindinger / Jasper Morrison), [hannover.de TW 2000/2500](https://www.hannover.de/Leben-in-der-Region-Hannover/Mobilität/Bus-Bahn/Angebot-Infrastruktur/Stadtbahn/Fahrzeugtypen/TW-2000-2500)
- A Cities: Skylines Workshop asset "New Town Hall_hannover" exists (Steam Workshop, not a redistributable license) — [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/comments/1177221309)
- Hannover official 3D city model: license "Creative Commons Namensnennung 4.0 DE" (CC BY 4.0), publisher "Landeshauptstadt Hannover, FB Planen und Stadtentwicklung, Bereich Geoinformation"; LoD1 (block model) and LoD2 (standardised roof shapes, ±1 m) in CityGML 2.0 and DWG; tiled 1×1 km; downloads e.g. [CityGML LOD2 ZIP, 307 MB](https://opengeodata.hannover-stadt.de/Stadtmodell_Hannover_CityGML_LOD2.zip) — [hannover.de Digitales 3D-Stadtmodell](https://www.hannover.de/Leben-in-der-Region-Hannover/Verwaltungen-Kommunen/Die-Verwaltung-der-Landeshauptstadt-Hannover/Dezernate-und-Fachbereiche-der-LHH/Stadtentwicklung-und-Bauen/Fachbereich-Planen-und-Stadtentwicklung/Geoinformation/Open-GeoData/3D-Stadtmodell-und-Geländemodell/Digitales-3D-Stadtmodell)
- E-scooters (all CC BY 4.0): "e scooter" by Artbor, 1,368 faces, low poly made in Blockbench — [Sketchfab](https://sketchfab.com/3d-models/e-scooter-93a1f690e9054236adf53cbf79facb1b); "Electric Scooter (Low-poly, game-ready)" by delandi, 16,469 faces, 4K Substance textures — [Sketchfab](https://sketchfab.com/3d-models/electric-scooter-low-poly-game-ready-e22bffc784b04a93acc83599fa7a81c0); "Electric Scooter" by gestLT, 2,356 faces — [Sketchfab](https://sketchfab.com/3d-models/f3785071e9244d83ba311b7da48a1085); "Tier scooter" by niilo.poutanen, 83,323 faces — [Sketchfab](https://sketchfab.com/3d-models/9479a6d3f1474971afde26b33fe96c55)
- Rider: "Female Scooter Rider" by novusod, CC BY 4.0, 5,712 faces, 0 animations — [Sketchfab](https://sketchfab.com/3d-models/female-scooter-rider-8dee814d538b45b38798ebdb4352903d); "Scooter girl" by novusod, CC BY, 3,798 faces — [Sketchfab](https://sketchfab.com/3d-models/c6a685414b6d488989e86161a7761891)
- Wheelie bins: "Wheelie bin" by 1-3D.com, CC BY-SA 4.0, 1,422 faces, originally by Ola-Kristian Hoff (Sweet Home 3D) — [Sketchfab](https://sketchfab.com/3d-models/wheelie-bin-81e273d7b3fe438a89a7a25dd0903b07); "wheelie bin game asset" by sameegh779, CC BY 4.0, 6,962 faces (Cape Town style) — [Sketchfab](https://sketchfab.com/3d-models/wheelie-bin-game-asset-390046444cab4de0b668fe702269b5c1); "Wheelie bin, 240 liters, green" by villekroger is CC BY-NC and 711k faces (avoid) — [Sketchfab](https://sketchfab.com/3d-models/fc11d27f62e445229c12f2321d081647)
- Trams: "Low-Poly Tram Downloadable" by robinmikart, CC BY 4.0, 16,186 faces — [Sketchfab](https://sketchfab.com/3d-models/low-poly-tram-downloadable-adb5b3fc0d774e7d82060a319d5d9705); "Siemens & Halske Tw3 electric tram" (historic German), CC BY 4.0, 2,234 faces — [Sketchfab](https://sketchfab.com/3d-models/siemens-halske-tw3-electric-tram-24e817989ee9427aa28af0c5eaef7957); "Low Poly Tram" by nathramn is CC BY-NC — [Sketchfab](https://sketchfab.com/3d-models/2012f3a22b994ef4b98430d5ed8b310e); plus Kenney `train-tram-modern` (CC0, see Kenney section)
- Coins: "Stylized Coin" by barracudabyte, CC BY 4.0, 436 faces — [Sketchfab](https://sketchfab.com/3d-models/stylized-coin-8cd6f95c44994ed5944a42892d0ffc10); "Low poly gold Coin" by michal.zawadzki, CC BY, 220 faces — [Sketchfab](https://sketchfab.com/3d-models/4acf042acbfd448fa74ee233ebff6e31); Kenney `coin-gold` (CC0)

### Inferences
- Best path: Kenney `train-tram-modern` recoloured/reshaped toward the TW2000/TW3000 look (or modelled from scratch from photos — a box-modelling task suited for beginners); Kröpcke clock and Neues Rathaus silhouette as our own models (great "own model" showcase); Marktkirche CC-BY model is too dense (122k faces) — use as reference or decimate heavily, or model a simplified tower ourselves.
- The Hannover LoD2 CityGML would need a CityGML→OBJ conversion step (tooling not researched); probably more effort than modelling simplified facades, but valuable for correct proportions of Kröpcke/Rathaus surroundings. It requires CC BY attribution to Landeshauptstadt Hannover.
- Rigged characters are useless; candidates for a static rider are Kenney Mini Skate / Mini Characters (CC0, palette texture), Quaternius Background Posed Humans (CC0, unverified poses), novusod's Female Scooter Rider (CC BY).

### Gaps
- Sketchfab models were not downloaded; texture setup, scale and actual pose of the rider models are unverified. Sketchfab search UI might show more results than the API queries used.
- No search was done on CGTrader/TurboSquid free sections (licenses there usually forbid raw redistribution — not verified).

## License compatibility for a public GitHub repo (CC0 vs CC-BY vs CC-BY-SA vs CC-BY-NC vs Sketchfab Standard/Editorial)

### Takeaway
CC0 = no conditions. CC BY 4.0 = allowed, but you must credit, link the license and indicate changes (and keep earlier change notes). CC BY-SA = allowed, but our modified asset must be released under BY-SA too (code is unaffected). CC BY-NC = legally arguable for a non-commercial university project but risky for a public repo (anyone can fork it) — avoid. Sketchfab Standard / Free Standard / Editorial and Synty = no raw-file redistribution → cannot be committed.

### Cited Findings
- CC BY 4.0 deed: give "appropriate credit", provide a link to the license, and "indicate if changes were made"; any reasonable manner but not implying endorsement; "In 4.0, you must indicate if you modified the material and retain an indication of previous modifications"; if supplied, provide creator name and attribution parties, copyright notice, license notice, disclaimer notice, link to material; no additional restrictions — [CC BY 4.0 deed](https://creativecommons.org/licenses/by/4.0/)
- CC BY-NC 4.0: no use "primarily intended for commercial advantage or monetary compensation" — [CC BY-NC 4.0 deed](https://creativecommons.org/licenses/by-nc/4.0/)
- CC BY-SA on OpenGameArt: "If you make derivative works, you must distribute them under the same license"; game code and media are separate entities per FSF — [OpenGameArt FAQ](https://opengameart.org/content/faq)
- Sketchfab Standard/Editorial: no standalone redistribution / third-party download — [Sketchfab Licenses](https://sketchfab.com/licenses)
- Synty: source files must not be shared outside the team — [Synty EULA](https://syntystore.com/pages/end-user-licence-agreement)
- CC0 sources (Kenney, Quaternius, Poly Haven, ambientCG) state attribution is optional — [Kenney Support](https://kenney.nl/support), [Quaternius FAQ](https://quaternius.com/faq.html), [Poly Haven License](https://polyhaven.com/license), [ambientCG License](https://docs.ambientcg.com/license/)

### Inferences
- "Modified" under CC BY: any change to the work (remesh, decimation, recolouring, re-UV, merging, format conversion arguably too) — record it in the credits ("modified: decimated to 2k tris, recoloured, baked to palette texture"). Format conversion alone is likely treated as a minor change; noting it costs nothing.
- Keep CC-BY-SA assets in a clearly separated folder with their own license note so it is obvious the SA obligation applies only to those files, not to the code.
- Policy suggestion for the team: allow CC0, CC-BY, (CC-BY-SA only if needed); forbid NC, ND (cannot modify, conflicts with "we modify assets"), Sketchfab Standard/Free Standard/Editorial, Synty, "free for personal use" packs.

### Gaps
- No university- or course-specific policy on NC material was found; ask the lecturer if an NC asset is ever wanted.
- CC BY 3.0 (common on Poly Pizza) differs slightly from 4.0 (3.0 required change-indication only for adaptations) — the full 3.0 legal code was not fetched.

## Best practice for documenting provenance (asset register, CREDITS file, original vs modified vs unmodified)

### Takeaway
Use TASL (Title, Author, Source, License) per asset, plus modification notes; keep a machine-readable register (CSV/markdown table) and a human-readable CREDITS/ATTRIBUTION file, and credit CC0 assets too (recommended, not required). Mark each asset as original / modified third-party / unmodified third-party, and keep before/after screenshots for the grading of own models.

### Cited Findings
- CC best practice: TASL — Title, Author (as the licensor wants to be credited), Source (link to original page, not shortened), License (named and linked, e.g. CC BY 4.0); good example: '"Creative Commons 10th Birthday Celebration San Francisco" by Timothy Vollmer is licensed under CC BY 4.0'; bad: "Photo: Creative Commons" — [CC Best practices for attribution](https://wiki.creativecommons.org/wiki/Best_practices_for_attribution)
- For small changes note them ("Cropped from original"); for adaptations credit the original with full TASL, state the work is adapted, and add your own attribution/license ('This work, "90fied", is adapted from …'); ND licenses forbid adaptations — [CC Best practices for attribution](https://wiki.creativecommons.org/wiki/Best_practices_for_attribution)
- For CC0, attribution is not legally required but recommended, e.g. '"The Milkmaid" by Vermeer. The Rijksmuseum collection. The image is dedicated to the public domain under CC0.'; pitfalls: attribution only in metadata/alt text, crediting the platform instead of the author — [CC Best practices for attribution](https://wiki.creativecommons.org/wiki/Best_practices_for_attribution)
- OpenGameArt suggests a credits entry with asset name, author, license and URL, honouring the artist's own "Copyright/Attribution Notice" — [OpenGameArt FAQ](https://opengameart.org/content/faq)
- ambientCG's suggested credit line format — [ambientCG License](https://docs.ambientcg.com/license/); Kenney asks to credit 'Kenney' or 'www.kenney.nl' (optional) and not use its logo — [Kenney Support](https://kenney.nl/support)

### Inferences (proposed templates — not from a source)
- Asset register `RunnerGame/Assets/ASSETS.csv` (or markdown table) columns: `file_path, asset_name, status (original|modified|unmodified), origin_title, author, source_url, license, license_url, download_date, source_pack_version, modifications, modified_by, made_by (for originals), tools, tri_count, texture, screenshot_before, screenshot_after, notes`.
- `CREDITS.md` entries, TASL + changes, e.g.:
  - `Tram body — based on "train-tram-modern" from Train Kit by Kenney (https://kenney.nl/assets/train-kit), CC0 1.0. Modified by <name>: lengthened, recoloured colormap to ÜSTRA livery.`
  - `"e scooter" by Artbor (https://sketchfab.com/3d-models/e-scooter-93a1f690e9054236adf53cbf79facb1b), licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Changes: converted glTF→OBJ, decimated, baked to single PNG.`
  - `Hannover building footprints/heights reference: 3D-Stadtmodell, Landeshauptstadt Hannover, FB Planen und Stadtentwicklung, Bereich Geoinformation, CC BY 4.0.`
- Keep the original `License.txt` from each pack next to the files (e.g. `Assets/ThirdParty/Kenney/CityKitRoads/License.txt`), and separate folders `Assets/Original/`, `Assets/ThirdParty/` (unmodified), `Assets/Modified/`.
- Before/after: keep the untouched downloaded file (or its URL+version) plus a screenshot of the original and of our version in `docs/asset-screenshots/`; for own models, save the `.blend` and progress screenshots as proof of authorship for grading.

### Gaps
- No authoritative university-specific standard for asset registers was found; the template above is a proposal.
