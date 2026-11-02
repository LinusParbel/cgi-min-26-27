using OpenTK.Mathematics;
using OpenTK.Windowing.GraphicsLibraryFramework;

namespace Engine;

// A camera that is steered with the keyboard ("fly cam"):
// arrow left/right = turn, arrow up/down = move forward/back, W/S = move up/down.
// Call Update once per frame in Application.Update and draw with FlyCamera.Camera.
public sealed class FlyCamera
{
    private float _yaw;     // rotation around the Y axis in radians, 0 = looking along -Z
    private float _pitch;   // rotation up/down in radians

    public FlyCamera(Vector3 position, float yaw = 0.0f, float pitch = 0.0f)
    {
        Position = position;
        _yaw = yaw;
        _pitch = pitch;
        Camera = new Camera(position, position + Forward);
    }

    public Camera Camera { get; }
    public Vector3 Position { get; private set; }

    // speeds per second, independent of the frame rate
    public float MoveSpeed { get; set; } = 5.0f;
    public float TurnSpeed { get; set; } = 1.5f;

    // the direction the camera looks at, calculated from yaw and pitch
    public Vector3 Forward => new(
        MathF.Sin(_yaw) * MathF.Cos(_pitch),
        MathF.Sin(_pitch),
        -MathF.Cos(_yaw) * MathF.Cos(_pitch));

    public void Update(KeyboardState keyboard, float deltaTime)
    {
        ArgumentNullException.ThrowIfNull(keyboard);

        if (keyboard.IsKeyDown(Keys.Left)) _yaw -= TurnSpeed * deltaTime;
        if (keyboard.IsKeyDown(Keys.Right)) _yaw += TurnSpeed * deltaTime;

        Vector3 position = Position;
        if (keyboard.IsKeyDown(Keys.Up)) position += Forward * MoveSpeed * deltaTime;
        if (keyboard.IsKeyDown(Keys.Down)) position -= Forward * MoveSpeed * deltaTime;
        if (keyboard.IsKeyDown(Keys.W)) position += Vector3.UnitY * MoveSpeed * deltaTime;
        if (keyboard.IsKeyDown(Keys.S)) position -= Vector3.UnitY * MoveSpeed * deltaTime;
        Position = position;

        Camera.LookAt(Position, Position + Forward);
    }
}
