#version 330 core
layout(location=0) in vec3 localPosition;
layout(location=1) in vec3 localNormal;
layout(location=2) in vec2 texCoord;
uniform mat4 uModel, uView, uProjection;
out vec3 worldPosition;
out vec3 worldNormal;
out vec2 uv;
void main() {
    uv=texCoord;
    worldPosition=(vec4(localPosition,1.0)*uModel).xyz;
    worldNormal=normalize(localNormal*transpose(inverse(mat3(uModel))));
    gl_Position=vec4(localPosition,1.0)*uModel*uView*uProjection;
}
