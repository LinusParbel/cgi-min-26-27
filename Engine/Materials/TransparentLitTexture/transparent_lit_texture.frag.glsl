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

uniform float uShininess;
uniform float uAlpha;

in vec2 uv;
in vec3 fragNormal;
in vec3 fragPosition;

out vec4 outColor;

void main()
{
    mat3 normalMatrix = mat3(uModel);
    vec3 normal = normalize(fragNormal * normalMatrix);

    // surface color and alpha from the texture
    vec4 surfaceColor = texture(uTexture, uv);

    // the same lighting as in AmbientDiffuseSpecularMaterial (Blinn-Phong)
    float brightness = max(dot(normal, uLightDirection), 0.0);
    vec3 v = normalize(uCameraPosition - fragPosition);
    vec3 h = normalize(uLightDirection + v);
    float ndoth = max(dot(normal, h), 0.0);
    float specularIntensity = pow(ndoth, uShininess) * brightness;

    vec3 color = surfaceColor.rgb * (uLightAmbientColor + brightness * uLightDiffuseColor)
               + specularIntensity * uLightSpecularColor;

    // the alpha of the texture is multiplied by the alpha parameter;
    // the highlight is a reflection on the surface, so it stays visible even on clear glass
    float alpha = min(surfaceColor.a * uAlpha + specularIntensity, 1.0);
    outColor = vec4(color, alpha);
}
