# Hannover Rush Hour: Map Sources, Licensing and Method

**Project:** University CGI runner game, C# / OpenTK course engine  
**Route prototype:** Hauptbahnhof / Ernst-August-Platz → Bahnhofstraße → Kröpcke → Georgstraße → Steintor  
**Documentation date:** 23 October 2026  
**Status:** Public-realm revision v2, 24 October 2026. Full pedestrian spaces replace the original narrow track. Two Kröpcke buildings have a first architectural-detail pass; the rest remains generalised massing. Current route is approximately **718.41 m**. This is unfinished work, not a survey-accurate or photorealistic reconstruction.

## Kurzfassung für die Projektvorstellung

Die Umgebung entsteht aus offenen Geodaten der Landeshauptstadt Hannover. Das amtliche LoD2-Stadtmodell liefert vorhandene Gebäudegeometrie und vereinfachte Dachformen. Georeferenzierte Luftbilder dienen zur Prüfung von Platzflächen und Wegeführung. Diese Daten werden nicht als eigene, vollständig selbst modellierte Gebäude ausgegeben. Unsere Arbeit umfasst Auswahl und Aufbereitung der Daten, Koordinatentransformation, Triangulierung, spielgerechte Wege- und Platzgestaltung, Integration in die eigene Engine sowie eigene bzw. separat lizenzierte Spielobjekte. Die Bearbeitung erfolgt mit dokumentierten, KI-unterstützt erstellten Skripten. Quellen, Lizenzhinweise und Änderungen werden nachvollziehbar festgehalten.

Das Drei-Spuren-Prinzip ist vorläufig: Es bezeichnet drei unsichtbare Steuerungspositionen, keine realen Fahrspuren. Es kann nach der ersten Erprobung durch eine andere Steuerung ersetzt werden. Die Fußgängerzone erhält keine aufgemalten Straßenmarkierungen.

## 1. Sources and how they are used

| Material | Publisher / creator | Licence | Role in this prototype |
|---|---|---|---|
| Digitales 3D-Stadtmodell, LoD2, CityGML 2.0 | Landeshauptstadt Hannover, Fachbereich Planen und Stadtentwicklung, Bereich Geoinformation | CC BY 4.0 International | Imported building massing, positions and generalised roof geometry. Adapted, not authored from scratch. |
| Digitale Orthophotos 2025, DOP20 | Same publisher | CC BY 4.0 International | Geographic reference for route layout, plazas and the sunken promenade. Reference images are kept separately; their pixels are not used in runtime textures. |
| Pedestrian paving, route specification and level geometry | Project-authored with script assistance | Project material; no new blanket licence is asserted by this document | Authored playable surfaces, route choices and simplified lower-level features. |
| Existing clock, rider, scooter and props | Mixed original/adapted project assets | See per-asset records | Reused with their existing provenance and attribution. This document does not replace their licences. |
| User-supplied annotated Google aerial screenshots | Google and its suppliers; red annotations supplied by user | Scope reference only; not redistributed | Inspected to understand the requested full area. Geometry measurements use official licensed data instead; no Google-derived meshes, tracing or image pixels are shipped. |
| Street-level reference photographs, 2014 / 2019 / 2024 | ChristianSchd; Bernd Schwabe in Hannover, via Wikimedia Commons | CC BY-SA 3.0 / 4.0, per photograph | Architectural reference for window bands, limestone bays, tree rows and paving. Photo derivatives retain their licences and credits; no photo pixels in runtime textures. |
| OpenStreetMap | Not adopted for this blockout | Not applicable to current inputs | No OSM geometry is currently incorporated. If introduced later, its separate obligations must be recorded first. |

**Authoritative source pages:**

- [Hannover: Digitales 3D-Stadtmodell](https://www.hannover.de/Leben-in-der-Region-Hannover/Verwaltungen-Kommunen/Die-Verwaltung-der-Landeshauptstadt-Hannover/Dezernate-und-Fachbereiche-der-LHH/Stadtentwicklung-und-Bauen/Fachbereich-Planen-und-Stadtentwicklung/Geoinformation/Open-GeoData/3D-Stadtmodell-und-Gel%C3%A4ndemodell/Digitales-3D-Stadtmodell)
- [Hannover: Digitale Orthophotos 2025](https://www.hannover.de/Leben-in-der-Region-Hannover/Verwaltungen-Kommunen/Die-Verwaltung-der-Landeshauptstadt-Hannover/Dezernate-und-Fachbereiche-der-LHH/Stadtentwicklung-und-Bauen/Fachbereich-Planen-und-Stadtentwicklung/Geoinformation/Open-GeoData/Digitale-Orthophotos-DOP20/Digitale-Orthophotos-2025)
- [CC BY 4.0 licence](https://creativecommons.org/licenses/by/4.0/) and [German-language deed](https://creativecommons.org/licenses/by/4.0/deed.de)
- [Google geo-content guidelines](https://about.google/intl/en-GB_ALL/brand-resource-center/products-and-services/geo-guidelines/)

The city's wording “4.0 DE” links to the German-language deed of **CC BY 4.0 International**. It is not a separate Germany-ported 4.0 licence.

## 2. Licence handling and attribution

CC BY 4.0 allows reuse and adaptation, including redistribution, subject to its terms. Our delivery includes the provider, material title, source URL, licence URL and a description of our modifications. We retain supplied notices and do not imply that the city endorses the game. We do not apply additional restrictions to the licensed data that would prevent the reuse allowed by the licence.

Attribution for the adapted building model:

> Gebäudegeometrie: „Digitales 3D-Stadtmodell Hannover, LoD2“, Landeshauptstadt Hannover, Fachbereich Planen und Stadtentwicklung, Bereich Geoinformation. Lizenz: CC BY 4.0, https://creativecommons.org/licenses/by/4.0/. Quelle: amtliche Open-GeoData-Veröffentlichung der Landeshauptstadt Hannover. Bearbeitet für Hannover Rush Hour: räumliche Auswahl, Triangulierung, lokale Koordinaten, Normalisierung der Gebäude-Grundhöhen für eine ebene Spielfläche, einfarbige Darstellung und Engine-Export. Keine Unterstützung des Projekts durch die Datengeberin behauptet.

Attribution for the aerial reference material:

> Karten-/Luftbildreferenz: „Digitale Orthophotos 2025 (DOP20)“, Landeshauptstadt Hannover, Bereich Geoinformation. Lizenz: CC BY 4.0, https://creativecommons.org/licenses/by/4.0/. Bearbeitungen an Referenzdarstellungen: räumlicher Ausschnitt, gegebenenfalls Größenanpassung, Raster und Beschriftung. Keine Luftbildpixel in den Spieltexturen.

The complete source URLs appear above and in `RunnerGame/CREDITS.md`. Per-file hashes, retrieval details and archived publisher/licence pages accompany the source assets. Existing asset credits remain in force; a CC BY city source does not relicense unrelated art or the entire project.

## 3. Data age, accuracy and limitations

- The city describes the LoD2 source as based on a **2010 laser survey**, with metadata modification date **5 December 2024** and publication date **20 January 2026**. A recent publication date is not a new survey date.
- LoD2 uses generalised roof forms; the city states approximately **±1 m height accuracy**. It does not supply photographic street-level facades. Current shopfronts and station details require separate verification.
- The aerial source was photographed **6 March 2025**, published **20 January 2026**, at **20 cm ground resolution**. Our combined reference overview is resampled to **50 cm per pixel**; that is a derived image resolution, not the source survey resolution. Roof overhangs, trees, people and shadows can obscure the paving beneath them.
- Source position reference is **ETRS89 / UTM zone 32N, EPSG:25832**. Source building height reference is recorded separately as **DHHN92** in the source evidence. These are metre coordinates, not latitude/longitude.
- The blockout uses a flat playable height near the station as an explicit simplification. In the game copy, each building is shifted vertically so its minimum GroundSurface height meets the same plane. Footprints and heights relative to each building's base are retained; absolute roof elevations are consequently not preserved. Per-building shifts and original/derivative hashes are recorded. The promenade's **3 m depth** and guardrails are authored assumptions, not surveyed measurements.
- The initial building selection has **504 source building objects and 54,274 triangles**. Whole buildings intersecting the selected rectangle are retained; the count does not represent all of Hannover.

## 4. Reproducible processing

1. Download selected official archive entries; retain publisher and licence evidence, source IDs, checksums and retrieval metadata. Where HTTP ranges are used, verify each extracted entry against the archive CRC. Do not claim a hash of a full archive that was not downloaded completely.
2. Read CityGML polygon surfaces, preserve interior rings, and triangulate them. The initial conversion preserves 149 polygon holes rather than filling them accidentally.
3. Convert raw source geometry into a stable local frame: **X = Easting − 550000; Y_raw = source height − 55; Z = −(Northing − 5803000)**. Preserve this raw conversion separately. For the flat playable copy, apply **Y_game = source height − building_ground_min − 1**. Both the upper floor and the minimum base of each building are then at engine Y = −1. Metre scale and east/north positions remain unchanged. Export triangulated OBJ plus one original opaque grey texture; no aerial pixels are baked onto buildings.
4. Use georeferenced aerial reference to choose the upper pedestrian corridor beside the Niki-de-Saint-Phalle-Promenade, establish the Kröpcke turn and check that the route avoids buildings and open lower-level areas. The initial north-west proposal failed the clearance check against the supplied building/opening geometry. The candidate instead uses the south-east upper side; neither source building footprints nor the interpreted opening polygons were shrunk to make it fit. The failed proposal is retained as evidence.
5. Author simplified paving and lower-level geometry. Keep source-derived measurements separate from gameplay choices such as clearance, obstacle spacing and smoothing of turns.
6. Parameterise the route by travelled distance and local forward/right directions. Place rider, camera and obstacles in that frame, so turns do not require a straight, fictitious street.
7. Validate geometry, path clearance, route continuity, lane offsets and runtime file loading. Inspect the result in the actual course engine before adding recognisable facade details.

## 5. What is our contribution?

**Imported:** Official building surfaces and their source positions. These are credited as third-party geometry.

**Adapted and implemented:** Data extraction, clipping, triangulation, coordinate conversion, exporter/validation scripts, route parameterisation, camera and gameplay integration, performance choices and source documentation. Coding and procedural modelling are AI-assisted; this should be described openly in the project presentation.

**Authored or separately adapted:** Gameplay, route design, paving, simplified promenade, original props and the existing model collection. Their precise provenance remains in each asset folder and the central credits.

**Not claimed:** A manual reconstruction of every building, a complete city digital twin, photographic accuracy, surveyed promenade depth, current storefront accuracy, or a final validated pedestrian circulation plan.

## 6. Prototype decisions to evaluate

- Three invisible steering positions are a temporary experiment, spaced **1.5 m** apart. With the player's 0.3 m half-width, the full swept lateral corridor is **3.6 m** wide. There are no painted road lanes in the pedestrian zone.
- Distances and building positions remain geographically grounded at blockout stage; any later compression will be recorded explicitly.
- The pedestrian section uses pedestrian-zone hazards, not regular car/van traffic. A later street section can introduce traffic.
- The scooter offence motivates the proposed chase narrative. Current gameplay mechanics and any later introduction sequence are documented separately from real traffic rules.
- Shadows, facade identity, signage and pedestrians follow only after the path and camera have been reviewed.

## Evidence locations

- Building conversion: `RunnerGame/Art/assets/hannover_route/`
- Source evidence: `RunnerGame/Art/assets/hannover_route/evidence/` and `provenance.json`
- Source building IDs / bounds: `RunnerGame/Art/assets/hannover_route/buildings.json`
- Aerial reference processing: `.model-research/hannover_route_reference/`
- Route/ground blockout: `RunnerGame/Art/assets/hannover_pedestrian_blockout/` (created during this implementation)
- Existing asset register / attribution: `RunnerGame/Art/ASSETS.md` and `RunnerGame/CREDITS.md`
- Route sampling tests: `RunnerGame.RouteTests/`

## First candidate checks (23 October; retained for comparison)

The final route has 52 control points and a runtime length of **714.27637 m**. The independent Python approximation differs by less than one millimetre. Minimum sampled bend radius is **4.576 m**; neither of the two outer steering paths reverses through the bends. The full player corridor clears the supplied building footprints by at least **1.038 m**, the interpreted openings by **1.074 m**, and the approximate clock base by **5.598 m**. These checks validate this model configuration, not current real-world accessibility or survey accuracy.

The candidate contains 54,274 city triangles and 5,052 authored ground/detail triangles. Source holes, ground openings, OBJ indices, normals and complete playable-surface support are checked. A known blocked route is rejected as a negative fixture. The original source conversion remains unchanged. Current checks and hashes are retained alongside the candidate; the runtime renderer also loads the files successfully.

The blockout keeps metre-scale distances. Its route deviates up to approximately 23 m from the initial hand-drawn proposal while staying on the selected pedestrian corridor. Building facades remain plain grey. A later detailing pass must verify the station frontage, selected shops, signage and landmark positions against street-level references. The finite preview ends at Steintor; a later road transition is not yet modelled.

## Public-realm revision v2 (24 October)

The user's marked images clarify a full area: the building edges, the complete Bahnhofstraße pedestrian surface, its sunken promenade, Kröpcke, Georgstraße and the Steintor square. The first candidate incorrectly reduced the intended setting to a narrow route surface. Version2 replaces that interpretation with approximately29,373m² of public paving and a continuous neutral context surface under the surrounding city. Five authored paving zones distinguish central fields, edges and plazas; these are representative patterns, not stone-by-stone surveyed textures.

The opening lip was reinterpreted from the official aerial imagery, with approximately±2m interpretation uncertainty. The old route now correctly fails the opening-intersection regression check. A new8-control route follows the usable upper corridor and turns more broadly through Kröpcke. Runtime/Python length is approximately718.405m and the minimum sampled turn radius is11.322m. The full3.6m swept player corridor is supported, with approximately1.545m source-building clearance and0.686m opening clearance. This does not certify current real-world accessibility.

The update places41 trees:32 avenue trees at16 paired stations and9 plaza trees. The avenue rows are representative inferences from the official aerial alignment and licensed street-level photo, with approximately10m row separation and±3m placement uncertainty. Authored avenue height is9.75m; exact current tree count, species, height and canopy shape are not claimed. Scaled lower trunk/branch geometry clears the complete player corridor while the higher canopy may overhang it, as in an avenue. Actual scaled canopies also clear source buildings and added facades. Independent checks include full tree-canopy and facade mesh projections, not only centres and old footprints. The retaining walls face into the openings and upward lower floors are checked with front-face ray tests; deliberately missing floors and reversed wall faces are rejected.

The Georgstraße field uses original gray rectangular pavers and two continuous2m terracotta-brick strips, following the visible material organisation in the2019 reference. The stripe patterns, colours and dimensions are authored interpretations; no photographic pixels are used. Warm/light station and square paving remain distinct. Paving zones are geometrically disjoint rather than stacked coplanar overlays.

Two source-aligned buildings receive10,616 triangles of initial facade detail: the rounded Magis corner and Kröpcke-Center. Reference dates and source age are important: the Center was redeveloped after the base survey, so its facade envelope is interpreted as29.1m with six-storey treatment rather than forced into the older main-wall height. The Magis skin interprets rounded corners and ribbon windows and extends about2m beyond the old parcel on two visible sides. That modification is recorded; current storefront branding, hidden returns and the full roof silhouette are not presented as verified replicas. The source building geometry is credited separately from the authored detail.

Street-level sources and per-photo licence evidence are in `RunnerGame/Art/assets/hannover_street_references/refs.json`. The resized photo pack and contact sheet retain their CC BY-SA licences. See the complete per-photo credits in `CREDITS_REFERENCE_ONLY.md` and central `RunnerGame/CREDITS.md`. Public architectural descriptions from [the limestone supplier](https://www.hofmann-naturstein.com/de/referenz/kroepcke-center/) and [the project engineers](https://www.zwp.de/de/projekte/einkaufszentren/kroepcke-center-hannover/) supplement the free-licensed photo references; their webpage photographs are not incorporated into the assets.

The renderer adds project-owned daylight shadow mapping for the new map (2048 depth texture, nine-sample filtering); the original street mode remains unchanged. Inspection allows moving along the map and orbiting the paused scene. These rendering changes improve depth cues; they do not establish geographic accuracy or finish the remaining grey facades.

Current geometry and ground: `RunnerGame/Art/assets/hannover_public_realm/`. Architectural-detail sources and limitations: `RunnerGame/Art/assets/kroepcke_facade_details/`. Version1 is preserved at `hannover_pedestrian_blockout/`. A full reconstruction still needs station frontage, additional street-by-street facade references, detailed lower-level access geometry, shopfronts and further material work.
