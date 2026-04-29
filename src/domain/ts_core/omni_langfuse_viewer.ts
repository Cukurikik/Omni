// Omni Langfuse Trace Viewer (TypeScript)
export interface Span { name: string; latencyMs: number; tokens: number }
export interface TraceView { id: string; name: string; spans: Span[]; totalCost: number }
export function computeCost(spans: Span[], costPerToken: number = 0.00001): number {
  return Math.round(spans.reduce((a,s) => a + s.tokens * costPerToken, 0) * 1e6) / 1e6;
}
export function p95Latency(spans: Span[]): number {
  const sorted = spans.map(s => s.latencyMs).sort((a,b) => a-b);
  return sorted[Math.floor(sorted.length * 0.95)] || 0;
}
