export class HubbleUIError extends Error {
    constructor(message: string) {
        super(`Hubble UI Error: ${message}`);
        this.name = "HubbleUIError";
    }
}

export class Result<T> {
    constructor(public readonly value: T | null, public readonly error: Error | null = null) {}

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
 * OMNI Engine: hubble-visualizer
 * Spatial plotting logic for multidimensional spectra geometries on 2D screens.
 */
export class HubbleVisualizerEngine {
    constructor(private readonly screenWidth: number, private readonly screenHeight: number) {}

    public calculateScreenProjectionBounds(distanceParsecs: number, maxRenderDistance: number): Result<{ scale_factor: number; is_visible: boolean }> {
        try {
            if (distanceParsecs <= 0 || maxRenderDistance <= 0) {
                return new Result(null, new HubbleUIError("Distance metrics geometrically invalid"));
            }

            if (distanceParsecs > maxRenderDistance) {
                return new Result({ scale_factor: 0.0, is_visible: false });
            }

            // Inverse square scaling approximation for rendering
            const scaleFactor = 1.0 / Math.pow((distanceParsecs / maxRenderDistance) + 1.0, 2);

            return new Result({ scale_factor: scaleFactor, is_visible: true });
        } catch (e: any) {
            return new Result(null, new HubbleUIError(`Projection calculation failed: ${e.message}`));
        }
    }

    public validateViewFrustum(x: number, y: number, zDepth: number): Result<{ in_frustum: boolean }> {
        try {
             if (zDepth < 0.1 || zDepth > 1000.0) {
                  return new Result({in_frustum: false});
             }
             
             // Simple ortho frustum check
             const isInX = x >= 0 && x <= this.screenWidth;
             const isInY = y >= 0 && y <= this.screenHeight;
             
             return new Result({in_frustum: isInX && isInY});
        } catch(e: any) {
             return new Result(null, new HubbleUIError(`Frustum map failed: ${e.message}`));
        }
    }
}
