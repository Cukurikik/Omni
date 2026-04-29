// Omni UoT Question Planner Domain (TypeScript)
// Ref: zhiyuanhubj/UoT — NeurIPS 2024
interface Question { text: string; relevance: number[]; }
interface PlanResult { question: Question; expectedInfoGain: number; }
export function entropy(probs: number[]): number {
  return -probs.reduce((s, p) => p > 1e-12 ? s + p * Math.log2(p) : s, 0);
}
export function selectBestQuestion(questions: Question[], hypotheses: number[]): PlanResult {
  let best: PlanResult = { question: questions[0], expectedInfoGain: -1 };
  for (const q of questions) {
    const posterior = hypotheses.map((h, i) => h * (q.relevance[i] || 1));
    const total = posterior.reduce((s, v) => s + v, 0) || 1;
    const norm = posterior.map(v => v / total);
    const ig = Math.max(entropy(hypotheses) - entropy(norm), 0);
    if (ig > best.expectedInfoGain) { best = { question: q, expectedInfoGain: Math.round(ig * 1e6) / 1e6 }; }
  }
  return best;
}
