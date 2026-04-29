export interface SolverRequest {
    problemStatement: string;
    maxTokens: number;
}

export class OmniFlacunaAPI {
    /** OMNI Interface Layer: Flacuna API */
    public static initiateSolve(req: SolverRequest): string {
        return `Solving problem (Max: ${req.maxTokens}T)`;
    }
}
