#version 330 core

uniform sampler2D uTexture;
uniform float uAlpha;

in vec2 uv;
out vec4 outColor;

void main()
{
    outColor = texture(uTexture, uv);
    // the alpha component of the output color is multiplied by this parameter
    outColor.a *= uAlpha;
}
