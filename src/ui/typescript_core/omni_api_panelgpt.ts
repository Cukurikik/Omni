// Omni API for PanelGPT Multi-Expert Panel
export interface ExpertResponse {
    expertId: string;
    answer: string;
    confidence: number;
}

export class OmniPanelGPTAPI {
    static aggregatePanelResponses(responses: ExpertResponse[]): ExpertResponse | null {
        if (!responses || responses.length === 0) return null;
        
        // Return the highest confidence response as the panel consensus
        return responses.reduce((prev, current) => {
            return (current.confidence > prev.confidence) ? current : prev;
        });
    }
}
