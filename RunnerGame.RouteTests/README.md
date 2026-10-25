# Route geometry checks

Run `dotnet run --project RunnerGame.RouteTests` from the repository root. This is a package-free console test executable linking only `RoutePath.cs`; it does not need OpenTK or a graphics context.

The route accepts JSON `{"points":[{"x":0,"z":0},{"x":0,"z":-10}]}`. Other properties are ignored. Coordinates and sample distances must be finite; points must be distinct. Reversals with a zero corner tangent are rejected.

Corners use quadratic Bezier rounding within the incoming/corner/outgoing control-point triangle. The trim distance is 20% of the shorter adjacent segment, so this deliberately cuts corners rather than guaranteeing waypoint interpolation. Unit tangents are analytic; a 128-step lookup per curve approximates arc length. The helper provides geometry only and does not claim geographic accuracy. A negative distance or distance beyond `Length` extrapolates along the endpoint tangent, supporting trailing actors and scenery before the route start.

Checks cover straight distance and endpoint extrapolation, known rounded-corner length, continuously rotating orthonormal forward/right directions, monotonic bounded right-angle positions, JSON metadata, missing/malformed coordinates, nonfinite numbers, duplicate points and invalid sample distances. The initial red run failed because the linked production helper did not yet exist; the subsequent run passed after implementation.

An optional integration check accepts a candidate route and optional independently calculated length:

`dotnet run --project RunnerGame.RouteTests -- path/to/route.json [expected-length-metres]`

It checks actual JSON endpoint mapping, negative-distance extrapolation, unit directions at 0.05m intervals, and expected length within 0.05m when supplied. It prints maximum tangent curvature and its distance, minimum sampled bend radius, and reversed progression counts for each +/-1.5m lane offset. It fails if the sampled radius is <=1.5m or either offset reverses. These are numerical sampling checks, not a proof against every possible global self intersection or a ground footprint containment test.

Candidate integration result (148-node pedestrian blockout): C# length 714.60535m versus independent Python 714.6036924m (difference 0.00166m). At 0.05m sampling, maximum curvature was 0.50973/m and minimum radius 1.96181m at distance 243.325m. Both +/-1.5m offsets had zero reversed steps; curvature times lane offset was 0.76460, below the local fold threshold of 1. The current tightest bend is below a preferred 4m radius and wider offsets need their own assessment.
