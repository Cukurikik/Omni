export interface TrajectoryResult {
    agentId: string;
    finalScore: number;
}

export class OmniAgentBenchAPI {
    /** OMNI Interface Layer: AgentBench API */
    public static renderLeaderboard(result: TrajectoryResult): string {
        return `Agent ${result.agentId} achieved score: ${result.finalScore.toFixed(2)}`;
    }
}
