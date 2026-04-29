export class OmniAgentBenchmarkAPI {
    public static successRate(successes: number, total: number): number {
        return total > 0 ? successes / total : 0;
    }
    public static avgSteps(steps: number[]): number {
        return steps.length > 0 ? steps.reduce((s,v) => s+v, 0) / steps.length : 0;
    }
}
