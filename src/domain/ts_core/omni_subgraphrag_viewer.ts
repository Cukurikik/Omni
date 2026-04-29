// Omni SubgraphRAG KG Viewer (TypeScript)
export interface KGTriple { head: string; rel: string; tail: string }
export function triplesToContext(triples: KGTriple[], max: number = 50): string {
  return triples.slice(0, max).map(t => `${t.head} --[${t.rel}]--> ${t.tail}`).join('\n');
}
export function entityLink(query: string, vocab: string[], topK: number = 5): {entity: string; score: number}[] {
  const qt = new Set(query.toLowerCase().split(/\s+/));
  return vocab.map(e => {
    const et = new Set(e.toLowerCase().replace(/_/g,' ').split(/\s+/));
    const overlap = [...qt].filter(t => et.has(t)).length;
    return {entity: e, score: Math.round(overlap / Math.max(et.size, 1) * 1e4) / 1e4};
  }).filter(x => x.score > 0).sort((a,b) => b.score - a.score).slice(0, topK);
}
