export class QuantumUIError extends Error {
    constructor(message: string) {
        super(`Quantum UI Error: ${message}`);
        this.name = "QuantumUIError";
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
 * OMNI Engine: q-projector-ui
 * Renders superposition arrays into 3D view frustums with probability sphere mapping.
 */
export class QuantumProjectorEngine {
    constructor(private readonly maxRenderSpheres: number = 2000) {}

    public calculateProbabilityRadius(amplitude: number, maxRadius: number): Result<{ render_radius: number }> {
        try {
            if (maxRadius <= 0.0) {
                return new Result(null, new QuantumUIError("Max radius bounds mathematically zero"));
            }

            // Probability is square of amplitude (Born Rule) mapped to screen space radius
            const probability = Math.pow(amplitude, 2);
            
            if (probability > 1.0 || probability < 0.0) {
                 return new Result(null, new QuantumUIError("Probability boundary violated in amplitude parsing"));
            }

            const radius = Math.sqrt(probability) * maxRadius;

            return new Result({ render_radius: radius });
        } catch (e: any) {
            return new Result(null, new QuantumUIError(`Radius logic broke: ${e.message}`));
        }
    }

    public validateRenderOverload(activeSpheres: number): Result<{ safe_to_draw: boolean }> {
         try {
             if (activeSpheres < 0) {
                  return new Result(null, new QuantumUIError("Geometrically impossible negative sphere count"));
             }
             
             return new Result({ safe_to_draw: activeSpheres <= this.maxRenderSpheres });
         } catch(e: any) {
             return new Result(null, new QuantumUIError(`Overload map fault: ${e.message}`));
         }
    }
}
