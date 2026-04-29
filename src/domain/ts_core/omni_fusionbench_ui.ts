// Omni FusionBench Model Merger UI (TypeScript)
// Ref: tanganke/fusion_bench — MIT
export interface MergeConfig { method: string; scaling: number; topK: number; models: string[]; }
export interface MergeMetrics { conflictRate: number; paramDelta: number; }

export function validateConfig(config: MergeConfig): { valid: boolean; errors: string[] } {
  const errors: string[] = [];
  if (!['task_arithmetic', 'ties', 'dare', 'fisher'].includes(config.method)) errors.push(`Unknown method: ${config.method}`);
  if (config.scaling < 0 || config.scaling > 2) errors.push('Scaling must be 0-2');
  if (config.models.length < 2) errors.push('Need at least 2 models');
  return { valid: errors.length === 0, errors };
}

export function estimateMergeTime(nParams: number, nModels: number, method: string): number {
  const base = nParams / 1e6 * 0.1; // 0.1ms per million params
  const factor = method === 'fisher' ? 3 : method === 'ties' ? 1.5 : 1;
  return Math.round(base * nModels * factor * 100) / 100;
}
