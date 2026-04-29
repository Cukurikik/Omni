export interface EvalResult {
    score: number;
    isHallucinated: boolean;
}

export class OmniHalluQAAPI {
    /** OMNI Interface Layer: HalluQA API */
    public static analyzeScore(score: number, threshold: number = 0.5): EvalResult {
        return {
            score,
            isHallucinated: score > threshold
        };
    }

    public static generateReport(results: EvalResult[]): string {
        const total = results.length;
        const hal = results.filter(r => r.isHallucinated).length;
        return `Hallucination Rate: ${((hal/total)*100).toFixed(1)}%`;
    }
}
