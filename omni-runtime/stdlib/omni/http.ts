// ==========================================
// 🌐 OMNI-LAND: HTTP/HTTPS GOROUTINE SERVER
// ==========================================
// Node.js `http.createServer` = 1 thread + libuv event loop
// OMNI `serve()` = UNLIMITED Goroutines + net/http stdlib
//
// IMPORT: import { serve, fetch } from 'omni/http';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
};

// ==========================================
// TYPES
// ==========================================

export interface OmniRequest {
    method: string;
    url: string;
    headers: Record<string, string>;
    body: string;
    params?: Record<string, string>;
    query?: Record<string, string>;
}

export interface OmniResponse {
    status: number;
    headers: Record<string, string>;
    body: string;
}

export type OmniHandler = (req: OmniRequest) => OmniResponse | string | object;

// ==========================================
// SERVER
// ==========================================

/**
 * Mulai HTTP/HTTPS server menggunakan Golang net/http.
 * Setiap request = 1 Goroutine = PARALEL SEJATI.
 *
 * @param options - { port, ssl?, certPath?, keyPath? }
 * @param handler - Fungsi yang dijalankan per-request
 */
export function serve(
    options: {
        port: number;
        ssl?: boolean;
        certPath?: string;
        keyPath?: string;
    },
    handler: OmniHandler,
): void {
    OmniNative.syscall("http_serve", {
        port: options.port,
        ssl: options.ssl ?? false,
        certPath: options.certPath ?? "",
        keyPath: options.keyPath ?? "",
        handlerName: (handler as any).name || "__anonymous_handler__",
    });
}

// ==========================================
// HTTP CLIENT (fetch replacement)
// ==========================================

export interface FetchOptions {
    method?: string;
    headers?: Record<string, string>;
    body?: string;
    timeout?: number; // milliseconds
    followRedirects?: boolean;
}

export interface FetchResponse {
    status: number;
    statusText: string;
    headers: Record<string, string>;
    body: string;
    ok: boolean;
    url: string;
}

/**
 * Fetch URL menggunakan Go net/http client.
 * ⚡ Connection pooling + keep-alive otomatis dari Go transport.
 */
export function fetch(url: string, options?: FetchOptions): FetchResponse {
    const res = OmniNative.syscall("http_fetch", {
        url,
        method: options?.method ?? "GET",
        headers: options?.headers ?? {},
        body: options?.body ?? "",
        timeout: options?.timeout ?? 30000,
        followRedirects: options?.followRedirects ?? true,
    });

    if (res.error) throw new Error(`[OMNI-HTTP] Fetch gagal: ${res.error}`);

    return res.result as FetchResponse;
}

/**
 * POST JSON helper.
 */
export function postJSON(url: string, data: any, headers?: Record<string, string>): FetchResponse {
    return fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...headers },
        body: JSON.stringify(data),
    });
}

/**
 * GET JSON helper — otomatis parse response body.
 */
export function getJSON<T = any>(url: string, headers?: Record<string, string>): T {
    const resp = fetch(url, {
        method: "GET",
        headers: { Accept: "application/json", ...headers },
    });
    return JSON.parse(resp.body) as T;
}

export default { serve, fetch, postJSON, getJSON };
