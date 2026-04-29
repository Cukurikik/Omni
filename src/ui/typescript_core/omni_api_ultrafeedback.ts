export interface FeedbackMetrics {
    modelId: string;
    score: number;
}

export class OmniUltraFeedbackAPI {
    /** OMNI Interface Layer: UltraFeedback API */
    public static submitMetrics(metrics: FeedbackMetrics): boolean {
        return metrics.score >= 0.0 && metrics.score <= 10.0;
    }
}
