export interface DecodeMetrics {
    iterations: number;
    speedupRatio: number;
}

export class OmniJacobiAPI {
    /** OMNI Interface Layer: Jacobi API */
    public static calculateEfficiency(metrics: DecodeMetrics): number {
        if (metrics.iterations === 0) return 0;
        return metrics.speedupRatio / metrics.iterations;
    }
}
