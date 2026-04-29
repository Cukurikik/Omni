// Omni TIFA Faithfulness Dashboard (TypeScript)
export interface TIFAResult { prompt: string; score: number; nQuestions: number; nCorrect: number }
export function computeTifa(answers: {correct: boolean}[]): number {
  if (!answers.length) return 0;
  return Math.round(answers.filter(a => a.correct).length / answers.length * 1e4) / 1e4;
}
export function elementBreakdown(answers: {type: string; correct: boolean}[]): Record<string, number> {
  const buckets: Record<string, {c: number; t: number}> = {};
  for (const a of answers) { const b = buckets[a.type] ||= {c:0,t:0}; b.t++; if (a.correct) b.c++; }
  return Object.fromEntries(Object.entries(buckets).map(([k,v]) => [k, Math.round(v.c/v.t*1e4)/1e4]));
}
