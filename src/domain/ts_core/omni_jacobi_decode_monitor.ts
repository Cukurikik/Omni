// Omni JacobiForcing Decode Monitor (TypeScript)
// Domain: Parallel decoding convergence tracking.
// Ref: hao-ai-lab/JacobiForcing
interface DecodeStep { iteration: number; converged: boolean; changedTokens: number; }
export function trackConvergence(steps: DecodeStep[]): { avgIterations: number; convergeRate: number } {
  const converged = steps.filter(s => s.converged).length;
  const total = steps.length || 1;
  const avgIter = steps.reduce((s, d) => s + d.iteration, 0) / total;
  return { avgIterations: Math.round(avgIter * 100) / 100, convergeRate: Math.round(converged / total * 1e6) / 1e6 };
}
