// OMNI TypeScript Interface Layer: Lucid Feature Visualization
// Rendering Neural Network Activation Maximizations in WebGL.

export class FeatureVisualizer {
    private gl: WebGLRenderingContext;
    private program: WebGLProgram;

    constructor(canvas: HTMLCanvasElement) {
        const gl = canvas.getContext('webgl');
        if (!gl) {
            throw new Error("WebGL not supported");
        }
        this.gl = gl;
        this.program = this.initShaders();
    }

    private initShaders(): WebGLProgram {
        const vsSource = `
            attribute vec4 aVertexPosition;
            attribute vec2 aTextureCoord;
            varying highp vec2 vTextureCoord;
            void main(void) {
                gl_Position = aVertexPosition;
                vTextureCoord = aTextureCoord;
            }
        `;

        const fsSource = `
            varying highp vec2 vTextureCoord;
            uniform sampler2D uSampler;
            
            // Apply colormap mapping for lucid activations
            void main(void) {
                highp vec4 texelColor = texture2D(uSampler, vTextureCoord);
                highp float intensity = (texelColor.r + texelColor.g + texelColor.b) / 3.0;
                
                // Plasma-like colormap approximation
                gl_FragColor = vec4(intensity * 1.2, intensity * 0.5, 1.0 - intensity, 1.0);
            }
        `;

        const vertexShader = this.loadShader(this.gl.VERTEX_SHADER, vsSource);
        const fragmentShader = this.loadShader(this.gl.FRAGMENT_SHADER, fsSource);

        const shaderProgram = this.gl.createProgram()!;
        this.gl.attachShader(shaderProgram, vertexShader);
        this.gl.attachShader(shaderProgram, fragmentShader);
        this.gl.linkProgram(shaderProgram);

        if (!this.gl.getProgramParameter(shaderProgram, this.gl.LINK_STATUS)) {
            throw new Error('Unable to initialize the shader program');
        }

        return shaderProgram;
    }

    private loadShader(type: number, source: string): WebGLShader {
        const shader = this.gl.createShader(type)!;
        this.gl.shaderSource(shader, source);
        this.gl.compileShader(shader);

        if (!this.gl.getShaderParameter(shader, this.gl.COMPILE_STATUS)) {
            this.gl.deleteShader(shader);
            throw new Error('An error occurred compiling the shaders');
        }
        return shader;
    }

    public renderActivationMap(textureData: Uint8Array, width: number, height: number) {
        this.gl.useProgram(this.program);
        
        const texture = this.gl.createTexture();
        this.gl.bindTexture(this.gl.TEXTURE_2D, texture);
        
        this.gl.texImage2D(
            this.gl.TEXTURE_2D, 0, this.gl.RGBA, width, height, 0, 
            this.gl.RGBA, this.gl.UNSIGNED_BYTE, textureData
        );
        
        this.gl.texParameteri(this.gl.TEXTURE_2D, this.gl.TEXTURE_MIN_FILTER, this.gl.LINEAR);
        this.gl.texParameteri(this.gl.TEXTURE_2D, this.gl.TEXTURE_WRAP_S, this.gl.CLAMP_TO_EDGE);
        this.gl.texParameteri(this.gl.TEXTURE_2D, this.gl.TEXTURE_WRAP_T, this.gl.CLAMP_TO_EDGE);

        // Define geometry (fullscreen quad) and draw
        // (Geometry definition omitted for brevity, assumes standard quad buffer setup)
        this.gl.drawArrays(this.gl.TRIANGLE_STRIP, 0, 4);
    }
}
