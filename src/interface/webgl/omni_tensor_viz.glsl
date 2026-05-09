#version 300 es
precision highp float;

// OMNI WebGL Shader for Neural Network Activation Visualization
in vec2 vTexCoord;
out vec4 fragColor;

uniform float time;
uniform sampler2D activationTexture;

void main() {
    // Read neural activation map
    vec4 actMap = texture(activationTexture, vTexCoord);
    
    // Apply OMNI heat-map color grading
    float intensity = actMap.r;
    vec3 color = vec3(0.0);
    
    if (intensity < 0.3) {
        color = mix(vec3(0.0, 0.0, 0.5), vec3(0.0, 0.5, 1.0), intensity / 0.3);
    } else if (intensity < 0.7) {
        color = mix(vec3(0.0, 0.5, 1.0), vec3(1.0, 1.0, 0.0), (intensity - 0.3) / 0.4);
    } else {
        color = mix(vec3(1.0, 1.0, 0.0), vec3(1.0, 0.0, 0.0), (intensity - 0.7) / 0.3);
    }
    
    // Pulse effect based on time
    color += vec3(0.1) * sin(time * 5.0 + intensity * 10.0);
    
    fragColor = vec4(color, 1.0);
}
