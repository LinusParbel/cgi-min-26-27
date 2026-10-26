#version 330 core

// input from the VAO (attribute locations, see Mesh.cs)
layout(location = 0) in vec3 localPosition;
layout(location = 1) in vec3 localNormal;
layout(location = 2) in vec2 texCoord;

// the matrices are set by the renderer for each draw call
uniform mat4 uModel;
uniform mat4 uView;
uniform mat4 uProjection;

// passed to the fragment shader
out vec2 uv;
out vec3 fragNormal;
out vec3 fragPosition;

void main()
{
    // the texture coordinate and the normal are passed on directly
    uv = texCoord;
    fragNormal = localNormal;

    // position in world space: the vertex position multiplied with the model matrix
    // (OpenTK uses row vectors: vector * matrix)
    vec4 worldPosition = vec4(localPosition, 1.0) * uModel;
    fragPosition = worldPosition.xyz;

    gl_Position = worldPosition * uView * uProjection;
}
