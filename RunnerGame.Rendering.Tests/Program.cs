using System.Text.Json;
using RunnerGame.Rendering;
using OpenTK.Mathematics;

int passed = 0;
VisibilityChecks.Run();
void Check(bool value, string message) { if (!value) throw new Exception(message); passed++; }
void Reject(Action action, string message)
{
    try { action(); } catch (InvalidDataException) { passed++; return; }
    throw new Exception(message);
}
string temporary = Path.Combine(Path.GetTempPath(), "runner-manifest-tests-" + Guid.NewGuid().ToString("N"));
Directory.CreateDirectory(temporary);
try
{
    File.WriteAllText(Path.Combine(temporary, "mesh.obj"), "test");
    File.WriteAllText(Path.Combine(temporary, "texture.png"), "test");
    string manifest = Path.Combine(temporary, "model.json");
    File.WriteAllText(manifest, """{"texture":"texture.png","parts":[{"name":"wheel","obj":"mesh.obj","pivot":[1,2,3]}]}""");
    var part = ModelManifest.Read(manifest).Single();
    Check(part.Pivot == new Vector3(1, 3, -2), "Blender pivot was not converted to engine coordinates.");
    Check(part.ObjPath == Path.Combine(temporary, "mesh.obj"), "OBJ reference was not resolved.");
    Reject(() => ModelManifest.Resolve(temporary, "../mesh.obj"), "Traversal accepted.");
    Reject(() => ModelManifest.Resolve(temporary, Path.Combine(temporary, "mesh.obj")), "Absolute path accepted.");
    using var bad = JsonDocument.Parse("[1,2]");
    Reject(() => ModelManifest.EnginePivot(bad.RootElement), "Malformed pivot accepted.");
    using var huge = JsonDocument.Parse("[1,2,1e100]");
    Reject(() => ModelManifest.EnginePivot(huge.RootElement), "Nonfinite pivot accepted.");
    File.WriteAllText(manifest, """{"texture":"texture.png","parts":[{"name":"bad","obj":"../mesh.obj","pivot":[0,0,0]}]}""");
    Reject(() => ModelManifest.Read(manifest), "Manifest traversal accepted.");
    var core=StreetCityGeometry.CreateFacadeCore();
    Check(core.Vertices.Min(v=>v.Position.Z)<-8 && core.Vertices.Max(v=>v.Position.Y)>6.4f,"Street facade has no depth or roof volume.");
    Check(core.Vertices.Any(v=>v.Normal.Y>.99f && Math.Abs(v.Position.Y-6.4f)<.001f),"Street facade has no closed top.");
    var ground=StreetCityGeometry.CreateGround();
    for(int i=0;i<ground.Indices.Length;i+=3) {
        var x=ground.Indices.Skip(i).Take(3).Select(index=>ground.Vertices[index].Position.X).ToArray();
        Check(x.Max()<=-3.75f || x.Min()>=3.75f,"City terrain caps the van road opening.");
    }
    Check(StreetCityGeometry.Buildings().Count>100,"Surrounding district is empty.");
    foreach(var building in StreetCityGeometry.Buildings()) {
        bool left=building.Centre.X<0 && StreetCityGeometry.WrappedDistance(building.Centre.Z,-6)<58+building.Size.Z*.5f;
        bool right=building.Centre.X>0 && building.Centre.X-building.Size.X*.5f<28 && StreetCityGeometry.WrappedDistance(building.Centre.Z,18)<25+building.Size.Z*.5f;
        Check(!left&&!right,"Backdrop building overlaps a protected landmark plaza.");
    }
    Console.WriteLine($"PASS {passed} manifest contracts (no graphics context).");
}
finally
{
    // Remove only the uniquely created test directory.
    Directory.Delete(temporary, true);
}
