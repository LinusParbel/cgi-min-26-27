#version 330 core

// the G-buffer textures
uniform sampler2D gColor;
uniform sampler2D gNormal;      // normal in rgb, shininess in a
uniform sampler2D gPosition;

// screen size in pixels, to calculate the texture coordinate from gl_FragCoord
uniform vec2 uScreenSize;

// set by the renderer
uniform vec3 uCameraPosition;

// the point light
uniform vec3 uPointLightPosition;
uniform float uPointLightRadius;
uniform vec3 uPointLightAmbientColor;
uniform vec3 uPointLightDiffuseColor;
uniform vec3 uPointLightSpecularColor;

out vec4 outColor;

void main()
{
    // screen coordinates in the range 0..1 = texture coordinate for the G-buffer textures
    vec2 fragmentScreenCoordinates = gl_FragCoord.xy / uScreenSize;

    vec4 surfaceColor = texture(gColor, fragmentScreenCoordinates);
    if (surfaceColor.a == 0.0) discard;

    // the world position of the surface at this pixel
    vec3 worldPosition = texture(gPosition, fragmentScreenCoordinates).rgb;

    // attenuation: 1 at the light position, 0 at the radius (quadratic)
    vec3 posMid = uPointLightPosition - worldPosition;
    float distance = max(length(posMid), 0.0001);
    float attenuation = clamp(1.0 - distance / uPointLightRadius, 0.0, 1.0);
    attenuation *= attenuation;

    // unlike the directional light, the light direction is different for every pixel
    vec3 lightDirection = posMid / distance;

    vec4 normalShininess = texture(gNormal, fragmentScreenCoordinates);
    vec3 normal = normalShininess.rgb;
    float shininess = normalShininess.a;

    float brightness = max(dot(normal, lightDirection), 0.0);

    // view vector is the camera position - the position in world space
    vec3 view = normalize(uCameraPosition - worldPosition);
    vec3 h = normalize(lightDirection + view);
    float ndoth = max(dot(normal, h), 0.0);
    float specularIntensity = pow(ndoth, shininess) * brightness;

    vec3 color = surfaceColor.rgb * (uPointLightAmbientColor + brightness * uPointLightDiffuseColor)
               + specularIntensity * uPointLightSpecularColor;

    // the light buffer is blended additively (One, One): every light adds its part
    outColor = vec4(color * attenuation, 1.0);
}
