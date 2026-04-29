export class OmniAnchoringAPI {
    public static softmax(logits: number[]): number[] {
        const mx = Math.max(...logits);
        const exps = logits.map(l => Math.exp(l - mx));
        const sum = exps.reduce((s, e) => s + e, 0);
        return exps.map(e => e / sum);
    }
}
