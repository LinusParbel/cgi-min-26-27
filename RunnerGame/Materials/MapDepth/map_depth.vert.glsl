#version 330 core
layout(location=0) in vec3 localPosition;
uniform mat4 uModel, uView, uProjection, uLightSpace;
uniform float uCameraProjectionWeight;
void main() {
    vec4 world=vec4(localPosition,1.0)*uModel;
    gl_Position=mix(world*uLightSpace,world*uView*uProjection,uCameraProjectionWeight);
}
