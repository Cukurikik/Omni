export class OmniAROBowAPI {
    public static recall(correct: number, total: number): number {
        return total > 0 ? correct / total : 0;
    }
    public static mrr(ranks: number[]): number {
        if (ranks.length === 0) return 0;
        return ranks.filter(r => r > 0).reduce((s, r) => s + 1 / r, 0) / ranks.length;
    }
}
