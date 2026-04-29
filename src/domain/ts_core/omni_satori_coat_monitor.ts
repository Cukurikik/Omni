// Omni Satori COAT Monitor (TypeScript)
// Ref: satori-reasoning/Satori — ICML'25
type COATAction = 'continue' | 'reflect' | 'explore';
interface TrajectoryStep { step: number; action: COATAction; confidence: number; }
export function analyzeTrajectory(steps: TrajectoryStep[]): { avgConf: number; explores: number; reflects: number } {
  const avg = steps.reduce((s, t) => s + t.confidence, 0) / Math.max(steps.length, 1);
  return { avgConf: Math.round(avg * 1e4) / 1e4,
           explores: steps.filter(s => s.action === 'explore').length,
           reflects: steps.filter(s => s.action === 'reflect').length };
}
export function coatEfficiency(steps: number, maxSteps: number, solved: boolean): number {
  const base = solved ? 1.0 : 0.0;
  return Math.round((base + 0.1 * (1 - steps / maxSteps)) * 1e4) / 1e4;
}
