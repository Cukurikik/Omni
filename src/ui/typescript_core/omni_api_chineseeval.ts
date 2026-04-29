// Omni API for Chinese Evaluator
export interface CJEvaluationMetrics {
    bleuScore: number;
    rougeL: number;
    charCount: number;
}

export class OmniChineseEvalAPI {
    static formatEvaluationDashboard(metrics: CJEvaluationMetrics): object {
        return {
            dashboard_id: "cjk_metrics",
            metrics: {
                bleu_norm: (metrics.bleuScore * 100).toFixed(2) + "%",
                rouge_norm: (metrics.rougeL * 100).toFixed(2) + "%",
                length: metrics.charCount
            },
            status: metrics.bleuScore > 0.4 ? "PASS" : "FAIL"
        };
    }
}
