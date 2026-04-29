// Omni LooGLE Benchmark UI (TypeScript)
export interface LongCtxResult { task: string; f1: number; contextLength: number }
export function bucketByLength(results: LongCtxResult[]): Record<string, number> {
  const buckets: Record<string, number[]> = {};
  for (const r of results) {
    const b = r.contextLength < 4096 ? 'short' : r.contextLength < 16384 ? 'medium' : 'long';
    (buckets[b] ||= []).push(r.f1);
  }
  return Object.fromEntries(Object.entries(buckets).map(([k,v]) => [k, Math.round(v.reduce((a,b)=>a+b,0)/v.length*1e4)/1e4]));
}
