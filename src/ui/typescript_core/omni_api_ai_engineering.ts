export class OmniAIEngineeringAPI {
    public static tokenBudget(promptTokens: number, maxTokens: number, reserve: number): number {
        return Math.max(0, maxTokens - promptTokens - reserve);
    }
    public static latencyP99(latencies: number[]): number {
        if (latencies.length === 0) return 0;
        const sorted = [...latencies].sort((a,b) => a-b);
        return sorted[Math.floor(0.99 * (sorted.length - 1))];
    }
}
