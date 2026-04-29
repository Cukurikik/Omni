// Omni Lilypad Prompt Version Tracker (TypeScript)
// Ref: Mirascope/lilypad
export interface PromptVersion { hash: string; template: string; variables: Record<string, string>; createdAt: number; }
export interface Trace { version: string; input: Record<string, any>; output: string; latencyMs: number; }

export function hashPrompt(template: string, vars: Record<string, string>): string {
  let h = 0;
  const s = template + JSON.stringify(vars);
  for (let i = 0; i < s.length; i++) { h = ((h << 5) - h + s.charCodeAt(i)) | 0; }
  return Math.abs(h).toString(16).padStart(8, '0');
}

export function createVersion(template: string, variables: Record<string, string>): PromptVersion {
  return { hash: hashPrompt(template, variables), template, variables, createdAt: Date.now() };
}

export function analyzeTraces(traces: Trace[]): { avgLatency: number; p95Latency: number; avgTokens: number } {
  if (!traces.length) return { avgLatency: 0, p95Latency: 0, avgTokens: 0 };
  const lats = traces.map(t => t.latencyMs).sort((a, b) => a - b);
  return {
    avgLatency: Math.round(lats.reduce((a, l) => a + l, 0) / lats.length * 100) / 100,
    p95Latency: lats[Math.floor(lats.length * 0.95)] || lats[lats.length - 1],
    avgTokens: Math.round(traces.reduce((a, t) => a + t.output.split(' ').length, 0) / traces.length),
  };
}
