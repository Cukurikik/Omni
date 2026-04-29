export interface ContamReport {
    datasetId: string;
    overlapRatio: number;
}

export class OmniDataContamAPI {
    /** OMNI Interface Layer: Data Contamination API */
    public static isContaminated(report: ContamReport): boolean {
        return report.overlapRatio > 0.05; // 5% threshold
    }
}
