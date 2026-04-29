export class OmniAIMETAPI {
    public static quantize(value: number, scale: number, bits: number): number {
        const maxVal = (1 << (bits - 1)) - 1;
        let q = Math.round(value / scale);
        q = Math.max(-maxVal, Math.min(maxVal, q));
        return q * scale;
    }
}
