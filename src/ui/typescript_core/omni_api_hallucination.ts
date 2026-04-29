export interface EvalReport {
    hallucinationScore: number;
    riskLevel: "Low" | "Medium" | "High";
}

export class OmniHallucinationAPI {
    /** OMNI Interface Layer: Hallucination Index API */
    public static generateReport(score: number): EvalReport {
        let risk: "Low" | "Medium" | "High" = "Low";
        if (score > 0.7) risk = "High";
        else if (score > 0.3) risk = "Medium";
        return { hallucinationScore: score, riskLevel: risk };
    }
}
