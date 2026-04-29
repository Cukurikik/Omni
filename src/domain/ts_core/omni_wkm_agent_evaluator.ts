// Omni WKM Agent Evaluator (TypeScript)
// Domain Layer: Type-safe evaluation framework for World Knowledge Model agent plans.
// Ref: zjunlp/WKM — NeurIPS 2024

interface PlanStep {
  action: string;
  preconditions: string[];
  effects: string[];
  confidence: number;
}

interface EvaluationResult {
  feasibility: number;
  stepCount: number;
  weakestLink: string;
}

export function evaluatePlan(steps: PlanStep[]): EvaluationResult {
  if (steps.length === 0) {
    return { feasibility: 0, stepCount: 0, weakestLink: 'EMPTY_PLAN' };
  }
  let minConf = 1.0;
  let weakest = '';
  let product = 1.0;
  for (const s of steps) {
    const c = Math.max(0, Math.min(1, s.confidence));
    product *= c;
    if (c < minConf) { minConf = c; weakest = s.action; }
  }
  return { feasibility: Math.round(product * 1e8) / 1e8, stepCount: steps.length, weakestLink: weakest };
}
