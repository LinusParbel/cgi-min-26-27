using RunnerGame.Gameplay;
using RunnerGame.Animation;

namespace RunnerGame.Rendering;

public interface IRunnerScene : IDisposable
{
    bool EnableCulling { get; set; }
    void Resize(int width, int height);
    void PrepareIntro(ConeIntroScene scene);
    void Render(RunSimulation state, IntroRenderState? intro = null);
    int MeshCount { get; }
    int TextureCount { get; }
    int DrawCount { get; }
}
