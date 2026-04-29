// Omni ClassEval Benchmark Runner (TypeScript)
// Domain Layer: Class-level code generation evaluation.
// Ref: FudanSELab/ClassEval — Benchmark for class-level code gen.
interface ClassEvalResult { className: string; methodsPassed: number; totalMethods: number; passRate: number; }
export function evaluateClass(name: string, passed: number, total: number): ClassEvalResult {
  const rate = total > 0 ? Math.round((passed / total) * 1e6) / 1e6 : 0;
  return { className: name, methodsPassed: passed, totalMethods: total, passRate: rate };
}
export function aggregateResults(results: ClassEvalResult[]): number {
  if (!results.length) return 0;
  return Math.round(results.reduce((s, r) => s + r.passRate, 0) / results.length * 1e6) / 1e6;
}
