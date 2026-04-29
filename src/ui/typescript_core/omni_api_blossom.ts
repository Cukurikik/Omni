// Omni API for BlossomLM Dataset Management
export interface DatasetStats {
    totalRecords: number;
    uniqueRecords: number;
    duplicationRate: number;
}

export class OmniBlossomAPI {
    static generateDatasetReport(total: number, unique: number): DatasetStats {
        const dupRate = total > 0 ? ((total - unique) / total) * 100 : 0.0;
        return {
            totalRecords: total,
            uniqueRecords: unique,
            duplicationRate: parseFloat(dupRate.toFixed(2))
        };
    }
}
