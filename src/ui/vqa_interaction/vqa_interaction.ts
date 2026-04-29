export class VQAUIError extends Error {
    constructor(message: string) {
        super(`VQA UI Error: ${message}`);
        this.name = "VQAUIError";
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
 * OMNI Engine: vqa-ui
 * Focus mapping logic checking visual bounds corresponding to question focus areas.
 */
export class VQAInteractionEngine {
    constructor(private readonly clickToleranceRadius: number = 20.0) {}

    public checkBoundingBoxFocusIntersect(pointerX: number, pointerY: number, boxOriginX: number, boxOriginY: number, boxW: number, boxH: number): Result<{ isIntersecting: boolean }> {
        try {
            if (boxW < 0 || boxH < 0) {
                 return new Result(null, new VQAUIError("Box dimension topologies physically unaligned"));
            }

            const inXBounds = pointerX >= (boxOriginX - this.clickToleranceRadius) && pointerX <= (boxOriginX + boxW + this.clickToleranceRadius);
            const inYBounds = pointerY >= (boxOriginY - this.clickToleranceRadius) && pointerY <= (boxOriginY + boxH + this.clickToleranceRadius);

            return new Result({ isIntersecting: inXBounds && inYBounds });
        } catch (e: any) {
            return new Result(null, new VQAUIError(`Intersect topology fault: ${e.message}`));
        }
    }
}
