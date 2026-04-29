// Omni API for ICSF Self-Correct Evaluation
export interface ConsensusResult {
    originalAnswer: string;
    refinedAnswer: string;
    iterations: number;
    consensusReached: boolean;
}

export class OmniICSFAPI {
    static packageRefinementResult(result: ConsensusResult): object {
        return {
            status: result.consensusReached ? "stable" : "divergent",
            final_output: result.refinedAnswer,
            compute_cost_iterations: result.iterations,
            changed: result.originalAnswer !== result.refinedAnswer
        };
    }
}
