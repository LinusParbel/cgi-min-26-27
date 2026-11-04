using RunnerGame.Audio;
using RunnerGame.Gameplay;

namespace RunnerGame.Animation;

/// <summary>Owns intro events and transitions, but never steps the gameplay simulation.</summary>
public sealed class OpeningSequence : IDisposable
{
    private readonly RunSimulation run;
    private readonly IIntroAudio audio;
    private bool startDown;
    public ConeIntroController Controller { get; }
    public int HandoffCount { get; private set; }
    public List<IntroCue> FiredCues { get; }=[];
    public OpeningSequence(IReadOnlyList<IntroCue> cues,RunSimulation run,IIntroAudio audio)
    { Controller=new(cues);this.run=run;this.audio=audio; }
    public void HandleInput(IntroInput input)
    { startDown=input.StartDown; Apply(Controller.HandleInput(input)); }
    public void Advance(float seconds,bool focused)
    {
        if(!focused) Apply(Controller.HandleInput(new(false,startDown,false,false)));
        Apply(Controller.Advance(seconds));
    }
    private void Apply(IntroTransition transition)
    {
        if(transition.Reset) {audio.Reset();run.Restart();FiredCues.Clear();HandoffCount=0;}
        audio.SetPaused(Controller.Phase==IntroPhase.Paused ||
            (Controller.Phase==IntroPhase.Complete && run.Phase==RunPhase.Paused));
        foreach(var cue in Controller.DrainCues()) {FiredCues.Add(cue);audio.Play(cue);}
        if(transition.Handoff)
        {
            HandoffCount++;
            if(transition.Skipped) {audio.Reset();audio.Play(new("gameAmbience",ConeIntroController.Duration,"ambience"));}
            run.Start();
        }
    }
    public void Dispose()=>audio.Dispose();
}
