// ============================================================
// 📦 omni-std/ui/types.ts — TypeScript Bindings
// ============================================================
// Mengimplementasikan strict monadic Result type dan type-safe Option

export type Result<T, E> = 
  | { ok: true; value: T }
  | { ok: false; error: E };

export function Ok<T>(value: T): Result<T, never> {
  return { ok: true, value };
}

export function Err<E>(error: E): Result<never, E> {
  return { ok: false, error };
}

export type Option<T> = 
  | { some: true; value: T }
  | { some: false };

export function Some<T>(value: T): Option<T> {
  return { some: true, value };
}

export const None: Option<never> = { some: false };

// OmniError
export interface OmniError {
  code: string;
  message: string;
}

export class OmniBuffer {
  // Bindings ke C memory.rs via bridge (implemented at LLVM layer)
  constructor(public ptr: number, public length: number) {}
}

export function unwrap<T, E>(res: Result<T, E>): T {
    if (res.ok) return res.value;
    throw new Error(`[OMNI-E002] Cannot unwrap Err: ${JSON.stringify(res.error)}`);
}
