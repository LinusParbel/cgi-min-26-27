#version 330 core

uniform sampler2D uColorTexture;
uniform sampler2D uNormalMap;
uniform float uShininess;

in vec2 uv;
in vec3 fragPosition;
in mat3 fragTBN;

// three outputs at the same time, one for each color attachment of the G-buffer
layout(location = 0) out vec4 gColor;      // output to ColorAttachment0
layout(location = 1) out vec3 gPosition;   // output to ColorAttachment1
layout(location = 2) out vec4 gNormal;     // output to ColorAttachment2 (normal + shininess)

void main()
{
    // alpha = 1 marks "there is geometry at this pixel"; the cleared background has alpha 0
    gColor = vec4(texture(uColorTexture, uv).rgb, 1.0);

    gPosition = fragPosition;

    // normal from the normal map, from tangent space into world space
    vec3 normal = texture(uNormalMap, uv).rgb;
    normal = normalize(normal * 2.0 - 1.0);
    normal = normalize(fragTBN * normal);
    gNormal = vec4(normal, uShininess);
}
