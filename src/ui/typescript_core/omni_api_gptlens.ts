export interface AuditReport {
    contractName: string;
    vulnerabilitiesFound: number;
}

export class OmniGPTLensAPI {
    /** OMNI Interface Layer: GPTLens API */
    public static printSummary(report: AuditReport): string {
        return `GPTLens Audit [${report.contractName}]: ${report.vulnerabilitiesFound} issues.`;
    }
}
