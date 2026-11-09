#version 330 core

// the fullscreen quad (Primitives.CreateFullscreenQuad) is already in the projected range -1..1
layout(location = 0) in vec3 localPosition;
layout(location = 2) in vec2 texCoord;

out vec2 uv;

void main()
{
    // the texture coordinate of the quad is exactly the coordinate to read the G-buffer textures
    uv = texCoord;

    // no matrix needed (no camera, no object transformation)
    gl_Position = vec4(localPosition, 1.0);
}
