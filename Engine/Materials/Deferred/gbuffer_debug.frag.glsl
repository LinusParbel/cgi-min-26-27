#version 330 core

// shows one G-buffer texture directly on the screen (debug view)
uniform sampler2D uTexture;

in vec2 uv;
out vec4 outColor;

void main()
{
    outColor = vec4(texture(uTexture, uv).rgb, 1.0);
}
