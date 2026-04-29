// Omni DeCo Hallucination Monitor (TypeScript)
// Domain Layer: Real-time hallucination detection metrics.
// Ref: zjunlp/Deco — ICLR 2025
interface HallucinationMetric { tokenIdx: number; correctionApplied: boolean; confidence: number; }
export function computeHallucinationRate(metrics: HallucinationMetric[]): number {
  if (!metrics.length) return 0;
  const corrected = metrics.filter(m => m.correctionApplied).length;
  return Math.round((corrected / metrics.length) * 1e6) / 1e6;
}
export function isHighRisk(rate: number, threshold: number = 0.3): boolean {
  return rate > threshold;
}
