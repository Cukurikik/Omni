// Omni DuQuant Quantization Viewer (TypeScript)
export interface QuantResult { nBits: number; mse: number; outlierReduction: number; scale: number }
export function compressionRatio(origBits: number, targetBits: number): number { return Math.round(origBits / targetBits * 10) / 10; }
export function memorySavingsGB(paramsB: number, origBits: number, targetBits: number): number {
  return Math.round((paramsB * 1e9 * (origBits - targetBits) / 8 / 1e9) * 100) / 100;
}
