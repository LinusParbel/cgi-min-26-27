namespace RunnerGame.Animation;

/// <summary>Pure playback clock. Gameplay advances only after the single handoff.</summary>
public sealed class ConeIntroController
{
    public const float Duration = 12;
    private static readonly float[] Boundaries = [0, 1.5f, 3, 4.25f, 5, 6.5f, 8, 10];
    private readonly IntroCue[] cues;
    private readonly List<IntroCue> pending = [];
    private bool startWasDown;
    private int nextCue;
    public IntroPhase Phase { get; private set; } = IntroPhase.Ready;
    public float Time { get; private set; }
    public string ShotId => $"S{Math.Max(0, Array.FindLastIndex(Boundaries, b => Time >= b)) + 1:00}";

    public ConeIntroController(IReadOnlyList<IntroCue> cues)
    {
        ArgumentNullException.ThrowIfNull(cues);
        this.cues = cues.ToArray();
        var ids = new HashSet<string>(StringComparer.Ordinal);
        float last = -1;
        foreach (var cue in this.cues)
        {
            if (cue == null || string.IsNullOrWhiteSpace(cue.Id) || string.IsNullOrWhiteSpace(cue.Sound) ||
                !ids.Add(cue.Id) || !float.IsFinite(cue.Time) || cue.Time < last || cue.Time < 0 || cue.Time > Duration)
                throw new ArgumentException("Cues require unique IDs, sounds and sorted finite times in [0,12].", nameof(cues));
            last = cue.Time;
        }
    }

    public IntroTransition HandleInput(IntroInput input)
    {
        bool pressed = input.StartDown && !startWasDown;
        startWasDown = input.StartDown;
        if (input.RestartPressed && input.Focused)
        {
            Time = 0; nextCue = 0; pending.Clear(); Phase = IntroPhase.Ready;
            return new(Reset: true);
        }
        if (!input.Focused)
        {
            if (Phase == IntroPhase.Playing) { Phase = IntroPhase.Paused; return new(PauseChanged: true); }
            return default;
        }
        if (Phase == IntroPhase.Paused)
        {
            if (input.PausePressed || pressed) { Phase = IntroPhase.Playing; return new(PauseChanged: true); }
            return default;
        }
        if (Phase == IntroPhase.Playing && input.PausePressed)
        { Phase = IntroPhase.Paused; return new(PauseChanged: true); }
        if (pressed && Phase == IntroPhase.Ready) { Phase = IntroPhase.Playing; CollectCues(); }
        else if (pressed && Phase == IntroPhase.Playing) return Finish();
        return default;
    }

    public IntroTransition Advance(float seconds)
    {
        if (!float.IsFinite(seconds) || seconds < 0) throw new ArgumentOutOfRangeException(nameof(seconds));
        if (Phase != IntroPhase.Playing) return default;
        Time = Math.Min(Duration, Time + seconds);
        CollectCues();
        return Time >= Duration ? Finish(clearCues: false) : default;
    }

    private void CollectCues()
    { while (nextCue < cues.Length && cues[nextCue].Time <= Time) pending.Add(cues[nextCue++]); }
    private IntroTransition Finish(bool clearCues = true)
    {
        Time = Duration; Phase = IntroPhase.Complete; nextCue = cues.Length;
        if (clearCues) pending.Clear();
        return new(Handoff: true);
    }
    public IReadOnlyList<IntroCue> DrainCues()
    { var result = pending.ToArray(); pending.Clear(); return result; }
}
