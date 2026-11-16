using OpenTK.Mathematics;
using OpenTK.Windowing.GraphicsLibraryFramework;

namespace Engine;

// A camera that is steered with mouse and keyboard, as in many games and editors:
// hold the right mouse button and move the mouse = look around (left/right and up/down),
// W/S = move forward/back in the view direction, A/D = move sideways, Q/E = move down/up,
// Shift = move faster.
// Call Update once per frame in Application.Update and draw with MouseCamera.Camera.
public sealed class MouseCamera
{
    // looking straight up or down would make the view direction parallel to the up vector
    private const float MaxPitch = 89.0f * MathF.PI / 180.0f;

    private float _yaw;     // rotation around the Y axis in radians, 0 = looking along -Z
    private float _pitch;   // rotation up/down in radians

    public MouseCamera(Vector3 position, float yaw = 0.0f, float pitch = 0.0f)
    {
        Position = position;
        _yaw = yaw;
        _pitch = Math.Clamp(pitch, -MaxPitch, MaxPitch);
        Camera = new Camera(position, position + Forward);
    }

    public Camera Camera { get; }
    public Vector3 Position { get; private set; }

    // speed per second, independent of the frame rate
    public float MoveSpeed { get; set; } = 5.0f;
    public float FastFactor { get; set; } = 4.0f;

    // rotation in radians per pixel of mouse movement
    public float MouseSensitivity { get; set; } = 0.003f;

    // the direction the camera looks at, calculated from yaw and pitch
    public Vector3 Forward => new(
        MathF.Sin(_yaw) * MathF.Cos(_pitch),
        MathF.Sin(_pitch),
        -MathF.Cos(_yaw) * MathF.Cos(_pitch));

    // to the right of the view direction, always horizontal
    public Vector3 Right => new(MathF.Cos(_yaw), 0.0f, MathF.Sin(_yaw));

    public void Update(KeyboardState keyboard, MouseState mouse, float deltaTime)
    {
        ArgumentNullException.ThrowIfNull(keyboard);
        ArgumentNullException.ThrowIfNull(mouse);

        // look around only while the right mouse button is held,
        // so the mouse can still be used normally otherwise
        if (mouse.IsButtonDown(MouseButton.Right))
        {
            _yaw += mouse.Delta.X * MouseSensitivity;
            _pitch -= mouse.Delta.Y * MouseSensitivity;    // screen Y points down
            _pitch = Math.Clamp(_pitch, -MaxPitch, MaxPitch);
        }

        float speed = MoveSpeed * deltaTime;
        if (keyboard.IsKeyDown(Keys.LeftShift) || keyboard.IsKeyDown(Keys.RightShift)) speed *= FastFactor;

        Vector3 position = Position;
        if (keyboard.IsKeyDown(Keys.W)) position += Forward * speed;
        if (keyboard.IsKeyDown(Keys.S)) position -= Forward * speed;
        if (keyboard.IsKeyDown(Keys.D)) position += Right * speed;
        if (keyboard.IsKeyDown(Keys.A)) position -= Right * speed;
        if (keyboard.IsKeyDown(Keys.E)) position += Vector3.UnitY * speed;
        if (keyboard.IsKeyDown(Keys.Q)) position -= Vector3.UnitY * speed;
        Position = position;

        Camera.LookAt(Position, Position + Forward);
    }
}
