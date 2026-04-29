export class OmniAnime4KAPI {
    public static bicubicWeight(x: number): number {
        const ax = Math.abs(x);
        if (ax <= 1) return (1.5 * ax - 2.5) * ax * ax + 1;
        if (ax <= 2) return ((-0.5 * ax + 2.5) * ax - 4) * ax + 2;
        return 0;
    }
}
