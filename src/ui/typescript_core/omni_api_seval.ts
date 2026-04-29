export interface SafetyReport {
    promptId: string;
    isSafe: boolean;
}

export class OmniSEvalAPI {
    /** OMNI Interface Layer: S-Eval API */
    public static flagContent(report: SafetyReport): string {
        return `[ALERT] Prompt ${report.promptId} flagged: ${!report.isSafe}`;
    }
}
