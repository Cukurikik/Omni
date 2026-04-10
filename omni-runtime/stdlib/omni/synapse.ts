// ==========================================
// ⚛️ OMNI-SYNAPSE: JS ↔ FASTAPI NEURAL BRIDGE
// ==========================================
// SPEK DEWA: Memanggil route FastAPI dari TypeScript
// TANPA HTTP, TANPA fetch(), TANPA CORS!
//
// Request melompat:
//   TypeScript → V8 → Rust FFI → Golang → CPython → FastAPI
//   Semua di dalam RAM — Zero Network Latency!
//
// IMPORT: import { pyFetch, synapse } from 'omni/synapse';
//
// CONTOH:
//   const res = await pyFetch("/python/analisis", { teks: "Hello AI!" });
//   console.log(res.skor_ai); // 0.99
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
};

// ==========================================
// TYPES
// ==========================================

export interface SynapseResponse<T = any> {
    status: number;
    headers: Record<string, string>;
    data: T;
}

export interface SynapseConfig {
    modulePath: string;
    moduleName: string;
    appVar: string;
}

export interface SynapseStatus {
    initialized: boolean;
    fastapi_loaded: boolean;
    app_module: string;
    app_var: string;
    total_calls: number;
    avg_latency_ns: number;
    avg_latency_us: number;
    uptime_seconds: number;
    mode: string;
    bridge: string;
}

// ==========================================
// 🔥 IGNITE: Menyalakan FastAPI di dalam RAM
// ==========================================

/**
 * Menyalakan reaktor FastAPI di dalam proses Golang.
 * ⚡ Setelah ignite, Uvicorn SELAMANYA tidak dibutuhkan!
 *
 * @param config.modulePath - Path ke folder yang berisi file Python
 * @param config.moduleName - Nama modul Python (tanpa .py)
 * @param config.appVar - Nama variable FastAPI app (default: "app")
 *
 * @example
 * igniteFastAPI({
 *   modulePath: "./api",
 *   moduleName: "ai_router",
 *   appVar: "app"
 * });
 */
export function igniteFastAPI(config?: Partial<SynapseConfig>): void {
    const res = OmniNative.syscall("synapse_ignite", {
        module_path: config?.modulePath ?? "./api",
        module_name: config?.moduleName ?? "main",
        app_var: config?.appVar ?? "app",
    });
    if (res.error) throw new Error(`[OMNI-SYNAPSE] Ignite gagal: ${res.error}`);
}

// ==========================================
// ⚡ pyFetch: Telepati Memori ke FastAPI
// ==========================================

/**
 * SPEK DEWA: Memanggil rute FastAPI tanpa HTTP Network!
 *
 * Request melompat dari V8 (JS) → Rust → Golang → CPython (FastAPI)
 * murni di dalam RAM. Latensi: ~0.001ms (vs ~15ms via HTTP biasa).
 *
 * ❌ Tidak perlu `fetch("http://localhost:8000/api")`
 * ❌ Tidak ada CORS error
 * ❌ Tidak ada JSON serialization via network
 * ✅ Komunikasi langsung di RAM!
 *
 * @param route - FastAPI route (contoh: "/python/analisis")
 * @param payload - Data yang dikirim ke FastAPI (auto-JSON.stringify)
 * @param options - Method, headers tambahan
 *
 * @example
 * const result = pyFetch("/python/analisis", { teks: "Hello!" });
 * console.log(result.skor_ai); // 0.99
 */
export function pyFetch<T = any>(
    route: string,
    payload?: any,
    options?: {
        method?: string;
        headers?: Record<string, string>;
        query?: string;
    }
): T {
    const method = options?.method ?? (payload ? "POST" : "GET");
    const body = payload ? JSON.stringify(payload) : "";

    const res = OmniNative.syscall("synapse_call", {
        method,
        route,
        body,
        query: options?.query ?? "",
        headers: {
            "content-type": "application/json",
            ...(options?.headers ?? {}),
        },
    });

    if (res.error) throw new Error(`[OMNI-SYNAPSE] ${res.error}`);

    const data = res.data as string;

    // Auto-parse JSON response
    try {
        return JSON.parse(data) as T;
    } catch {
        return data as unknown as T;
    }
}

/**
 * pyFetch dengan full response metadata (status, headers, body).
 */
export function pyFetchFull<T = any>(
    route: string,
    payload?: any,
    options?: {
        method?: string;
        headers?: Record<string, string>;
        query?: string;
    }
): SynapseResponse<T> {
    const method = options?.method ?? (payload ? "POST" : "GET");
    const body = payload ? JSON.stringify(payload) : "";

    const res = OmniNative.syscall("synapse_call", {
        method,
        route,
        body,
        query: options?.query ?? "",
        headers: {
            "content-type": "application/json",
            ...(options?.headers ?? {}),
        },
    });

    if (res.error) throw new Error(`[OMNI-SYNAPSE] ${res.error}`);

    const status = res.status as number;
    const headers = res.headers as Record<string, string>;
    const data = res.data as string;

    let parsedData: T;
    try {
        parsedData = JSON.parse(data) as T;
    } catch {
        parsedData = data as unknown as T;
    }

    return { status, headers, data: parsedData };
}

// ==========================================
// 🔧 HELPER SHORTCUTS
// ==========================================

/**
 * GET request ke FastAPI route.
 */
export function pyGet<T = any>(route: string, query?: string): T {
    return pyFetch<T>(route, undefined, { method: "GET", query });
}

/**
 * POST request ke FastAPI route.
 */
export function pyPost<T = any>(route: string, payload: any): T {
    return pyFetch<T>(route, payload, { method: "POST" });
}

/**
 * PUT request ke FastAPI route.
 */
export function pyPut<T = any>(route: string, payload: any): T {
    return pyFetch<T>(route, payload, { method: "PUT" });
}

/**
 * DELETE request ke FastAPI route.
 */
export function pyDelete<T = any>(route: string): T {
    return pyFetch<T>(route, undefined, { method: "DELETE" });
}

/**
 * PATCH request ke FastAPI route.
 */
export function pyPatch<T = any>(route: string, payload: any): T {
    return pyFetch<T>(route, payload, { method: "PATCH" });
}

// ==========================================
// 📊 STATUS & DIAGNOSTICS
// ==========================================

/**
 * Dapatkan status OMNI-SYNAPSE engine.
 */
export function getSynapseStatus(): SynapseStatus {
    const res = OmniNative.syscall("synapse_status", {});
    return res as unknown as SynapseStatus;
}

// ==========================================
// 📦 EXPORTS
// ==========================================

export const synapse = {
    ignite: igniteFastAPI,
    call: pyFetch,
    callFull: pyFetchFull,
    get: pyGet,
    post: pyPost,
    put: pyPut,
    delete: pyDelete,
    patch: pyPatch,
    status: getSynapseStatus,
};

export default synapse;
