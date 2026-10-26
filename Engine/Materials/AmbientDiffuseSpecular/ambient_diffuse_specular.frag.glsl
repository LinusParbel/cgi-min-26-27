#version 330 core

uniform sampler2D uTexture;
uniform mat4 uModel;

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
in vec3 fragNormal;
in vec3 fragPosition;

out vec4 outColor;

void main()
{
    // rotation (and scale) of the model matrix, to bring the normal into world space
    mat3 normalMatrix = mat3(uModel);
    vec3 normal = normalize(fragNormal * normalMatrix);

    // surface color from the texture
    vec3 surfaceColor = texture(uTexture, uv).rgb;

    // diffuse: Lambert's cosine law, no light from behind
    float brightness = max(dot(normal, uLightDirection), 0.0);

    // specular (Blinn): halfway vector between light direction and view direction
    vec3 v = normalize(uCameraPosition - fragPosition);
    vec3 h = normalize(uLightDirection + v);
    float ndoth = max(dot(normal, h), 0.0);
    // multiplied with the diffuse brightness: no highlight on surfaces facing away from the light,
    // and the highlight fades out softly towards the shadow side
    float specularIntensity = pow(ndoth, uShininess) * brightness;

    // ambient + diffuse are multiplied with the surface color, the highlight is added on top
    vec3 color = surfaceColor * (uLightAmbientColor + brightness * uLightDiffuseColor)
               + specularIntensity * uLightSpecularColor;

    outColor = vec4(color, 1.0);
}
