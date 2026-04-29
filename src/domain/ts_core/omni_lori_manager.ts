// Omni LoRI Adapter Manager (TypeScript)
export interface AdapterInfo { taskName: string; rank: number; nParams: number; interference: number }
export function mergeAdapters(adapters: AdapterInfo[], weights?: number[]): {nTasks: number; avgInterference: number} {
  const w = weights || adapters.map(() => 1 / adapters.length);
  const avgInt = adapters.reduce((s, a, i) => s + a.interference * w[i], 0);
  return {nTasks: adapters.length, avgInterference: Math.round(avgInt * 1e4) / 1e4};
}
