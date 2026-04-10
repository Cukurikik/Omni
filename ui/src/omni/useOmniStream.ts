// ==========================================
// 🚀 OMNI-STREAM: ES2026 Resource-Managed Streaming Hook
// ==========================================
// Menggunakan filosofi Explicit Resource Management (ES2026 `using`/`Symbol.dispose`)
// untuk memastikan koneksi SSE/WebSocket SELALU ditutup saat komponen di-unmount.
//
// FILOSOFI:
//   Di masa lalu, developer sering bocor memory karena lupa menutup koneksi.
//   OMNI-STREAM menggunakan pattern Disposable Resource — koneksi
//   dikelola oleh lifecycle React dan ditutup OTOMATIS.
//
// KOMPATIBILITAS:
//   - Pattern ini mengimplementasikan Symbol.dispose dari TC39 Explicit Resource Management
//   - Bekerja di semua browser modern via Vite/esbuild transpilation
//   - Fallback untuk browser lama tetap tersedia
// ==========================================

import { useState, useEffect, useCallback, useRef } from 'react';

// ⚡ ES2026 Polyfill: Symbol.dispose
// Beberapa runtime belum memiliki Symbol.dispose secara native.
// Polyfill ini memastikan OMNI-STREAM berjalan di SEMUA environment.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
(Symbol as any).dispose ??= Symbol.for('Symbol.dispose');

// ==========================================
// TYPE DEFINITIONS
// ==========================================

export interface StreamMessage<T = unknown> {
    /** Tipe event dari server */
    type: string;
    /** Data payload */
    data: T;
    /** Timestamp server */
    timestamp?: number;
}

export interface StreamProgress {
    /** Job ID yang sedang dipantau */
    jobId: string;
    /** Status job: QUEUED → PROCESSING → SUCCESS/ERROR */
    status: 'QUEUED' | 'PROCESSING' | 'SUCCESS' | 'ERROR';
    /** Progress 0-100 */
    progress: number;
    /** URL output (tersedia saat SUCCESS) */
    outputUrl?: string;
    /** Error message (tersedia saat ERROR) */
    error?: string;
}

export type ConnectionState = 'DISCONNECTED' | 'CONNECTING' | 'CONNECTED' | 'ERROR';

interface UseOmniStreamResult {
    /** Status koneksi */
    connectionState: ConnectionState;
    /** Progress data terkini */
    progress: StreamProgress | null;
    /** Pesan-pesan dari stream */
    messages: StreamMessage[];
    /** Error jika ada */
    error: string | null;
    /** Mulai streaming untuk job tertentu */
    connect: (jobId: string) => void;
    /** Putuskan koneksi secara manual */
    disconnect: () => void;
}

// ==========================================
// 🌐 DISPOSABLE STREAM RESOURCE (ES2026 Pattern)
// ==========================================
// Implementasi interface Disposable — resource otomatis dibersihkan
// saat keluar dari scope atau saat React unmount.

class OmniStreamResource {
    private eventSource: EventSource | null = null;
    private _disposed = false;

    constructor(
        private url: string,
        private onMessage: (msg: StreamMessage) => void,
        private onProgress: (progress: StreamProgress) => void,
        private onStateChange: (state: ConnectionState) => void,
        private onError: (error: string) => void
    ) {
        this.connect();
    }

    private connect(): void {
        if (this._disposed) return;

        this.onStateChange('CONNECTING');

        const es = new EventSource(this.url);
        this.eventSource = es;

        es.onopen = () => {
            if (!this._disposed) {
                this.onStateChange('CONNECTED');
            }
        };

        es.onmessage = (event) => {
            if (this._disposed) return;

            try {
                const parsed = JSON.parse(event.data);

                // Jika ini progress update
                if (parsed.status && parsed.progress !== undefined) {
                    this.onProgress(parsed as StreamProgress);

                    // Auto-disconnect saat job selesai (SUCCESS/ERROR)
                    if (parsed.status === 'SUCCESS' || parsed.status === 'ERROR') {
                        setTimeout(() => this.dispose(), 500);
                    }
                }

                // Kirim sebagai pesan umum
                this.onMessage({
                    type: parsed.type || 'data',
                    data: parsed,
                    timestamp: Date.now(),
                });
            } catch {
                // Non-JSON data — kirim sebagai raw string
                this.onMessage({
                    type: 'raw',
                    data: event.data as unknown,
                    timestamp: Date.now(),
                });
            }
        };

        es.onerror = () => {
            if (this._disposed) return;
            this.onStateChange('ERROR');
            this.onError('Koneksi SSE terputus. OMNI-STREAM akan mencoba ulang otomatis.');
            // EventSource otomatis reconnect — ini fitur bawaan browser
        };
    }

    get disposed(): boolean {
        return this._disposed;
    }

    /**
     * ⚡ ES2026 Explicit Resource Management
     * Dipanggil otomatis oleh `using` keyword atau manual via dispose()
     */
    dispose(): void {
        if (this._disposed) return;
        this._disposed = true;

        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }

        this.onStateChange('DISCONNECTED');
    }

    // Symbol.dispose untuk ES2026 `using` keyword compatibility
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    [(Symbol as any).dispose](): void {
        this.dispose();
    }
}

// ==========================================
// ⚛️ REACT HOOK: useOmniStream
// ==========================================
// Hook utama untuk streaming job progress dari Golang Gateway.
//
// @example
// ```tsx
// const { connectionState, progress, connect, disconnect } = useOmniStream();
//
// // Mulai pantau job
// connect('job-uuid-123');
//
// // Progress otomatis update
// if (progress?.status === 'SUCCESS') {
//   window.open(progress.outputUrl);
// }
// ```

export function useOmniStream(): UseOmniStreamResult {
    const [connectionState, setConnectionState] = useState<ConnectionState>('DISCONNECTED');
    const [progress, setProgress] = useState<StreamProgress | null>(null);
    const [messages, setMessages] = useState<StreamMessage[]>([]);
    const [error, setError] = useState<string | null>(null);
    const resourceRef = useRef<OmniStreamResource | null>(null);

    // Bersihkan resource saat unmount (ES2026 Resource Management pattern)
    useEffect(() => {
        return () => {
            // ⚡ Explicit Resource Disposal — Zero memory leak
            if (resourceRef.current) {
                resourceRef.current.dispose();
                resourceRef.current = null;
            }
        };
    }, []);

    const connect = useCallback((jobId: string) => {
        // Dispose koneksi sebelumnya jika ada
        if (resourceRef.current) {
            resourceRef.current.dispose();
        }

        // Reset state
        setError(null);
        setMessages([]);
        setProgress({ jobId, status: 'QUEUED', progress: 0 });

        // Buat resource baru — akan auto-dispose saat komponen unmount
        const url = `/api/v1/stream/jobs?job_id=${encodeURIComponent(jobId)}`;

        resourceRef.current = new OmniStreamResource(
            url,
            // onMessage
            (msg) => setMessages((prev) => [...prev.slice(-99), msg]), // Keep last 100
            // onProgress
            (prog) => setProgress(prog),
            // onStateChange
            (state) => setConnectionState(state),
            // onError
            (err) => setError(err)
        );
    }, []);

    const disconnect = useCallback(() => {
        if (resourceRef.current) {
            resourceRef.current.dispose();
            resourceRef.current = null;
        }
    }, []);

    return {
        connectionState,
        progress,
        messages,
        error,
        connect,
        disconnect,
    };
}

// ==========================================
// 🔌 STANDALONE: connectToTitanBuffer (ES2026 `using` pattern)
// ==========================================
// Untuk penggunaan non-React (Service Workers, CLI, dll).
// Menggunakan `using` keyword untuk auto-cleanup.
//
// @example
// ```ts
// async function uploadAndMonitor(jobId: string) {
//     using stream = connectToTitanBuffer(jobId);
//     // stream otomatis ditutup ketika fungsi ini selesai!
// }
// ```

export function connectToTitanBuffer(jobId: string): OmniStreamResource {
    return new OmniStreamResource(
        `/api/v1/stream/jobs?job_id=${encodeURIComponent(jobId)}`,
        (msg) => console.log('📡 [OMNI-TITAN]', msg.data),
        (prog) => console.log(`📊 [PROGRESS] ${prog.progress}% — ${prog.status}`),
        (state) => console.log(`🔌 [STATE] ${state}`),
        (err) => console.error(`❌ [ERROR] ${err}`)
    );
}
