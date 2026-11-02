namespace RunnerGame.Animation;

public readonly record struct IntroInput(bool Focused, bool StartDown, bool PausePressed, bool RestartPressed);
public enum IntroPhase { Ready, Playing, Paused, Complete }
public readonly record struct IntroTransition(bool Reset = false, bool Handoff = false, bool PauseChanged = false);
