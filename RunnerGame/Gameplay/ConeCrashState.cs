namespace RunnerGame.Gameplay;

/// <summary>One terminal street-cone contact; world simulation freezes at this snapshot.</summary>
public sealed class ConeCrashState(float playerX, float playerY, bool ducking, int coneId, float coneX, float coneZ)
{
    public const float Duration = 17;
    public float PlayerX { get; } = playerX;
    public float PlayerY { get; } = playerY;
    public bool WasDucking { get; } = ducking;
    public int ConeId { get; } = coneId;
    public float ConeX { get; } = coneX;
    public float ConeZ { get; } = coneZ;
    public float Time { get; private set; }
    public bool Complete => Time >= Duration;
    internal void Advance(float dt) => Time = Math.Min(Duration, Time + dt);
}
