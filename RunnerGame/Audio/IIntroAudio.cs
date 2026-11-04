using RunnerGame.Animation;
namespace RunnerGame.Audio;

public interface IIntroAudio : IDisposable
{
    void Play(IntroCue cue);
    void SetPaused(bool paused);
    void Reset();
    void SetVolume(float volume);
}
