namespace RunnerGame.Gameplay;

public enum RunPhase { Ready, Running, Paused, Caught }
public enum ObjectKind { Cone, Bin, Pothole, HighBarrier, Car, Van, Coin, Planter }
public sealed class TrackObject
{
    public int Id { get; internal set; }
    public ObjectKind Kind { get; internal set; }
    public float X { get; internal set; }
    public float Z { get; internal set; }
    public bool Active { get; internal set; } = true;
    internal bool HitConsumed { get; set; }
}

/// <summary>Metres, Y up, player Z=0. Step accepts seconds and subdivides for swept contacts.</summary>
public sealed class RunSimulation
{
    readonly int seed;
    private readonly bool pedestrian;
    Random random = null!;
    int nextId, lane, safeLane, routeDirection;
    float laneStart, laneTime, jumpTime, duckTime, stumbleTime, nextRowDistance;
    bool jumping, fastFall;
    const float RideHeight = 1.674661f, DuckHeight = 1.316786f;
    const float PlayerHalfWidth = .30f, PlayerHalfLength = .80f;
    public RunSimulation(int seed = 2026, bool pedestrian = false) { this.seed = seed; this.pedestrian = pedestrian; worldView = objects.AsReadOnly(); Restart(); }
    public RunPhase Phase { get; private set; }
    public float PlayerX { get; private set; }
    public float LaneSpacing => pedestrian ? 1.5f : 2.5f;
    public float PlayerY { get; private set; }
    public bool IsDucking => duckTime > 0;
    public float Speed { get; private set; }
    public float EffectiveSpeed => Speed * (stumbleTime > 0 ? .55f : 1);
    public float Distance { get; private set; }
    public float ElapsedTime { get; private set; }
    public int CoinCount { get; private set; }
    public int Score => (int)Distance + CoinCount * 10;
    public float InvulnerabilityRemaining { get; private set; }
    public float PursuitRemaining { get; private set; }
    private readonly List<TrackObject> objects = [];
    readonly IReadOnlyList<TrackObject> worldView;
    public IReadOnlyList<TrackObject> WorldObjects => worldView;
    public void Start() { if (Phase == RunPhase.Ready) Phase = RunPhase.Running; }
    public void Restart()
    {
        random = new Random(seed); nextId = 0; lane = 0; safeLane = random.Next(-1, 2); routeDirection = random.Next(2) == 0 ? -1 : 1;
        laneStart = laneTime = jumpTime = duckTime = stumbleTime = 0;
        jumping = fastFall = false; PlayerX = PlayerY = Distance = ElapsedTime = 0;
        CoinCount = 0; InvulnerabilityRemaining = PursuitRemaining = 0;
        Speed = 12; Phase = RunPhase.Ready; objects.Clear(); nextRowDistance = 40;
        FillTrack();
    }
    public void TogglePause()
    {
        if (Phase == RunPhase.Running) Phase = RunPhase.Paused;
        else if (Phase == RunPhase.Paused) Phase = RunPhase.Running;
    }
    public void Move(int direction)
    {
        if (Phase != RunPhase.Running || direction == 0) return;
        int target = Math.Clamp(lane + Math.Sign(direction), -1, 1);
        if (target == lane) return;
        lane = target; laneStart = PlayerX; laneTime = 0;
    }
    public void Jump()
    {
        if (Phase != RunPhase.Running || jumping || IsDucking) return;
        jumping = true; fastFall = false; jumpTime = 0;
    }
    public void Duck()
    {
        if (Phase != RunPhase.Running) return;
        duckTime = .8f; fastFall = jumping;
    }
    public void Step(float dt)
    {
        if (Phase != RunPhase.Running || !float.IsFinite(dt) || dt <= 0) return;
        // Small deterministic slices bound lateral/vertical approximation; longitudinal interval is swept.
        int slices = Math.Max(1, (int)Math.Ceiling(dt / .002));
        float h = dt / slices;
        for (int i = 0; i < slices && Phase == RunPhase.Running; i++) Tick(h);
    }
    void Tick(float dt)
    {
        ElapsedTime += dt;
        InvulnerabilityRemaining = Math.Max(0, InvulnerabilityRemaining - dt);
        PursuitRemaining = Math.Max(0, PursuitRemaining - dt);
        stumbleTime = Math.Max(0, stumbleTime - dt);
        duckTime = Math.Max(0, duckTime - dt);
        float oldX = PlayerX, oldY = PlayerY;
        laneTime = Math.Min(.15f, laneTime + dt);
        PlayerX = laneStart + (lane * LaneSpacing - laneStart) * (laneTime / .15f);
        if (jumping)
        {
            jumpTime += dt;
            PlayerY = fastFall ? Math.Max(0, PlayerY - 12 * dt) : Math.Max(0, 16 * jumpTime * (.7f - jumpTime) / 1.4f);
            if (PlayerY == 0) { jumping = false; fastFall = false; }
        }
        Speed = Math.Min(30, Speed + .06f * dt);
        float travel = EffectiveSpeed * dt;
        Distance += travel;
        foreach (var obj in objects)
        {
            float oldZ = obj.Z;
            obj.Z += travel;
            if (!obj.Active || obj.HitConsumed) continue;
            var (width, length, bottom, top) = Bounds(obj.Kind);
            float near = -length - PlayerHalfLength, far = length + PlayerHalfLength;
            if (obj.Z < near || oldZ > far) continue;
            // Evaluate physical positions at entry and exit of the swept longitudinal interval.
            float entry = Math.Clamp((near - oldZ) / travel, 0, 1);
            float exit = Math.Clamp((far - oldZ) / travel, 0, 1);
            float x1 = oldX + (PlayerX - oldX) * entry, x2 = oldX + (PlayerX - oldX) * exit;
            if (Math.Max(x1,x2) < obj.X - width - PlayerHalfWidth || Math.Min(x1,x2) > obj.X + width + PlayerHalfWidth) continue;
            float feet = Math.Min(oldY, PlayerY), head = Math.Max(oldY, PlayerY) + (IsDucking ? DuckHeight : RideHeight);
            if (feet >= top || head <= bottom) continue;
            if (obj.Kind == ObjectKind.Coin) { obj.Active = false; CoinCount++; }
            else if (InvulnerabilityRemaining <= 0)
            {
                obj.HitConsumed = true;
                if (PursuitRemaining > 0) { Phase = RunPhase.Caught; break; }
                PursuitRemaining = 10; InvulnerabilityRemaining = 1; stumbleTime = 1;
            }
        }
        objects.RemoveAll(o => o.Z > 15);
        FillTrack();
    }
    static (float width, float length, float bottom, float top) Bounds(ObjectKind kind) => kind switch
    {
        ObjectKind.Cone => (.23f,.23f,0,.55f),
        ObjectKind.Bin => (.35f,.35f,0,1.0f),
        ObjectKind.Pothole => (.65f,.6f,-.2f,.12f),
        ObjectKind.HighBarrier => (.95f,.25f,1.43f,2.4f),
        ObjectKind.Car => (.9f,2.2f,0,1.6f),
        ObjectKind.Van => (1f,2.7f,0,2.6f),
        ObjectKind.Planter => (.4625f,.4625f,0,1.279f),
        _ => (.28f,.18f,.45f,1.2f)
    };
    void FillTrack()
    {
        while (nextRowDistance < Distance + 220)
        {
            foreach (int column in new[] {-1,0,1})
            {
                if (column == safeLane) continue;
                var kind = (ObjectKind)random.Next(0,6);
                if (pedestrian) kind = kind switch
                {
                    ObjectKind.Car or ObjectKind.Van => ObjectKind.Planter,
                    ObjectKind.Pothole => ObjectKind.Cone,
                    _ => kind
                };
                objects.Add(new TrackObject { Id=nextId++, Kind=kind, X=column*LaneSpacing, Z=Distance-nextRowDistance });
            }
            for (int i=0;i<3;i++) objects.Add(new TrackObject { Id=nextId++, Kind=ObjectKind.Coin, X=safeLane*LaneSpacing, Z=Distance-nextRowDistance-i*2 });
            nextRowDistance += 24;
            // Ping-pong through adjacent lanes; even camping an outer lane eventually meets traffic.
            if (safeLane + routeDirection is < -1 or > 1) routeDirection = -routeDirection;
            safeLane += routeDirection;
        }
    }
}
