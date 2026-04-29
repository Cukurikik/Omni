// Omni MOELoRA Domain (TypeScript)
export interface GateOutput { expertWeights: number[]; selectedExpert: number }
export function softmaxGate(logits: number[]): GateOutput {
  const mx = Math.max(...logits); const exps = logits.map(l => Math.exp(l-mx));
  const s = exps.reduce((a,b)=>a+b,0); const weights = exps.map(e => Math.round(e/s*1e6)/1e6);
  return { expertWeights: weights, selectedExpert: weights.indexOf(Math.max(...weights)) };
}
