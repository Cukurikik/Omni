// Omni CAMEL Multi-Agent Monitor (TypeScript)
// Ref: camel-ai/multi-agent-streamlit-ui
export interface AgentTrace { from: string; to: string; step: number; content: string; }
export function consensusRate(responses: string[]): number {
  const unique = new Set(responses.map(r => r.trim().toLowerCase()));
  return Math.round((1 - (unique.size - 1) / Math.max(responses.length, 1)) * 1e4) / 1e4;
}
export function traceToTimeline(traces: AgentTrace[]): { step: number; from: string; to: string }[] {
  return traces.map(t => ({ step: t.step, from: t.from, to: t.to }));
}
