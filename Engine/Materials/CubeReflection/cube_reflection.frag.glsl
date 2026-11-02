#version 330 core

uniform samplerCube uCubeTexture;
uniform sampler2D uNormalMap;

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

    // the reflected view direction is the texture coordinate of the cube map
    vec3 texcoord = normalize(reflect(fragV, normal));

    outColor = vec4(texture(uCubeTexture, texcoord).rgb, 1.0);
}
