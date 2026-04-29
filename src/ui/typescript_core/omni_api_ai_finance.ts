export class OmniAIFinanceAPI {
    public static sharpeRatio(returns: number[], riskFree: number = 0): number {
        if (returns.length <= 1) return 0;
        const excess = returns.map(r => r - riskFree);
        const mean = excess.reduce((s,v) => s+v, 0) / excess.length;
        const variance = excess.reduce((s,v) => s + (v-mean)**2, 0) / excess.length;
        return variance > 0 ? mean / Math.sqrt(variance) : 0;
    }
}
