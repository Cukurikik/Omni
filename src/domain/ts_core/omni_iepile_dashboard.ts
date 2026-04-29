// Omni IEPile Extraction Dashboard (TypeScript)
// Ref: zjunlp/IEPile — ACL 2024
export interface ExtractedEntity { text: string; type: string; start: number; end: number; }
export interface IEMetrics { precision: number; recall: number; f1: number; }

export function computeF1(predicted: ExtractedEntity[], gold: ExtractedEntity[]): IEMetrics {
  const predSet = new Set(predicted.map(e => `${e.text}:${e.type}`));
  const goldSet = new Set(gold.map(e => `${e.text}:${e.type}`));
  let tp = 0;
  predSet.forEach(e => { if (goldSet.has(e)) tp++; });
  const precision = tp / Math.max(predSet.size, 1);
  const recall = tp / Math.max(goldSet.size, 1);
  const f1 = precision + recall > 0 ? 2 * precision * recall / (precision + recall) : 0;
  return { precision: Math.round(precision * 1e4) / 1e4, recall: Math.round(recall * 1e4) / 1e4,
           f1: Math.round(f1 * 1e4) / 1e4 };
}

export function groupByType(entities: ExtractedEntity[]): Record<string, ExtractedEntity[]> {
  const groups: Record<string, ExtractedEntity[]> = {};
  entities.forEach(e => { (groups[e.type] ||= []).push(e); });
  return groups;
}
