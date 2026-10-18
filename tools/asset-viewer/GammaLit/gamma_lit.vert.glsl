#version 330 core

layout(location = 0) in vec3 localPosition;
layout(location = 1) in vec3 localNormal;
layout(location = 2) in vec2 texCoord;

uniform mat4 uModel;
uniform mat4 uView;
uniform mat4 uProjection;

out vec3 worldPosition;
out vec3 worldNormal;
out vec2 uv;

void main()
{
    uv = texCoord;
    // OpenTK uses row vectors; the matrices are uploaded accordingly.
    worldPosition = (vec4(localPosition, 1.0) * uModel).xyz;
    worldNormal = normalize(localNormal * transpose(inverse(mat3(uModel))));
    gl_Position = vec4(localPosition, 1.0) * uModel * uView * uProjection;
}
