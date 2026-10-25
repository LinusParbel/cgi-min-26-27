using System.Text.Json;
using RunnerGame.Rendering;

static JsonElement Map(string json) => JsonDocument.Parse(json).RootElement.Clone();
static void Check(bool value, string message) { if (!value) throw new Exception(message); }
static void Reject(string json)
{
    try { ScenePropMetadata.ReadProps(Map(json)); }
    catch (InvalidDataException) { return; }
    throw new Exception("Invalid prop metadata was accepted: " + json);
}

Check(ScenePropMetadata.ReadProps(Map("{}")).Count == 0, "Old maps must remain compatible");
var prop = ScenePropMetadata.ReadProps(Map("""{"sceneProps":[{"kind":"bench","x":20,"z":-5,"yaw":90,"y":0.2,"scale":1.5}]}"""))[0];
Check(prop == new SceneProp("bench",20,-5,.2f,90,1.5f), "Authored transforms must survive parsing");
var defaults = ScenePropMetadata.ReadProps(Map("""{"sceneProps":[{"kind":"tree","x":0,"z":0}]}"""))[0];
Check(defaults.Y == 0 && defaults.YawDegrees == 0 && defaults.Scale == 1, "Optional transform defaults");
foreach (string invalid in new[] {
    """{"sceneProps":[{"kind":"car","x":0,"z":0}]}""",
    """{"sceneProps":[{"kind":"rack","x":0,"z":0,"scale":0}]}""",
    """{"sceneProps":[{"kind":"rack","x":0,"z":0,"scale":-1}]}""",
    """{"sceneProps":[{"kind":"lamp","x":1e99,"z":0}]}""",
    """{"sceneProps":[{"kind":"planter","x":0,"z":0,"yaw":"90"}]}"""
}) Reject(invalid);
var extras = ScenePropMetadata.ReadExtras(Map("""{"extraManifests":[{"key":"facades","manifest":"Facades_parts.json"}]}"""));
Check(extras.Single() == new ExtraSceneManifest("facades", "Facades_parts.json"), "Facade manifest preserved");
bool rejected = false;
try { ScenePropMetadata.ReadExtras(Map("""{"extraManifests":[{"key":"a","manifest":"a.json"},{"key":"a","manifest":"b.json"}]}""")); }
catch (InvalidDataException) { rejected = true; }
Check(rejected, "Duplicate facade keys must be rejected");
Console.WriteLine("Scene metadata checks passed (compatibility, transforms, invalid values, extra manifests).");
var center = new OpenTK.Mathematics.Vector3(123, -1, -345);
var lightSpace = MapShadowPass.CreateLightSpace(center);
foreach (float x in new[] { -20f, 0, 20f })
foreach (float z in new[] { -35f, 0, 35f })
{
    var world = new OpenTK.Mathematics.Vector4(center + new OpenTK.Mathematics.Vector3(x, 0, z), 1);
    var clip = world * lightSpace;
    Check(Math.Abs(clip.X / clip.W) < 1 && Math.Abs(clip.Y / clip.W) < 1 && Math.Abs(clip.Z / clip.W) < 1,
        "Shadow light frustum must cover the near-player 40m by 70m ground region");
}
var originalClip = new OpenTK.Mathematics.Vector4(center, 1) * lightSpace;
var shifted = center + new OpenTK.Mathematics.Vector3(1000, 0, -1000);
var shiftedClip = new OpenTK.Mathematics.Vector4(shifted, 1) * MapShadowPass.CreateLightSpace(shifted);
Check((originalClip - shiftedClip).Length < .001f, "Shadow camera must follow world translation");
Console.WriteLine("Shadow light-space ground coverage and translation checks passed (no graphics context).");
