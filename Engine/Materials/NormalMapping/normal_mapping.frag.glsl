#version 330 core

// color texture and normal map
uniform sampler2D uColorTexture;
uniform sampler2D uNormalMap;

// directional light, set by the renderer (DirectionalLight)
uniform vec3 uLightDirection;      // from the surface towards the light, normalized
uniform vec3 uLightAmbientColor;
uniform vec3 uLightDiffuseColor;
uniform vec3 uLightSpecularColor;

// camera position in world space, set by the renderer
uniform vec3 uCameraPosition;

// shininess exponent of the material
uniform float uShininess;

// input from the vertex shader
in vec2 uv;
in vec3 fragPosition;
in mat3 fragTBN;

out vec4 outColor;

void main()
{
    // normal from the normal map: color 0..1 -> direction -1..1, then from tangent space into world space
    vec3 normal = texture(uNormalMap, uv).rgb;
    normal = normalize(normal * 2.0 - 1.0);
    normal = normalize(fragTBN * normal);

    // from here on exactly as in AmbientDiffuseSpecularMaterial
    vec3 surfaceColor = texture(uColorTexture, uv).rgb;

    // diffuse: Lambert's cosine law, no light from behind
    float brightness = max(dot(normal, uLightDirection), 0.0);

    // specular (Blinn): halfway vector between light direction and view direction
    vec3 v = normalize(uCameraPosition - fragPosition);
    vec3 h = normalize(uLightDirection + v);
    float ndoth = max(dot(normal, h), 0.0);
    float specularIntensity = pow(ndoth, uShininess) * brightness;

    vec3 color = surfaceColor * (uLightAmbientColor + brightness * uLightDiffuseColor)
               + specularIntensity * uLightSpecularColor;

    outColor = vec4(color, 1.0);
}
