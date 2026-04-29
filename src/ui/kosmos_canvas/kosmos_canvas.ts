export class KosmosUIError extends Error {
    constructor(message: string) {
        super(`Kosmos UI Error: ${message}`);
        this.name = "KosmosUIError";
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
 * OMNI Engine: kosmos-ui
 * Interweaves text and visual token spans across grid bounds on the frontend.
 */
export class KosmosCanvasEngine {
    constructor(private readonly maxSpanTokens: number = 2048) {}

    public calculateInterleavedCanvasLayout(textTokens: number, visualTokens: number, containerWidthPx: number): Result<{ spanPixelWidth: number }> {
        try {
            if (containerWidthPx <= 0) {
                return new Result(null, new KosmosUIError("Container dimensions negative"));
            }

            const totalTokens = textTokens + visualTokens;
            if (totalTokens > this.maxSpanTokens) {
                return new Result(null, new KosmosUIError("Token bounds physically exceed frontend layout limits"));
            }

            if (totalTokens === 0) {
                 return new Result({ spanPixelWidth: 0 });
            }

            const widthPerToken = containerWidthPx / totalTokens;

            return new Result({ spanPixelWidth: widthPerToken });
        } catch (e: any) {
            return new Result(null, new KosmosUIError(`Canvas reflow triggered fault: ${e.message}`));
        }
    }
}
