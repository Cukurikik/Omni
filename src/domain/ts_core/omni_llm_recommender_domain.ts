// Omni LLM Recommender Domain (TypeScript)
// Ref: liuqidong07/Awesome-LLM-Enhanced-Recommender-Systems
interface RecItem { id: string; score: number; source: 'knowledge' | 'interaction' | 'model'; }
export function mergeEnhancements(knowledge: RecItem[], interaction: RecItem[], model: RecItem[]): RecItem[] {
  const all = [...knowledge, ...interaction, ...model];
  const map = new Map<string, RecItem>();
  for (const item of all) {
    const existing = map.get(item.id);
    if (!existing || item.score > existing.score) map.set(item.id, item);
  }
  return Array.from(map.values()).sort((a, b) => b.score - a.score);
}
export function ndcg(ranked: string[], relevant: Set<string>, k: number): number {
  let dcg = 0, idcg = 0;
  for (let i = 0; i < k; i++) {
    if (i < ranked.length && relevant.has(ranked[i])) dcg += 1 / Math.log2(i + 2);
    if (i < relevant.size) idcg += 1 / Math.log2(i + 2);
  }
  return idcg === 0 ? 0 : Math.round(dcg / idcg * 1e6) / 1e6;
}
