// Omni Finance-LLMs Risk Analyzer (TypeScript)
// Domain: Financial risk analysis metrics.
// Ref: kennethleungty/Finance-LLMs
export function sharpeRatio(returns: number[], riskFreeRate: number = 0.02): number {
  const n = returns.length; if (n === 0) return 0;
  const mean = returns.reduce((s, r) => s + r, 0) / n;
  const std = Math.sqrt(returns.reduce((s, r) => s + (r - mean) ** 2, 0) / n);
  return std === 0 ? 0 : Math.round((mean - riskFreeRate) / std * 1e6) / 1e6;
}
export function maxDrawdown(prices: number[]): number {
  let peak = prices[0] || 0, mdd = 0;
  for (const p of prices) { if (p > peak) peak = p; const dd = (peak - p) / peak; if (dd > mdd) mdd = dd; }
  return Math.round(mdd * 1e6) / 1e6;
}
