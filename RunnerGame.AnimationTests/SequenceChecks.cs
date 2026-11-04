using RunnerGame.Animation;
using RunnerGame.Audio;
using RunnerGame.Gameplay;

static class SequenceChecks
{
    sealed class FakeAudio : IIntroAudio
    {
        public List<string> Played=[]; public bool Paused; public int Resets;
        public void Play(IntroCue cue)=>Played.Add(cue.Id);
        public void SetPaused(bool value)=>Paused=value;
        public void Reset(){Resets++;Paused=false;}
        public void SetVolume(float value){}
        public void Dispose(){}
    }
    public static void Run()
    {
        foreach(float boundary in new[]{0f,4f,7f,9f,11f,12.3f,15f,17f,20f,24f,27f,29.99f})
        {
            var run=new RunSimulation(); var audio=new FakeAudio();
            using var sequence=new OpeningSequence(new[]{new IntroCue("a",1,"step")},run,audio);
            sequence.HandleInput(new(true,true,false,false)); sequence.HandleInput(new(true,false,false,false));
            sequence.Advance(boundary,true);
            if(run.Distance!=0 || run.Score!=0 || run.Phase!=RunPhase.Ready) throw new Exception("Intro advanced game");
            sequence.HandleInput(new(true,true,false,false));
            if(run.Phase!=RunPhase.Running || run.PursuitRemaining!=0 || run.Distance!=0 || run.Speed!=12) throw new Exception("Bad skip handoff");
            sequence.HandleInput(new(true,false,false,true));
            if(run.Phase!=RunPhase.Ready || sequence.Controller.Time!=0) throw new Exception("Restart mismatch");
        }
        var sim=new RunSimulation(); var sound=new FakeAudio();
        using var natural=new OpeningSequence(new[]{new IntroCue("a",1,"step")},sim,sound);
        natural.HandleInput(new(true,true,false,false)); natural.Advance(1,true);
        natural.Advance(1,false); if(!sound.Paused || natural.Controller.Time!=1) throw new Exception("Focus advance");
        natural.HandleInput(new(true,false,false,false)); natural.HandleInput(new(true,true,false,false));
        if(sound.Paused || natural.Controller.Phase!=IntroPhase.Playing) throw new Exception("Resume");
        natural.Advance(29,true); natural.Advance(1,true);
        if(natural.HandoffCount!=1 || sound.Played.Count(x=>x=="a")!=1 || sim.Phase!=RunPhase.Running) throw new Exception("Natural handoff/cue duplication");
        if(sound.Resets!=0) throw new Exception("Natural handoff must preserve continuous ambience");
        sim.TogglePause();natural.Advance(0,false);
        if(!sound.Paused)throw new Exception("Post-intro ambience ignored gameplay/crash pause");
        sim.TogglePause();natural.Advance(0,true);
        if(sound.Paused)throw new Exception("Post-intro ambience failed to resume with gameplay");
        Console.WriteLine("PASS opening sequence: boundary skips, frozen game, reset, focus/audio pause and exactly-once handoff");
    }
}
