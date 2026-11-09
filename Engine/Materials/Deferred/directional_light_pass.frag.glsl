#version 330 core

// the G-buffer textures
uniform sampler2D gColor;
uniform sampler2D gNormal;      // normal in rgb, shininess in a
uniform sampler2D gPosition;

// set by the renderer: camera position and the directional light
uniform vec3 uCameraPosition;
uniform vec3 uLightDirection;
uniform vec3 uLightAmbientColor;
uniform vec3 uLightDiffuseColor;
uniform vec3 uLightSpecularColor;

in vec2 uv;
out vec4 outColor;

void main()
{
    // surface color from the G-buffer; alpha 0 = no geometry, the background stays as it is
    vec4 surfaceColor = texture(gColor, uv);
    if (surfaceColor.a == 0.0) discard;

    // normal and shininess from the G-buffer
    vec4 normalShininess = texture(gNormal, uv);
    vec3 normal = normalShininess.rgb;
    float shininess = normalShininess.a;

    // the same lighting as in AmbientDiffuseSpecularMaterial, also in world space
    float brightness = max(dot(normal, uLightDirection), 0.0);

    // view vector is the camera position - the position in world space
    vec3 view = normalize(uCameraPosition - texture(gPosition, uv).rgb);
    vec3 h = normalize(uLightDirection + view);
    float ndoth = max(dot(normal, h), 0.0);
    float specularIntensity = pow(ndoth, shininess) * brightness;

    vec3 color = surfaceColor.rgb * (uLightAmbientColor + brightness * uLightDiffuseColor)
               + specularIntensity * uLightSpecularColor;
    outColor = vec4(color, 1.0);
}
