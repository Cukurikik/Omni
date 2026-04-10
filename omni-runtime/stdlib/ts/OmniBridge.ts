// ============================================================
// OMNI TypeScript Bridge — Type-Safe Interface Definitions
// ============================================================
// Dikompilasi oleh OMNI Compiler (bukan tsc/esbuild/swc).
// Tipe ini menjamin keamanan contract antara UI ↔ Kernel.
// ============================================================

/** Representasi pointer ke OmniBuffer di Rust heap */
export interface OmniBuffer {
  /** Alamat memori mentah (usize dari Rust NonNull<u8>) */
  readonly ptr: number;
  /** Panjang data aktual dalam bytes */
  readonly len: number;
  /** Kapasitas alokasi total */
  readonly capacity: number;
}

/** Result monadik — menggantikan try/catch konvensional */
export type OmniResult<T, E = OmniError> =
  | { ok: true; value: T }
  | { ok: false; error: E };

/** Error bertipe dari kernel OMNI */
export interface OmniError {
  code: string;    // E001, E002, dst.
  message: string;
  layer: 'system' | 'network' | 'compute' | 'domain' | 'ui';
}

/** FFI function signature yang di-inject oleh V8 MicroIsolate */
declare global {
  /** Eksekusi fungsi native OMNI */
  function __omni_ffi(functionName: string, data: ArrayBuffer): ArrayBuffer;
  /** Alokasi OmniBuffer di Rust heap */
  function __omni_buffer_alloc(sizeBytes: number): OmniBuffer;
  /** Spawn green thread via OmniEventLoop */
  function __omni_spawn(taskName: string, payload: ArrayBuffer): Promise<ArrayBuffer>;
}

/**
 * Type-safe wrapper untuk OMNI FFI boundary.
 * Menegakkan monadic error handling di layer TypeScript.
 */
export function executeOmni<T>(
  functionName: string,
  data: ArrayBuffer
): OmniResult<T> {
  try {
    const raw = __omni_ffi(functionName, data);
    // Decode result dari flat buffer → typed object
    const view = new DataView(raw);
    const statusByte = view.getUint8(0);

    if (statusByte === 0x00) {
      // Success path
      return { ok: true, value: raw as unknown as T };
    } else {
      return {
        ok: false,
        error: {
          code: `E${String(statusByte).padStart(3, '0')}`,
          message: 'Kernel returned error status',
          layer: 'system',
        },
      };
    }
  } catch (e) {
    return {
      ok: false,
      error: {
        code: 'E999',
        message: String(e),
        layer: 'system',
      },
    };
  }
}
