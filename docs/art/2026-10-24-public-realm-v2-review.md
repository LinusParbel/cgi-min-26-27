# Hannover public realm v2 independent review — 2026-10-24

Scope: geography, actual exported hero geometry alignment, ground support, tree clearance, and attribution paths. Only this review file was changed. No renderer/shadow approval, GUI inspection, builds, or commits were performed.

## Decision

The v2 geometry corrects the narrow-track interpretation: it supplies 29,372.82 m² of public realm plus 759,959.80 m² of background support. The red outlines in the two user images express the extent of the pedestrian area, including the broad spaces around the route. They are scope references, not permission to derive Google imagery pixels. `placements-source.json` explicitly records manual interpretation of the licensed aerial and says the user Google markings were used for scope only.

The current geometry passes the independent clearance checks below. This is not approval of complete Hannover realism: most surrounding buildings remain neutral LoD2 masses, the paving is representative, and the two detailed Kröpcke buildings are a first facade pass. The lower level still assumes a 3 m depth; flat upper ground and aerial interpretation uncertainties remain material limitations.

## Independent geometry evidence

A read-only Python check used the repository's Shapely/Numpy dependency directory. It parsed the actual exported OBJ triangle coordinates, projected nonzero-area triangles to X/Z, unioned all object groups for each building, and reconstructed the eight current route controls with the builder's 20% quadratic corner trims. No build module was imported or executed. Curve sampling was approximately 5 cm; the conservative player envelope was a 1.8 m buffered tube.

| Check | Result |
|---|---:|
| Reconstructed route length | 718.405016 m |
| Minimum analytic turn radius | 11.321857 m |
| Actual building_0271 complete hero projection to tube | 27.379948 m clearance; 0 m² overlap |
| Actual building_0307 complete hero projection to tube | 6.292365 m clearance; 0 m² overlap |
| Tube outside actual exported ground triangle projection | 0 m² |
| All 24 full tree mesh projections against source footprints plus actual hero projection | 0 intersections |
| Minimum full tree projection clearance to those obstacles | 2.681244 m |

The hero check includes the rounded corner and stair tower objects, roof cap, shell, and facade groups. It therefore covers the Magis skin extension beyond its old source footprint; source footprint clearance alone would not establish that result. Full-height projection is deliberately conservative: it also treats overhanging upper parts as horizontal obstacles.

The tree test transformed the actual installed `Assets/Models/Umgebung/StreetTree/ENV_StreetTree.obj`, whose horizontal bounds are X[-1.76435,1.73565], Z[-1.759605,1.740395], to each map placement. It includes canopy extent, rather than checking only trunk centre points. All 24 current placements have scale 1 and yaw 0.

The ground projection test proves horizontal support only. Separately, the current `lower-visibility-verification.json` reports 117 upward floor triangles, eight inside wall rays, inward wall normals, outward rail normals, and detection of missing-floor and reversed-wall negative fixtures. These are relevant front-face checks; GPU appearance after that fix still needs the parent agent's current runtime evidence.

## Hero reference assessment

Inspected the four-photo licensed reference sheet and `previews/model_together.png`. Photo 03 supports the Kröpcke-Center's pale vertical bays and rounded prow; photo 04 supports Magis horizontal ribbon glazing and its taller rounded stair corner. The preview makes those two facade families visibly distinct. The exported hero has 10,616 triangles according to its verification record. Its authored atlas contains no sampled photo pixels according to the generator/verification record.

This is a recognizable architectural interpretation, not a surveyed present-day reconstruction. Photographs 03/04 date from 2014; the official model is generalized, based on older survey data. The six-storey/limestone factual explanation has supplier/project URLs in the hero credits. This review did not independently fetch those websites and does not certify their current wording.

## Must fix before a final professor-facing handoff

1. Update the professor-facing explanation, central/runtime credits, and handoff to v2. Describe full public-area coverage, the revised opening and route, the two detailed buildings, remaining grey buildings, flat datum/assumed depth, and the distinction between user scope screenshots and licensed source data. Avoid claiming that the whole city is finished or that the 2010 generalized footprints prove current survey accuracy.
2. Ensure the distributed map's credits include both official aerial/model attribution and the facade reference author, title, licence links, source URLs, historical date, and alteration/reference-only statements. Relevant records already exist at `hannover_public_realm/SOURCE_CREDITS.txt`, `kroepcke_facade_details/SOURCE_CREDITS.txt`, `kroepcke_facade_details/refs.json`, and `hannover_street_references/CREDITS_REFERENCE_ONLY.md`. The map merges the hero through `extraManifests` key `facades`; an aerial-only map credit is insufficient to explain that merged asset's provenance.
3. Obtain a current runtime image after the lower-floor/wall winding repair before presenting that repair visually. The existing `docs/art/previews/hannover-v2-kroepcke.bmp` predates the ground fix and cannot establish the repaired appearance. Shadow work is expressly outside this review.

## Could fix / regression robustness

Persist the actual hero projection and full canopy checks in the verifier. The current `hannover_public_realm/verify.py` uses old source footprints for route clearance and tests prop centres at a fixed distance. Current exports are clear, but a future facade extrusion or larger canopy could violate those conditions while that verifier continues to pass. Ground support checks should keep both exported geometry coverage and front-face visibility negative fixtures.

For stronger visual fidelity, continue the many untreated shopfronts/facades and compare representative route-height views along Bahnhofstraße and Georgstraße against the licensed reference set. Keep that remaining work explicit rather than treating passing geometry counts as an aesthetic acceptance test.

## Bounded closeout — later on 24 October

Inspected the refreshed `docs/art/previews/hannover-v2-kroepcke.bmp` once. The lower opening now visibly contains retaining walls and a lit lower floor behind the railings, rather than relying solely on geometry metadata. This frame supplies visual evidence for that local floor/wall repair; it is not an independent audit of the shadow implementation, all camera angles, or the entire lower-level access layout.

Read the updated `HANNOVER_MAP_SOURCES_AND_METHOD.md` v2 status/revision and source table, the appended central `RunnerGame/CREDITS.md`, and confirmed `out/STREET_REFERENCE_CREDITS.md` exists. The current documentation distinguishes Google user-image intent from official licensed measurements, gives Commons photograph licence/author/source details, and explicitly preserves the unfinished-facade and survey limitations. The three handoff findings above are closed for this bounded review on that evidence. The older v1 numeric results are explicitly retained under their 23 October comparison heading; v2 is the current status.

The independent geometry check is now reproducible with `python docs/art/check_v2_integration.py`. It only reads source inputs and writes its own `docs/art/v2-integration-checks.json`; no build module executes. Its completed run passed with hero tube clearances 27.379948 m / 6.292365 m, zero unsupported tube area, 24 canopy checks with minimum 2.681244 m clearance, and a deliberately blocked translated tree fixture detected. Input hashes are in that JSON. This supplements the existing verifier rather than changing its scope.

Verdict: current integration geometry and the local repaired opening have supporting evidence; the full-city architectural reconstruction remains unfinished. No whole-city realism approval or shadow-code approval is implied.

### Paired avenue placement revision

The preceding 24-tree results describe the earlier placement snapshot. Re-ran the independent checker after the paired avenue revision: 41 current trees pass actual full-mesh projection clearance, with minimum building/hero separation **0.266170 m**. The checker now applies each finite positive scale and finite yaw about local origin, using negative X/Z rotation angle to match the engine Y-axis transform, then translates to the map location. It no longer assumes scale 1. The blocked-tree negative fixture uses a 1.5-scaled canopy and is detected. Hero tube clearances, zero unsupported tube area, route length and bend radius remain as above. The updated JSON hashes identify the checked snapshot; this is model clearance, not a claim of surveyed tree dimensions or position accuracy.
