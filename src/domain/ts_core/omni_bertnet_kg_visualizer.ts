// Omni BertNet KG Visualizer Domain (TypeScript)
// Ref: tanyuqian/knowledge-harvest-from-lms
export interface Triple { head: string; relation: string; tail: string; confidence: number; }
export function filterHighConfidence(triples: Triple[], threshold: number = 0.5): Triple[] {
  return triples.filter(t => t.confidence >= threshold);
}
export function graphStats(triples: Triple[]): { nodes: number; edges: number; avgConf: number } {
  const entities = new Set<string>(); triples.forEach(t => { entities.add(t.head); entities.add(t.tail); });
  const avg = triples.length > 0 ? triples.reduce((s, t) => s + t.confidence, 0) / triples.length : 0;
  return { nodes: entities.size, edges: triples.length, avgConf: Math.round(avg * 1e4) / 1e4 };
}
