using RunnerGame.Gameplay;

static void Check(bool value, string message) { if (!value) throw new Exception(message); }
static void Near(float a, float b, float tolerance = .001f) => Check(MathF.Abs(a-b) <= tolerance, $"Expected {b}, got {a}");
static void Reject(Action action) { try { action(); } catch (ArgumentException) { return; } catch (System.Text.Json.JsonException) { return; } throw new Exception("Expected invalid route rejection"); }
var straight = new RoutePath(new[] { (0f,0f), (0f,-10f) });
Near(straight.Length,10); Near(straight.Sample(4).Z,-4);
Near(straight.Sample(-3).Z,3); Near(straight.Sample(13).Z,-13);
Near(straight.Sample(0).RightX,1);
var corner = new RoutePath(new[] { (0f,0f), (0f,-10f), (10f,-10f) });
// Two 8-unit straights plus a quadratic corner of approximately 3.24645 units.
Near(corner.Length,19.24645f,.002f);
var previous = corner.Sample(0);
for (float d = .01f; d <= corner.Length; d += .01f) {
 var s = corner.Sample(d);
 Check(float.IsFinite(s.X+s.Z+s.ForwardX+s.ForwardZ),"Finite samples");
 Near(s.ForwardX*s.ForwardX+s.ForwardZ*s.ForwardZ,1);
 Near(s.ForwardX*s.RightX+s.ForwardZ*s.RightZ,0);
 Check(s.X >= previous.X-.0001f && s.Z <= previous.Z+.0001f,"Monotonic corner");
 Check(s.X >= 0 && s.Z >= -10.001f,"Corner stays inside convex corridor");
 Check(s.ForwardX*previous.ForwardX+s.ForwardZ*previous.ForwardZ > .999f,"Smooth tangent");
 previous=s;
}
Reject(() => new RoutePath(Array.Empty<(float,float)>()));
Reject(() => new RoutePath(new[] { (0f,0f),(0f,0f) }));
Reject(() => new RoutePath(new[] { (0f,0f),(1f,0f),(0f,0f) }));
Reject(() => new RoutePath(new[] { (0f,0f),(float.NaN,0f) }));
Reject(() => straight.Sample(float.PositiveInfinity));
var file=Path.GetTempFileName();
try {
 File.WriteAllText(file,"{\"points\":[{\"x\":0,\"z\":0},{\"x\":0,\"z\":-10}],\"metadata\":true}"); Near(RoutePath.Load(file).Length,10);
 foreach(var json in new[]{"{}","{","{\"points\":[{\"x\":0},{\"x\":1,\"z\":2}]}","{\"points\":[{\"x\":0,\"z\":0},{\"x\":1e100,\"z\":2}]}"}) { File.WriteAllText(file,json); Reject(()=>RoutePath.Load(file)); }
} finally { File.Delete(file); }
Console.WriteLine("PASS: route geometry, arc length, extrapolation, JSON and invalid inputs");

if (args.Length > 0)
{
    var candidate = RoutePath.Load(args[0]);
    using var json = System.Text.Json.JsonDocument.Parse(File.ReadAllText(args[0]));
    var nodes = json.RootElement.GetProperty("points").EnumerateArray().ToArray();
    var start = candidate.Sample(0);
    var end = candidate.Sample(candidate.Length);
    Near(start.X, nodes[0].GetProperty("x").GetSingle());
    Near(start.Z, nodes[0].GetProperty("z").GetSingle());
    Near(end.X, nodes[^1].GetProperty("x").GetSingle());
    Near(end.Z, nodes[^1].GetProperty("z").GetSingle());
    var behind = candidate.Sample(-3);
    Near(behind.X,start.X-3*start.ForwardX);
    Near(behind.Z,start.Z-3*start.ForwardZ);
    if (args.Length > 1) Near(candidate.Length, float.Parse(args[1], System.Globalization.CultureInfo.InvariantCulture), .05f);
    double maxCurvature=0;
    float maxAt=0;
    int leftReversals=0,rightReversals=0;
    var prior=start;
    float priorDistance=0;
    for(int i=1; priorDistance<candidate.Length; i++)
    {
        float distance=MathF.Min(i*.05f,candidate.Length);
        var s=candidate.Sample(distance);
        Check(float.IsFinite(s.X+s.Z+s.ForwardX+s.ForwardZ),"Actual route finite sample");
        Near(s.ForwardX*s.ForwardX+s.ForwardZ*s.ForwardZ,1);
        Near(s.ForwardX*s.RightX+s.ForwardZ*s.RightZ,0);
        double cross=prior.ForwardX*s.ForwardZ-prior.ForwardZ*s.ForwardX;
        double dot=prior.ForwardX*s.ForwardX+prior.ForwardZ*s.ForwardZ;
        double curvature=Math.Abs(Math.Atan2(cross,dot))/(distance-priorDistance);
        if(curvature>maxCurvature) { maxCurvature=curvature; maxAt=(distance+priorDistance)*.5f; }
        foreach(float offset in new[]{-1.5f,1.5f})
        {
            float dx=s.X+offset*s.RightX-prior.X-offset*prior.RightX;
            float dz=s.Z+offset*s.RightZ-prior.Z-offset*prior.RightZ;
            float progress=dx*(s.ForwardX+prior.ForwardX)+dz*(s.ForwardZ+prior.ForwardZ);
            if(progress < -1e-5f) { if(offset<0) leftReversals++; else rightReversals++; }
        }
        prior=s; priorDistance=distance;
    }
    Console.WriteLine(FormattableString.Invariant($"ACTUAL: nodes={nodes.Length}, length={candidate.Length:F5}m, max curvature={maxCurvature:F5}/m, minimum sampled radius={1/maxCurvature:F5}m at distance={maxAt:F3}m; +/-1.5m lane reverse steps={leftReversals}/{rightReversals}"));
    Check(maxCurvature*1.5<1 && leftReversals==0 && rightReversals==0,"Actual route folds a 1.5m lane offset; increase corner radius");
}
