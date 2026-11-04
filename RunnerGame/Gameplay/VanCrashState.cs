namespace RunnerGame.Gameplay;

public enum VanCrashPreviewContact { Rear, Side, Duck, Air }

/// <summary>Contact snapshot and scene clock. World simulation stays frozen.</summary>
public sealed class VanCrashState(float playerX, float playerY, bool ducking, float vanX, float vanZ)
{
    public const float Duration = 6;
    public float PlayerX { get; } = playerX;
    public float PlayerY { get; } = playerY;
    public bool WasDucking { get; } = ducking;
    public float VanX { get; } = vanX;
    public float VanZ { get; } = vanZ;
    // A side-entry contact may be alongside the van: rebound behind its rear
    // before the opening appears, rather than cutting the van's support away.
    public float ReboundZ => Math.Max(0, VanZ + 3.5f);
    public float OpeningFrontZ => ReboundZ - .65f;
    public float Time { get; private set; }
    public bool Complete => Time >= Duration;
    internal void Advance(float dt) => Time = Math.Min(Duration, Time + dt);
}
