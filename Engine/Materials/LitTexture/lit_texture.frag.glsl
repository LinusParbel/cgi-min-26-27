#version 330 core

in vec3 worldPosition;
in vec3 worldNormal;
in vec2 uv;
out vec4 outColor;

uniform vec3 uCameraPosition;
uniform vec3 uLightDirection;   // directional light, set by the renderer
uniform sampler2D uTexture;
uniform vec3 uTint;
uniform float uAmbientStrength;
uniform float uSpecularStrength;
uniform float uShininess;

void main()
{
    // Sample the texture and multiply with the tint.
    vec3 color = texture(uTexture, uv).rgb * uTint;

    // Calculate fake lighting
    vec3 N = normalize(worldNormal);
    vec3 L = uLightDirection;
    vec3 V = normalize(uCameraPosition - worldPosition);
    vec3 R = reflect(-L, N);

    vec3 ambient = uAmbientStrength * color;
    vec3 diffuse = max(dot(N, L), 0.0) * color;
    vec3 specular = vec3(uSpecularStrength) * pow(max(dot(R, V), 0.0), uShininess)
                    * step(0.0, dot(N, L));

    // No color space conversion for now: the texture value is written out directly.
    outColor = vec4(ambient + diffuse + specular, 1.0);
}
