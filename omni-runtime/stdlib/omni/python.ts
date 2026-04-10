// ==========================================
// 🐍 OMNI-LAND: NATIVE PYTHON BINDINGS
// ==========================================
// TypeScript bisa mengeksekusi Python secara NATIVE!
// Alur: TypeScript → V8 → Rust Syscall → Golang → CPython (in-process!)
//
// ╔═══════════════════════════════════════════╗
// ║  TANPA Flask. TANPA FastAPI.              ║
// ║  TANPA HTTP overhead.                     ║
// ║  LANGSUNG DI RAM!                         ║
// ╚═══════════════════════════════════════════╝
//
// IMPORT: import { runVenom, runPythonRaw } from 'omni/python';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
};

export interface VenomResult {
    result: string;
    mode: 'native' | 'stub';
    script?: string;
    func?: string;
}

export interface VenomStatus {
    initialized: boolean;
    python_version: string;
    scripts_dir: string;
    mode: 'NATIVE_CPYTHON' | 'STUB';
    bridge: string;
}

/**
 * ⚡ SPEK DEWA: Mengeksekusi fungsi Python secara Native dari TypeScript.
 * Latensi nyaris NOL — tidak ada HTTP overhead!
 *
 * **Alur:** TypeScript → V8 → Rust Syscall → Golang CGO → CPython
 *
 * @param script - Nama file Python (tanpa .py) di folder venom_scripts/
 * @param func - Nama fungsi yang akan dipanggil
 * @param data - Data yang dikirim ke Python (auto-serialized ke JSON)
 * @returns Hasil dari fungsi Python (auto-parsed dari JSON)
 *
 * @example
 * ```ts
 * import { runVenom } from 'omni/python';
 *
 * // Panggil fungsi Python langsung dari TypeScript!
 * const prediksi = runVenom("data_cruncher", "proses_big_data", {
 *     sales: [100, 200, 300, 400, 500],
 *     region: "Asia Pacific"
 * });
 * console.log(prediksi); // { mean: 300, std: 141.42, trend: "naik" }
 * ```
 */
export function runVenom<T = unknown>(script: string, func: string, data: unknown): T {
    const raw = OmniNative.syscall("venom_execute", {
        script,
        func,
        payload: JSON.stringify(data),
    });

    if (raw.error) {
        throw new Error(`[OMNI-VENOM] Eksekusi Python gagal: ${raw.error}`);
    }

    const result = raw.result as string;

    // Coba parse JSON dari Python
    try {
        return JSON.parse(result) as T;
    } catch {
        // Jika bukan JSON, kembalikan string apa adanya
        return result as unknown as T;
    }
}

/**
 * ⚡ Eksekusi kode Python mentah (raw code) langsung dari TypeScript.
 * Berguna untuk one-off scripts atau prototyping cepat.
 *
 * @example
 * ```ts
 * import { runPythonRaw } from 'omni/python';
 *
 * const output = runPythonRaw(`
 *     import math
 *     print(f"Pi = {math.pi}")
 *     print(f"Euler = {math.e}")
 * `);
 * console.log(output); // "Pi = 3.141592653589793\nEuler = 2.718281828459045"
 * ```
 */
export function runPythonRaw(code: string): string {
    const raw = OmniNative.syscall("venom_raw", { code });

    if (raw.error) {
        throw new Error(`[OMNI-VENOM] Eksekusi raw Python gagal: ${raw.error}`);
    }

    return (raw.output as string) ?? "";
}

/**
 * 🔥 Aktifkan OMNI-VENOM Python engine.
 * Harus dipanggil SEBELUM runVenom().
 * Biasanya dipanggil saat server boot.
 *
 * @param scriptsDir - Path ke folder yang berisi file .py (default: ./venom_scripts)
 */
export function ignitePython(scriptsDir?: string): void {
    const raw = OmniNative.syscall("venom_ignite", {
        scripts_dir: scriptsDir ?? "./venom_scripts",
    });

    if (raw.error) {
        throw new Error(`[OMNI-VENOM] Gagal mengaktifkan Python: ${raw.error}`);
    }

    console.log("🐍 [OMNI-VENOM] Python Reactor ONLINE!");
}

/**
 * 📊 Dapatkan status engine Python saat ini.
 */
export function getVenomStatus(): VenomStatus {
    return OmniNative.syscall("venom_status", {}) as unknown as VenomStatus;
}

export default { runVenom, runPythonRaw, ignitePython, getVenomStatus };
