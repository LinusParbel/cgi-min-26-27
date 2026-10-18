#version 330 core

in vec3 worldPosition;
in vec3 worldNormal;
in vec2 uv;
out vec4 outColor;

uniform vec3 uCameraPosition;
uniform vec3 uLightPosition;
uniform sampler2D uTexture;
uniform vec3 uTint;
uniform float uAmbientStrength;
uniform float uSpecularStrength;
uniform float uShininess;

void main()
{
    // Texture is sRGB-encoded: convert to linear, light in linear space, encode again.
    vec3 color = pow(texture(uTexture, uv).rgb, vec3(2.2)) * uTint;

    vec3 N = normalize(worldNormal);
    vec3 L = normalize(uLightPosition - worldPosition);
    vec3 V = normalize(uCameraPosition - worldPosition);
    vec3 R = reflect(-L, N);

    vec3 ambient = uAmbientStrength * color;
    vec3 diffuse = max(dot(N, L), 0.0) * color;
    vec3 specular = vec3(uSpecularStrength) * pow(max(dot(R, V), 0.0), uShininess)
                    * step(0.0, dot(N, L));

    outColor = vec4(pow(ambient + diffuse + specular, vec3(1.0 / 2.2)), 1.0);
}
