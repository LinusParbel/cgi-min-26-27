#version 330 core

layout(location = 0) in vec3 localPosition;
layout(location = 2) in vec2 texCoord;

uniform mat4 uModel;
uniform mat4 uView;
uniform mat4 uProjection;

out vec2 uv;

void main()
{
    uv = texCoord;
    gl_Position = vec4(localPosition, 1.0) * uModel * uView * uProjection;
}
