export class OmniA2SummAPI {
    public static rougeL(lcsLen: number, refLen: number, hypLen: number): number {
        if (refLen <= 0 || hypLen <= 0) return 0;
        const p = lcsLen / hypLen, r = lcsLen / refLen;
        return (p + r > 0) ? 2 * p * r / (p + r) : 0;
    }
}
