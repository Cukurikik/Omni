export class OmniAllenNLPAPI {
    public static spanF1(tp: number, fp: number, fn: number): number {
        if (tp <= 0) return 0;
        const p = tp / (tp + fp), r = tp / (tp + fn);
        return 2 * p * r / (p + r);
    }
}
