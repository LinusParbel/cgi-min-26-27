using System.Numerics;
using System.Text.Json;

namespace RunnerGame.Gameplay;

public readonly record struct RouteSample(float X, float Z, float ForwardX, float ForwardZ)
{
    public float RightX => -ForwardZ;
    public float RightZ => ForwardX;
}

/// <summary>
/// Distance-parameterized provisional route. Corners are replaced with quadratic
/// Beziers trimmed by 20% of the shorter adjacent edge. Their convex hull bounds
/// corner cutting; curves do not pass through the original corner waypoint.
/// A 128-step arc-length table per corner approximates distance (not geography).
/// Outside the route, positions extrapolate along the stable endpoint tangent.
/// </summary>
public sealed class RoutePath
{
    private sealed class Piece(Vector2 a, Vector2 b, Vector2 c, bool curved)
    {
        public readonly float[] Distances = new float[curved ? 129 : 2];
        public float Start;
        public Vector2 Position(float t) => curved ? (1-t)*(1-t)*a + 2*(1-t)*t*b + t*t*c : Vector2.Lerp(a,c,t);
        public Vector2 Tangent(float t) => Vector2.Normalize(curved ? 2*((1-t)*(b-a)+t*(c-b)) : c-a);
        public float Build()
        {
            var previous = a;
            for (int i=1; i<Distances.Length; i++) {
                var position=Position((float)i/(Distances.Length-1));
                Distances[i]=Distances[i-1]+Vector2.Distance(previous,position);
                previous=position;
            }
            return Distances[^1];
        }
        public RouteSample Sample(float distance)
        {
            int index=Array.BinarySearch(Distances,distance);
            float t;
            if(index>=0) t=(float)index/(Distances.Length-1);
            else {
                index=Math.Clamp(~index,1,Distances.Length-1);
                t=(index-1+(distance-Distances[index-1])/(Distances[index]-Distances[index-1]))/(Distances.Length-1);
            }
            var p=Position(t); var forward=Tangent(t);
            return new(p.X,p.Y,forward.X,forward.Y);
        }
    }
    private readonly List<Piece> pieces = [];
    public float Length { get; private set; }

    public RoutePath(IEnumerable<(float X,float Z)> points)
    {
        ArgumentNullException.ThrowIfNull(points);
        var nodes=points.Select(p=>new Vector2(p.X,p.Z)).ToArray();
        if(nodes.Length<2 || nodes.Any(p=>!float.IsFinite(p.X)||!float.IsFinite(p.Y)) || nodes.Distinct().Count()!=nodes.Length)
            throw new ArgumentException("A route requires at least two finite, distinct points.",nameof(points));
        var cursor=nodes[0];
        for(int i=1;i<nodes.Length-1;i++) {
            var incoming=nodes[i]-nodes[i-1]; var outgoing=nodes[i+1]-nodes[i];
            float before=incoming.Length(), after=outgoing.Length();
            if(!float.IsFinite(before+after) || before<=0 || after<=0)
                throw new ArgumentException("Route edges must have finite positive lengths.",nameof(points));
            var f=incoming/before; var g=outgoing/after;
            if(Vector2.Dot(f,g)<-.99999f) throw new ArgumentException("A route cannot reverse at a zero tangent.",nameof(points));
            float trim=.2f*MathF.Min(before,after);
            var entry=nodes[i]-f*trim; var exit=nodes[i]+g*trim;
            Add(cursor,entry,entry,false);
            Add(entry,nodes[i],exit,true);
            cursor=exit;
        }
        Add(cursor,nodes[^1],nodes[^1],false);
        if(!float.IsFinite(Length)||Length<=0) throw new ArgumentException("Route length must be finite and positive.",nameof(points));
    }

    private void Add(Vector2 a,Vector2 b,Vector2 c,bool curved)
    {
        var piece=new Piece(a,b,c,curved) { Start=Length };
        float length=piece.Build();
        if(!float.IsFinite(length)||length<=0) throw new ArgumentException("Route contains a degenerate segment.");
        Length+=length;
        pieces.Add(piece);
    }

    public static RoutePath Load(string path)
    {
        using var document=JsonDocument.Parse(File.ReadAllText(path));
        var root=document.RootElement;
        if(root.ValueKind!=JsonValueKind.Object || !root.TryGetProperty("points",out var points) || points.ValueKind!=JsonValueKind.Array)
            throw new JsonException("Expected a points array.");
        var nodes=new List<(float,float)>();
        foreach(var point in points.EnumerateArray()) {
            if(point.ValueKind!=JsonValueKind.Object || !point.TryGetProperty("x",out var x) || !point.TryGetProperty("z",out var z) ||
               x.ValueKind!=JsonValueKind.Number || z.ValueKind!=JsonValueKind.Number || !x.TryGetSingle(out float px) || !z.TryGetSingle(out float pz) || !float.IsFinite(px)||!float.IsFinite(pz))
                throw new JsonException("Each point requires finite numeric x and z.");
            nodes.Add((px,pz));
        }
        return new RoutePath(nodes);
    }

    public RouteSample Sample(float distance)
    {
        if(!float.IsFinite(distance)) throw new ArgumentException("Distance must be finite.",nameof(distance));
        if(distance<0 || distance>Length) {
            var end=distance<0 ? pieces[0].Sample(0) : pieces[^1].Sample(pieces[^1].Distances[^1]);
            float extra=distance<0 ? distance : distance-Length;
            return end with { X=end.X+extra*end.ForwardX, Z=end.Z+extra*end.ForwardZ };
        }
        int low=0,high=pieces.Count-1;
        while(low<high) { int mid=(low+high+1)/2; if(pieces[mid].Start<=distance) low=mid; else high=mid-1; }
        return pieces[low].Sample(distance-pieces[low].Start);
    }
}
