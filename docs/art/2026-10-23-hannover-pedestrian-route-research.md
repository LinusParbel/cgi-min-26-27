# Hannover pedestrian opening — feasibility research

User proposes a recognisable opening from Hauptbahnhof through Kröpcke and toward Steintor, with illegal scooter riding in the pedestrian zone motivating the officer's pursuit. A later section can transition to a road. This research does not change the current game or approve a finished route design.

## Recommended route concept

Hauptbahnhof / Ernst-August-Platz → Bahnhofstraße → Kröpcke → Georgstraße toward Steintor. Preserve actual landmark order, street alignment and changes in space, while allowing compressed travel distances and readable runner clearance. Start with an establishing station view, then follow the rider. Use pedestrian paving without painted traffic lanes. The three gameplay lanes can remain invisible logical paths.

Bahnhofstraße has two pedestrian levels: the sunken Niki-de-Saint-Phalle-Promenade is a defining feature. Do not flatten it away or run the player across its opening. A reference blockout must choose a viable upper-level corridor, entrances/crossings and guardrails before detailed asset production. Exact side/width/turn angle remain to be measured from open data.

## Verified source options

- Hannover official 3D city model: LoD1/LoD2, CityGML2.0, EPSG25832, CC BY4.0 stated on publisher page. Published2026-01-20. Provides a candidate base for building massing and rooflines; inspect actual files before claiming facade detail or direct engine compatibility. Whole-city LoD2 archive listed307MB; city describes1km tiles. Download only needed coverage where available.
  https://www.hannover.de/Leben-in-der-Region-Hannover/Verwaltungen-Kommunen/Die-Verwaltung-der-Landeshauptstadt-Hannover/Dezernate-und-Fachbereiche-der-LHH/Stadtentwicklung-und-Bauen/Fachbereich-Planen-und-Stadtentwicklung/Geoinformation/Open-GeoData/3D-Stadtmodell-und-Gel%C3%A4ndemodell/Digitales-3D-Stadtmodell
- Hannover official orthophotos2025: surveyed2025-03-06, published2026-01-20,20cm ground resolution, RGB JPG+JGW, EPSG25832, CC BY4.0 stated. Suitable for plan measurements and ground-layout reference; does not replace street-level facade references.
  https://www.hannover.de/Leben-in-der-Region-Hannover/Verwaltungen-Kommunen/Die-Verwaltung-der-Landeshauptstadt-Hannover/Dezernate-und-Fachbereiche-der-LHH/Stadtentwicklung-und-Bauen/Fachbereich-Planen-und-Stadtentwicklung/Geoinformation/Open-GeoData/Digitale-Orthophotos-DOP20/Digitale-Orthophotos-2025
- Official visitor description confirms Bahnhofstraße / lower promenade and Georgstraße linking Steintor:
  https://www.visit-hannover.com/Kultur-Sehensw%C3%BCrdigkeiten/Sehensw%C3%BCrdigkeiten/Kr%C3%B6pcke
- Google expressly prohibits reconstructing3D models from captured Google Earth output. Do not extract Google photogrammetry or bake Google screenshots into shipped assets. Use the openly licensed city sources and individually licensed street photographs instead.
  https://about.google/intl/en-GB_ALL/brand-resource-center/products-and-services/geo-guidelines/
- Hannover police says pedestrian-zone scooter riding is prohibited except where signs allow it. This supports the proposed fictional chase premise; do not claim a survey of every current sign along the route.
  https://www.pd-h.polizei-nds.de/startseite/pravention/verkehrsunfallpravention/neue-mobilitatsformen-117879.html

## Implementation approach to evaluate next

1. Inspect/download a small official-data sample, preserve licence/provenance and identify corridor coverage.
2. Convert map coordinates to a local origin in metres; clip buildings to a limited corridor and import CityGML into Blender with a reproducible parser/converter. Simplify/triangulate and export existing OBJ+opaquePNG contract. This conversion pipeline is not yet implemented or tested.
3. Make an untextured route blockout with accurate building massing, station forecourt, promenade opening, Kröpcke space and Georgstraße turn. Inspect in the actual game camera before detailed modelling.
4. Use free-licensed street-level references or user-owned photographs for recognisable station facade, selected corner buildings and Steintor silhouette. Reuse approved Kröpcke clock and street furniture. Treat other facades as restrained background modules until sightlines prove which need detail.
5. Replace world-Z-only placement with route-distance sampling and a lateral local frame; rotate world/camera smoothly through real turns. Keep collision and obstacle placement in route coordinates. Add tests for turns, lane orientation and chunk joins.
6. Swap road obstacles for pedestrian-zone-appropriate bins, planters, café furniture, temporary works and parked scooters; ordinary traffic belongs in a later road section. Pedestrians require a separate licensed character/animation step and should not be implied by a blockout.

First deliverable should be the recognisable route blockout, not a promise of a photorealistic complete city. Aerial photos supply layout; ground photographs and selective authored work supply the street-level identity.
