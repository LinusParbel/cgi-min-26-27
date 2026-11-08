# Street city backdrop sources

The canonical editable source is RunnerGame/Rendering/StreetCityGeometry.cs.
This is code-native procedural runtime geometry: no Blender export or external
model download is required. It reuses the existing shared ShopfrontKit facade
meshes, Shopfront atlas and StreetKit atlas. Their licence and source records
remain in RunnerGame/CREDITS.md and the original asset folders.

CreateFacadeCore supplies an eight-metre-deep closed building volume, roof,
parapet and small roof fixtures. CreateStreetBuilding combines that core and
existing ground/upper facades into one draw. SquareFacade in SceneRenderer uses
these complete front buildings for both the street rows and plaza enclosures.

CreateNeighbourhood builds a repeatable 420-metre district of complete four-sided
buildings. Buildings() is the shared deterministic layout. It reserves the full
Rathaus forecourt and enclosing wings, and the clock square and its rear walls,
including wrapped district boundaries. Each building has surrounding paving.
CreateGround extends terrain outside the road corridor past the camera/fog range;
it deliberately leaves the road centre empty so the existing van opening is
not sealed by a new underlying plane; the cone cinematic
extends the main street before and behind the riding origin.

Background districts are batched into shared meshes, with distant district tiles
omitted outside the camera fog range. The current ticket shot uses 336 draws
rather than the initial unbatched revision's 624, with the same visible buildings.
Counts describe this capture, not a sustained frame-rate benchmark.

Street fog color is synchronized with the scene clear color via RunnerLitMaterial.
Default fog remains the previous gray for other renderers. The cone sky can
therefore turn blue without gray fully fogged landmark silhouettes. No existing
shared model or atlas bytes are edited, and normal gameplay collision rules are
unchanged. This is a stylized decorative street district, not a geographic map.

Review evidence and feedback belong to Assets/Animations/ConeCrash/review.md.
The two user screenshots are preserved as local ignored review media. Generation
is runtime C#; local Python review packaging remains ignored by repository policy.
