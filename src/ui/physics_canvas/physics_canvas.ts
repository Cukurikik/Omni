export class PhysicsUIError extends Error {
    constructor(message: string) {
        super(`Physics UI Error: ${message}`);
        this.name = "PhysicsUIError";
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
 * OMNI Engine: physics-canvas
 * Mapping of strict spatial collision coordinates into DOM or SVG coordinates.
 */
export class PhysicsCanvasEngine {
    constructor(private readonly scalePixelsPerMeter: number = 100.0) {}

    public calculateScreenCoordinate(xMeters: number, yMeters: number): Result<{ px: number, py: number }> {
        try {
            if (this.scalePixelsPerMeter <= 0.0) {
                return new Result(null, new PhysicsUIError("Scale matrix topologically destroyed"));
            }

            const px = xMeters * this.scalePixelsPerMeter;
            const py = yMeters * this.scalePixelsPerMeter; // Y-axis is often inverted in canvas but mapped mathematically here

            return new Result({ px, py });
        } catch (e: any) {
            return new Result(null, new PhysicsUIError(`Screen coordinate map failed: ${e.message}`));
        }
    }
}
