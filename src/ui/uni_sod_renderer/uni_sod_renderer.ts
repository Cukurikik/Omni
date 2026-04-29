class UniSODUIError extends Error {
    constructor(message: string) {
        super(message);
        this.name = "UniSODUIError";
    }
}

class Result<T> {
    public value: T | null;
    public error: Error | null;

    constructor(value: T | null, error: Error | null = null) {
        this.value = value;
        this.error = error;
    }

    isOk(): boolean {
        return this.error === null;
    }

    unwrap(): T {
        if (!this.isOk()) {
            throw this.error;
        }
        return this.value as T;
    }
}

/**
 * OMNI Engine: unisod-renderer
 * WebGL limits for rendering Unified Salient Object Detection depth maps in browser geometry.
 */
export class UniSODRendererEngine {
    private maxTextureSize: number;

    constructor(glMaxTextureLimit: number = 4096) {
        this.maxTextureSize = glMaxTextureLimit;
    }

    public prepareDepthMapTexture(width: number, height: number): Result<{ textureReady: boolean, u_depthFactor: number }> {
        try {
            if (width <= 0 || height <= 0) {
                return new Result(null, new UniSODUIError("Depth map matrix dimensionally invalid or zero"));
            }

            if (width > this.maxTextureSize || height > this.maxTextureSize) {
                 return new Result(null, new UniSODUIError(`Texture size constraint ${this.maxTextureSize}x${this.maxTextureSize} shattered by WebGL DOM mapping`));
            }

            // Normalization uniform to scale depth correctly
            const depthFactor = 1.0 / Math.max(width, height);

            return new Result({
                textureReady: true,
                u_depthFactor: depthFactor
            });

        } catch (e: any) {
            return new Result(null, new UniSODUIError(`UniSOD WebGL failure: ${e.message}`));
        }
    }
}
