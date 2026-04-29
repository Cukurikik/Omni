export interface OmniResult<T> {
    value: T | null;
    error: string | null;
    isOk: boolean;
}

export class CompressionDashboard {
    public updateRatio(originalSize: number, compressedSize: number): OmniResult<number> {
        if (originalSize <= 0 || compressedSize <= 0) {
            return { value: null, error: "Invalid sizes", isOk: false };
        }

        // TypeScript UI logic for displaying AutoAWQ compression ratio
        const ratio = originalSize / compressedSize;
        console.log(`Compression ratio: ${ratio.toFixed(2)}x`);
        
        return { value: ratio, error: null, isOk: true };
    }
}
