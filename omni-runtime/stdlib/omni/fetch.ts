// ==========================================
// 🌐 OMNI-NEXUS FETCH: POLYGLOT API GATEWAY
// ==========================================
// Rantai Eksekusi 5 Dimensi:
//   TypeScript → JavaScript(V8) → Golang(HTTP) → Rust(Validate) → Python(Crunch)
//
// Saat developer memanggil `omniFetch()`:
//   1. TypeScript: Auto-complete + Type Safety + IntelliSense
//   2. JavaScript: V8 Engine mengeksekusi syscall
//   3. Golang: HTTP client bare-metal (kebal timeout + DDoS)
//   4. Rust: Memvalidasi JSON (kebal XSS/SQLi/injection)
//   5. Python: Data crunching (statistik/AI/prediksi)
//
// IMPORT: import { omniFetch, omniGet, omniPost } from 'omni/fetch';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
};

// ==========================================
// TYPES
// ==========================================

/** Konfigurasi untuk omniFetch */
export interface OmniFetchOptions {
    /** HTTP Method (default: GET) */
    method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'HEAD' | 'OPTIONS';
    /** Request headers */
    headers?: Record<string, string>;
    /** Request body (string atau object — auto JSON.stringify) */
    body?: string | Record<string, unknown>;
    /** Timeout dalam milliseconds (default: 10000) */
    timeoutMs?: number;
    /** Aktifkan Rust JSON validation (default: true) */
    validateRust?: boolean;
    /** Konfigurasi Python data cruncher (opsional) */
    usePythonCruncher?: PythonCruncherConfig | string;
    /** Follow redirects (default: true) */
    followRedirect?: boolean;
}

/** Konfigurasi untuk Python Data Cruncher */
export interface PythonCruncherConfig {
    /** Nama script Python di venom_scripts/ (tanpa .py) */
    script: string;
    /** Nama fungsi Python untuk memproses data */
    func: string;
}

/** Response dari omniFetch — jauh lebih kaya dari fetch() biasa */
export interface OmniFetchResponse<T = any> {
    /** HTTP status code */
    status: number;
    /** HTTP status text (e.g. "200 OK") */
    statusText: string;
    /** Response headers */
    headers: Record<string, string>;
    /** Raw response body (string) */
    body: string;
    /** URL final setelah redirect */
    url: string;
    /** true jika status 2xx */
    ok: boolean;
    /** Total latency dalam milliseconds */
    latencyMs: number;
    /** Pipeline bahasa yang dilalui */
    pipeline: string[];
    /** Laporan validasi Rust (jika aktif) */
    rustReport?: string;
    /** Data hasil olahan Python (jika aktif) */
    pythonData?: string;
}

/** Parsed response — data sudah di-parse sebagai type T */
export interface OmniFetchParsed<T = any> extends OmniFetchResponse<T> {
    /** Data yang sudah di-parse sebagai JSON */
    data: T;
    /** Data olahan Python (sudah di-parse) */
    crunched?: any;
}

// ==========================================
// ⚡ CORE: omniFetch — THE 5D POLYGLOT GATEWAY
// ==========================================

/**
 * OMNI NEXUS FETCH — Polyglot API Gateway
 *
 * Memanggil API eksternal melalui rantai 5 bahasa:
 * TypeScript → V8 → Golang HTTP → Rust Validate → Python Crunch
 *
 * @example
 * ```typescript
 * // Simple GET
 * const resp = omniFetch<WeatherData>("https://api.weather.com/v1/current");
 *
 * // POST with Rust validation
 * const resp = omniFetch("https://api.example.com/data", {
 *     method: 'POST',
 *     body: { key: "value" },
 *     validateRust: true
 * });
 *
 * // GET + Python AI processing
 * const crypto = omniFetch<CryptoAnalysis>("https://api.binance.com/api/v3/klines", {
 *     usePythonCruncher: { script: "nexus_cruncher", func: "proses_data_kripto" }
 * });
 * ```
 */
export function omniFetch<T = any>(url: string, options?: OmniFetchOptions): OmniFetchParsed<T> {
    const method = options?.method || 'GET';
    const validateRust = options?.validateRust !== false; // Default: true

    // Prepare body
    let bodyStr = '';
    if (options?.body) {
        bodyStr = typeof options.body === 'string'
            ? options.body
            : JSON.stringify(options.body);
    }

    // Prepare Python config
    let pythonScript = '';
    let pythonFunc = '';
    if (options?.usePythonCruncher) {
        if (typeof options.usePythonCruncher === 'string') {
            pythonScript = options.usePythonCruncher;
            pythonFunc = options.usePythonCruncher;
        } else {
            pythonScript = options.usePythonCruncher.script;
            pythonFunc = options.usePythonCruncher.func;
        }
    }

    // ⚡ SYSCALL: Go menerima, Rust validasi, Python olah!
    const response = OmniNative.syscall("omni_nexus_fetch", {
        url,
        method,
        headers: options?.headers || {},
        body: bodyStr,
        timeoutMs: options?.timeoutMs || 10000,
        validateRust,
        pythonScript,
        pythonFunc,
        followRedirect: options?.followRedirect !== false,
    });

    const result = response.result as Record<string, unknown>;

    if (!result) {
        throw new Error('[OMNI-NEXUS] Syscall returned null — Golang mungkin crash');
    }

    // Parse response
    const fetchResponse: OmniFetchParsed<T> = {
        status: (result.status as number) || 0,
        statusText: (result.status_text as string) || '',
        headers: (result.headers as Record<string, string>) || {},
        body: (result.body as string) || '',
        url: (result.url as string) || url,
        ok: (result.ok as boolean) || false,
        latencyMs: (result.latency_ms as number) || 0,
        pipeline: (result.pipeline as string[]) || [],
        rustReport: result.rust_report as string,
        pythonData: result.python_data as string,
        data: {} as T,
    };

    // Auto-parse body as JSON
    try {
        fetchResponse.data = JSON.parse(fetchResponse.body) as T;
    } catch {
        fetchResponse.data = fetchResponse.body as unknown as T;
    }

    // Auto-parse Python crunched data
    if (fetchResponse.pythonData) {
        try {
            fetchResponse.crunched = JSON.parse(fetchResponse.pythonData);
        } catch {
            fetchResponse.crunched = fetchResponse.pythonData;
        }
    }

    return fetchResponse;
}

// ==========================================
// 🎯 CONVENIENCE METHODS
// ==========================================

/** GET request — shorthand */
export function omniGet<T = any>(url: string, headers?: Record<string, string>): OmniFetchParsed<T> {
    return omniFetch<T>(url, { method: 'GET', headers });
}

/** POST JSON — shorthand */
export function omniPost<T = any>(url: string, body: unknown, headers?: Record<string, string>): OmniFetchParsed<T> {
    return omniFetch<T>(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...headers },
        body: typeof body === 'string' ? body : JSON.stringify(body),
    });
}

/** PUT JSON — shorthand */
export function omniPut<T = any>(url: string, body: unknown, headers?: Record<string, string>): OmniFetchParsed<T> {
    return omniFetch<T>(url, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', ...headers },
        body: typeof body === 'string' ? body : JSON.stringify(body),
    });
}

/** DELETE request — shorthand */
export function omniDelete<T = any>(url: string, headers?: Record<string, string>): OmniFetchParsed<T> {
    return omniFetch<T>(url, { method: 'DELETE', headers });
}

/** PATCH JSON — shorthand */
export function omniPatch<T = any>(url: string, body: unknown, headers?: Record<string, string>): OmniFetchParsed<T> {
    return omniFetch<T>(url, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', ...headers },
        body: typeof body === 'string' ? body : JSON.stringify(body),
    });
}

// ==========================================
// 🐍 PYTHON-POWERED FETCH VARIANTS
// ==========================================

/**
 * Fetch + Python Data Crunching
 * Ambil data dari API, lalu proses dengan Python secara in-memory.
 *
 * @example
 * ```typescript
 * const analysis = omniFetchWithPython(
 *     "https://api.binance.com/api/v3/klines?symbol=BTCUSDT",
 *     "nexus_cruncher",
 *     "proses_data_kripto"
 * );
 * console.log(analysis.crunched.statistics.mean);
 * ```
 */
export function omniFetchWithPython<T = any>(
    url: string,
    pythonScript: string,
    pythonFunc: string,
    options?: Omit<OmniFetchOptions, 'usePythonCruncher'>,
): OmniFetchParsed<T> {
    return omniFetch<T>(url, {
        ...options,
        usePythonCruncher: { script: pythonScript, func: pythonFunc },
    });
}

/**
 * Fetch tanpa validasi Rust — untuk API yang sudah trusted
 * ⚠️ PERINGATAN: Data tidak disanitasi!
 */
export function omniFetchUnsafe<T = any>(url: string, options?: OmniFetchOptions): OmniFetchParsed<T> {
    return omniFetch<T>(url, { ...options, validateRust: false });
}

// ==========================================
// 📊 NEXUS GATEWAY STATUS
// ==========================================

/** Ambil statistik Nexus Gateway */
export function getNexusStatus(): Record<string, unknown> {
    return OmniNative.syscall("nexus_status", {});
}

// ==========================================
// 🔧 TYPE HELPERS
// ==========================================

/** Type guard for checking if fetch was successful */
export function isOmniFetchOk<T>(response: OmniFetchParsed<T>): response is OmniFetchParsed<T> & { ok: true } {
    return response.ok;
}

/** Extract error message from failed fetch */
export function getOmniFetchError(response: OmniFetchParsed): string {
    if (response.ok) return '';
    try {
        const parsed = typeof response.data === 'string' ? JSON.parse(response.data) : response.data;
        return parsed?.error || parsed?.message || `HTTP ${response.status}`;
    } catch {
        return `HTTP ${response.status}: ${response.statusText}`;
    }
}

// ==========================================
// 📦 DEFAULT EXPORT
// ==========================================

export default {
    omniFetch,
    omniGet,
    omniPost,
    omniPut,
    omniDelete,
    omniPatch,
    omniFetchWithPython,
    omniFetchUnsafe,
    getNexusStatus,
    isOmniFetchOk,
    getOmniFetchError,
};
