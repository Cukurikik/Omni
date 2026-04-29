// Omni XRec Explainable Rec UI (TypeScript)
export interface RecResult { itemId: string; score: number; explanation: string }
export function topKRecommend(userEmb: number[], items: {id: string; emb: number[]}[], k: number = 10): RecResult[] {
  return items.map(it => {
    const dot = userEmb.reduce((s, u, i) => s + u * (it.emb[i]||0), 0);
    const score = Math.round(1 / (1 + Math.exp(-dot)) * 1e4) / 1e4;
    return {itemId: it.id, score, explanation: `Score: ${score}`};
  }).sort((a,b) => b.score - a.score).slice(0, k);
}
