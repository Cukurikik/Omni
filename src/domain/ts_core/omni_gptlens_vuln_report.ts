// Omni GPTLens Vulnerability Report (TypeScript)
// Ref: git-disl/GPTLens
interface Finding { line: number; type: string; confidence: number; verified: boolean; }
export function filterVerified(findings: Finding[], minConf: number = 0.6): Finding[] {
  return findings.filter(f => f.verified && f.confidence >= minConf);
}
export function severityScore(findings: Finding[]): number {
  const weights: Record<string, number> = { reentrancy: 1.0, tx_origin: 0.8, delegatecall: 0.9, selfdestruct: 1.0 };
  return findings.reduce((s, f) => s + (weights[f.type] || 0.5) * f.confidence, 0);
}
