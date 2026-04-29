export interface OptimizationStep {
    iteration: number;
    improved: boolean;
}

export class OmniLMOpsAPI {
    /** OMNI Interface Layer: LMOps API */
    public static stepReport(step: OptimizationStep): string {
        return `LMOps Iteration ${step.iteration}: Improvement = ${step.improved}`;
    }
}
