export class OmniArxivTimesAPI {
    public static hIndex(citations: number[]): number {
        const sorted = [...citations].sort((a, b) => b - a);
        let h = 0;
        for (let i = 0; i < sorted.length; ++i) if (sorted[i] >= i + 1) h = i + 1;
        return h;
    }
}
