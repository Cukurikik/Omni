export interface BenchmarkResult {
    agentId: string;
    finalScore: number;
}

export class OmniDSBenchAPI {
    /** OMNI Interface Layer: DSBench API */
    public static publishResult(res: BenchmarkResult): string {
        return `Agent ${res.agentId} achieved DSBench score: ${res.finalScore.toFixed(2)}`;
    }
}
