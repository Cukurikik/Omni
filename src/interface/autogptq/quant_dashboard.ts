export interface OmniResult<T> {
    value: T | null;
    error: string | null;
    isOk: boolean;
}

export class QuantDashboardUI {
    public displayCompressionRatio(originalSize: number, newSize: number): OmniResult<boolean> {
        if (originalSize <= 0 || newSize <= 0) {
            return { value: false, error: "Invalid sizes", isOk: false };
        }

        // TypeScript UI logic for displaying GPTQ memory savings
        const ratio = originalSize / newSize;
        console.log(`Compression Ratio: ${ratio.toFixed(2)}x`);
        
        return { value: true, error: null, isOk: true };
    }
}
