export interface FinancialReport {
    documentId: string;
    text: string;
}

export class OmniFinanceLLMAPI {
    /** OMNI Interface Layer: Finance LLMs API */
    public static buildAnalysisPrompt(report: FinancialReport): string {
        return `Analyze financial risk for doc ${report.documentId}:\n${report.text}`;
    }
}
