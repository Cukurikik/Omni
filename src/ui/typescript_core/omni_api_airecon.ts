export class OmniAIReconAPI {
    public static threatScore(indicators: number, totalRules: number, severityAvg: number): number {
        return totalRules > 0 ? (indicators / totalRules) * severityAvg : 0;
    }
}
