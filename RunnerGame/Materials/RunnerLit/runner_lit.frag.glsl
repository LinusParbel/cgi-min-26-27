#version 330 core
in vec3 worldPosition, worldNormal;
in vec2 uv;
uniform sampler2D uTexture;
uniform vec3 uCameraPosition, uLightPosition, uFogColor;
uniform float uFogStart, uFogEnd;
uniform sampler2D uShadowMap;
uniform float uShadowsEnabled;
uniform mat4 uLightSpace;
uniform vec3 uSunDirection;
out vec4 outColor;
float shadowVisibility(vec3 N, vec3 L) {
    vec4 light=vec4(worldPosition,1.0)*uLightSpace;
    vec3 p=light.xyz/light.w*0.5+0.5;
    // Each PCF sample lies on a different point of the receiver plane. Comparing
    // all nine against the centre depth creates regular bands on large paving
    // triangles, even when the centre sample has a valid constant depth bias.
    vec3 dx=dFdx(p), dy=dFdy(p);
    float determinant=dx.x*dy.y-dx.y*dy.x;
    vec2 depthGradient=vec2(0.0);
    if(abs(determinant)>1e-12)
        depthGradient=vec2(dx.z*dy.y-dy.z*dx.y,dx.x*dy.z-dy.x*dx.z)/determinant;
    if(any(lessThan(p,vec3(0.0))) || any(greaterThan(p,vec3(1.0)))) return 1.0;
    float bias=max(0.00018,0.00085*(1.0-max(dot(N,L),0.0)));
    vec2 texel=1.0/vec2(textureSize(uShadowMap,0));
    float visible=0.0;
    for(int y=-1;y<=1;y++) for(int x=-1;x<=1;x++) {
        vec2 sampleUv=p.xy+vec2(x,y)*texel;
        // Nearest sampling reads the texel centre, including a fractional offset
        // for the centre tap. Correct that offset as well as the PCF tap offset.
        vec2 sampledCentre=(floor(sampleUv/texel)+vec2(0.5))*texel;
        float receiverDepth=p.z+dot(depthGradient,sampledCentre-p.xy);
        visible+=receiverDepth-bias<=texture(uShadowMap,sampleUv).r ? 1.0 : 0.0;
    }
    // Fade at the shadow coverage boundary instead of a hard moving rectangle.
    float edge=min(min(p.x,1.0-p.x),min(p.y,1.0-p.y));
    return mix(1.0,visible/9.0,smoothstep(0.0,0.06,edge));
}
void main() {
    vec3 base=pow(texture(uTexture,uv).rgb,vec3(2.2));
    vec3 N=normalize(worldNormal);
    vec3 L=normalize(uLightPosition-worldPosition);
    if(uShadowsEnabled>0.5) L=normalize(uSunDirection);
    vec3 V=normalize(uCameraPosition-worldPosition);
    float diffuse=max(dot(N,L),0.0);
    float spec=0.07*pow(max(dot(reflect(-L,N),V),0.0),24.0)*step(0.001,diffuse);
    vec3 lit=base*(0.36+0.78*diffuse)+vec3(spec);
    if(uShadowsEnabled>0.5) {
        float visibility=shadowVisibility(N,L);
        lit=base*(vec3(0.28,0.32,0.38)+vec3(0.86,0.79,0.67)*diffuse*visibility)+vec3(spec*visibility);
    }
    float fog=smoothstep(uFogStart,uFogEnd,length(uCameraPosition-worldPosition));
    vec3 linearColor=mix(lit,pow(uFogColor,vec3(2.2)),fog);
    outColor=vec4(pow(max(linearColor,vec3(0.0)),vec3(1.0/2.2)),1.0);
}
