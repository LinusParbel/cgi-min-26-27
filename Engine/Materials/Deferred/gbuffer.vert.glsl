#version 330 core

// input from the VAO (attribute locations, see Mesh.cs)
layout(location = 0) in vec3 localPosition;
layout(location = 1) in vec3 localNormal;
layout(location = 2) in vec2 texCoord;
layout(location = 3) in vec3 localTangent;
layout(location = 4) in vec3 localBitangent;

// the matrices are set by the renderer for each draw call
uniform mat4 uModel;
uniform mat4 uView;
uniform mat4 uProjection;

out vec2 uv;
out vec3 fragPosition;
out mat3 fragTBN;

void main()
{
    // TBN matrix in world space, as in the NormalMappingMaterial
    vec3 T = normalize((vec4(localTangent, 0.0) * uModel).xyz);
    vec3 B = normalize((vec4(localBitangent, 0.0) * uModel).xyz);
    vec3 N = normalize((vec4(localNormal, 0.0) * uModel).xyz);
    fragTBN = mat3(T, B, N);

    uv = texCoord;

    // the position in world space is written into the G-buffer
    vec4 worldPosition = vec4(localPosition, 1.0) * uModel;
    fragPosition = worldPosition.xyz;

    gl_Position = worldPosition * uView * uProjection;
}
