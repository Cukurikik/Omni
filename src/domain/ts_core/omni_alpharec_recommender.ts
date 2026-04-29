// Omni AlphaRec Recommender Domain (TypeScript)
// Ref: LehengTHU/AlphaRec — ICLR 2025
export interface ItemProfile { id: string; embedding: number[]; metadata: string; }
export function graphConv(nodeEmb: number[], neighborEmbs: number[][], selfWeight: number = 0.5): number[] {
  if (!neighborEmbs.length) return nodeEmb;
  const d = nodeEmb.length;
  const agg = Array.from({length: d}, (_, i) => neighborEmbs.reduce((s, n) => s + n[i], 0) / neighborEmbs.length);
  return nodeEmb.map((v, i) => Math.round((selfWeight * v + (1 - selfWeight) * agg[i]) * 1e8) / 1e8);
}
export function ndcgAtK(ranked: string[], relevant: Set<string>, k: number): number {
  let dcg = 0, idcg = 0;
  for (let i = 0; i < k; i++) {
    if (i < ranked.length && relevant.has(ranked[i])) dcg += 1 / Math.log2(i + 2);
    if (i < relevant.size) idcg += 1 / Math.log2(i + 2);
  }
  return idcg === 0 ? 0 : Math.round(dcg / idcg * 1e6) / 1e6;
}
