// Omni Anchoring App Evaluator (TypeScript)
// Domain Layer: Pipeline evaluation framework for no-code LLM apps.
// Ref: AnchoringAI/anchoring-ai
interface EvalResult { pipelineHash: string; latencyMs: number; tokenCost: number; quality: number; }
export function evaluatePipeline(hash: string, latency: number, tokens: number, quality: number): EvalResult {
  return { pipelineHash: hash, latencyMs: Math.max(0, latency), tokenCost: Math.max(0, tokens),
           quality: Math.round(Math.max(0, Math.min(1, quality)) * 1e6) / 1e6 };
}
export function comparePipelines(a: EvalResult, b: EvalResult): string {
  if (a.quality > b.quality) return a.pipelineHash;
  if (b.quality > a.quality) return b.pipelineHash;
  return a.latencyMs <= b.latencyMs ? a.pipelineHash : b.pipelineHash;
}
