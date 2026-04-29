export class BiModUIError extends Error {
    constructor(message: string) {
        super(`BiModal UI Error: ${message}`);
        this.name = "BiModUIError";
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
 * OMNI Engine: bimod-dash
 * DOM binding mapping logic for rendering neurological brain coupling tensors.
 */
export class BiModNeuroDashboardEngine {
    constructor(private readonly maxRenderNodes: number = 256) {}

    public calculateNodeColorGradient(couplingIndex: number): Result<{ hex: string, brightness: number }> {
        try {
            if (couplingIndex < 0.0) {
                return new Result(null, new BiModUIError("Coupling index topologically impossible"));
            }

            // Normalization mapping from 0 to 10 (hypothetical cap)
            const normalized = Math.min(couplingIndex / 10.0, 1.0);
            
            // Red gradient for high cortical activation
            const r = Math.floor(normalized * 255);
            const g = Math.floor((1.0 - normalized) * 100);
            const b = 50;

            const hex = `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;

            return new Result({ hex, brightness: normalized });
        } catch (e: any) {
            return new Result(null, new BiModUIError(`Gradient mapper collapsed: ${e.message}`));
        }
    }
}
