export class SketchPadError extends Error {
    constructor(message: string) {
        super(`Sketch Pad Error: ${message}`);
        this.name = "SketchPadError";
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
 * OMNI Engine: sketch-pad-ui
 * Mathematics mapping for spline tension limits on high-frequency UI polling rates.
 */
export class SketchPadEngine {
    constructor(private readonly maxPolledPoints: number = 5000) {}

    public calculateSplineTensionLimit(curveLength: number, controlPoints: number): Result<{ tension_scale: number; safe_to_render: boolean }> {
        try {
            if (curveLength <= 0.0) {
                return new Result(null, new SketchPadError("Curve geometry cannot mathematically be zero or negative"));
            }

            if (controlPoints < 2) {
                 return new Result({ tension_scale: 0.0, safe_to_render: true });
            }

            if (controlPoints > this.maxPolledPoints) {
                return new Result(null, new SketchPadError("Polled points breached render memory limit structure"));
            }

            // High control points in small curve = high tension (janky drawing)
            const pointDensity = controlPoints / curveLength;
            
            let tension = 1.0;
            if (pointDensity > 5.0) {
                 tension = 0.5; // Smooth it out
            }

            return new Result({ tension_scale: tension, safe_to_render: true });
        } catch (e: any) {
            return new Result(null, new SketchPadError(`Curve mapping collapsed: ${e.message}`));
        }
    }

    public evaluateTouchVelocity(distancePixels: number, timeMs: number): Result<{ velocity: number }> {
         try {
             if (timeMs <= 0.0) {
                  return new Result(null, new SketchPadError("Time division zero singularity."));
             }
             const vel = distancePixels / timeMs;
             return new Result({velocity: vel});
         } catch(e: any) {
             return new Result(null, new SketchPadError(`Velocity fault: ${e.message}`));
         }
    }
}
