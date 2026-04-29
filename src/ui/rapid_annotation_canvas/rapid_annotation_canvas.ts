class RapidCanvasUIError extends Error {
    constructor(message: string) {
        super(message);
        this.name = "RapidCanvasUIError";
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
 * OMNI Engine: rapid-annotation-canvas
 * HTML Canvas 2D mapping for high-speed bounding box bounding constraints.
 */
export class RapidAnnotationCanvasEngine {
    private maxBoxesPerFrame: number;

    constructor(boxLimit: number = 100) {
        this.maxBoxesPerFrame = boxLimit;
    }

    public mapBoundingBoxToCanvas(x: number, y: number, w: number, h: number, canvasW: number, canvasH: number): Result<{ mappedX: number, mappedY: number, mappedW: number, mappedH: number }> {
        try {
            if (w <= 0 || h <= 0 || canvasW <= 0 || canvasH <= 0) {
                return new Result(null, new RapidCanvasUIError("Canvas or box geometry mapped to absolute 0 or negative space"));
            }

            if (x < 0 || y < 0 || (x + w) > canvasW || (y + h) > canvasH) {
                 return new Result(null, new RapidCanvasUIError("Bounding box mapping strictly escaped Canvas DOM bounds"));
            }

            return new Result({
                mappedX: x,
                mappedY: y,
                mappedW: w,
                mappedH: h
            });

        } catch (e: any) {
            return new Result(null, new RapidCanvasUIError(`Canvas math shattered: ${e.message}`));
        }
    }
}
