#version 330 core

// the light volume: a sphere, scaled to the radius of the light and moved to its position
layout(location = 0) in vec3 localPosition;

uniform mat4 uModel;
uniform mat4 uView;
uniform mat4 uProjection;

void main()
{
    gl_Position = vec4(localPosition, 1.0) * uModel * uView * uProjection;
}
