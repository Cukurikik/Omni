// Omni API for AutoML Pipeline
export interface AutoMLModelCandidate {
    modelId: string;
    architectureHash: string;
    validationAccuracy: number;
}

export class OmniAutoMLAPI {
    static selectBestCandidate(candidates: AutoMLModelCandidate[]): AutoMLModelCandidate | null {
        if (!candidates || candidates.length === 0) return null;
        return candidates.reduce((prev, current) => 
            (current.validationAccuracy > prev.validationAccuracy) ? current : prev
        );
    }
}
