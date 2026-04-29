// Omni UHGEval Hallucination Dashboard (TypeScript)
export function hallucinationRatio(responseTokens: string[], refTokens: string[]): number {
  const refSet = new Set(refTokens.map(t => t.toLowerCase()));
  const ungrounded = responseTokens.filter(t => !refSet.has(t.toLowerCase())).length;
  return Math.round(ungrounded / Math.max(responseTokens.length, 1) * 1e4) / 1e4;
}
export function benchmarkScore(taskScores: number[]): {mean: number; min: number; max: number} {
  if (!taskScores.length) return {mean: 0, min: 0, max: 0};
  return {mean: Math.round(taskScores.reduce((a,b)=>a+b,0)/taskScores.length*1e4)/1e4, min: Math.min(...taskScores), max: Math.max(...taskScores)};
}
