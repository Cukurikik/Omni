// Omni DMax Decode Monitor (TypeScript)
// Ref: czg1225/DMax
export function monitorParallelDecode(proposed: number[], verified: number[]): { accepted: number; rate: number } {
  let accepted = 0;
  for (let i = 0; i < Math.min(proposed.length, verified.length); i++) {
    if (proposed[i] === verified[i]) accepted++; else break;
  }
  return { accepted, rate: Math.round(accepted / Math.max(proposed.length, 1) * 1e4) / 1e4 };
}
export function adaptiveSchedule(step: number, total: number, base: number = 4): number {
  const p = step / Math.max(total, 1);
  if (p < 0.3) return Math.min(base * 2, 16);
  if (p < 0.7) return base;
  return Math.max(Math.floor(base / 2), 1);
}
