#version 330 core

// color texture, normal map and cube map
uniform sampler2D uColorTexture;
uniform sampler2D uNormalMap;
uniform samplerCube uCubeTexture;

// directional light, set by the renderer (DirectionalLight); no specular color needed here
uniform vec3 uLightDirection;
uniform vec3 uLightAmbientColor;
uniform vec3 uLightDiffuseColor;

in vec2 uv;
in vec3 fragV;
in mat3 fragTBN;

out vec4 outColor;

void main()
{
    // normal from the normal map (see NormalMappingMaterial)
    vec3 normal = texture(uNormalMap, uv).rgb;
    normal = normalize(normal * 2.0 - 1.0);
    normal = normalize(fragTBN * normal);

    // the reflected view direction picks the color from the cube map
    vec3 texcoord = normalize(reflect(fragV, normal));
    vec3 cubeColor = texture(uCubeTexture, texcoord).rgb;

    // diffuse brightness as in AmbientDiffuseSpecularMaterial
    float brightness = max(dot(normal, uLightDirection), 0.0);

    vec3 surfaceColor = texture(uColorTexture, uv).rgb;

    // ambient + diffuse as usual, the cube map color replaces the specular highlight
    vec3 color = surfaceColor * (uLightAmbientColor + brightness * uLightDiffuseColor) + cubeColor;

    outColor = vec4(color, 1.0);
}
