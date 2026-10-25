using RunnerGame.Gameplay;

namespace RunnerGame.Rendering;

public interface IRunnerScene : IDisposable
{
    void Resize(int width, int height);
    void Render(RunSimulation state);
    int MeshCount { get; }
    int TextureCount { get; }
    int DrawCount { get; }
}
