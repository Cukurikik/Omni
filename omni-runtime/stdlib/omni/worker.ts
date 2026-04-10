// ==========================================
// 🧵 OMNI-LAND: NATIVE WORKER THREADS
// ==========================================
// Node.js worker_threads membuat V8 Isolate baru per worker.
// OMNI workers menggunakan Goroutines + V8 Isolates via Rust.
//
// IMPORT: import { Worker } from 'omni/worker';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
    registerCallback: (id: string, fn: Function) => void;
};

export interface WorkerOptions {
    workerData?: any;
    maxHeapMB?: number;
}

/**
 * Worker — eksekusi kode di V8 Isolate terpisah (via Goroutine).
 * Setiap Worker mendapat heap-nya sendiri — isolasi total!
 */
export class Worker {
    readonly workerId: string;
    private _listeners: Map<string, Array<(data: any) => void>> = new Map();

    constructor(scriptPath: string, options?: WorkerOptions) {
        const res = OmniNative.syscall("worker_create", {
            scriptPath,
            workerData: options?.workerData ?? null,
            maxHeapMB: options?.maxHeapMB ?? 128,
        });
        if (res.error) throw new Error(`[OMNI-WORKER] ${res.error}`);
        this.workerId = res.workerId as string;
    }

    /**
     * Kirim pesan ke worker.
     */
    postMessage(data: any): void {
        OmniNative.syscall("worker_post_message", {
            workerId: this.workerId,
            data,
        });
    }

    /**
     * Daftarkan listener untuk pesan dari worker.
     */
    onMessage(callback: (data: any) => void): this {
        const cbId = `worker_msg_${this.workerId}`;
        OmniNative.registerCallback(cbId, callback);
        OmniNative.syscall("worker_on_message", { workerId: this.workerId, callbackId: cbId });
        if (!this._listeners.has("message")) this._listeners.set("message", []);
        this._listeners.get("message")!.push(callback);
        return this;
    }

    /**
     * Daftarkan listener untuk error dari worker.
     */
    onError(callback: (err: string) => void): this {
        const cbId = `worker_err_${this.workerId}`;
        OmniNative.registerCallback(cbId, callback);
        OmniNative.syscall("worker_on_error", { workerId: this.workerId, callbackId: cbId });
        return this;
    }

    /**
     * Daftarkan listener untuk worker selesai.
     */
    onExit(callback: (code: number) => void): this {
        const cbId = `worker_exit_${this.workerId}`;
        OmniNative.registerCallback(cbId, callback);
        OmniNative.syscall("worker_on_exit", { workerId: this.workerId, callbackId: cbId });
        return this;
    }

    /**
     * Terminate worker secara paksa.
     */
    terminate(): void {
        OmniNative.syscall("worker_terminate", { workerId: this.workerId });
        this._listeners.clear();
    }
}

/**
 * Jumlah worker yang sedang aktif.
 */
export function activeWorkerCount(): number {
    const res = OmniNative.syscall("worker_active_count", {});
    return res.result as number;
}

/**
 * Dapatkan workerData (hanya tersedia di dalam worker thread).
 */
export function getWorkerData(): any {
    return OmniNative.syscall("worker_get_data", {}).result;
}

/**
 * Cek apakah kode berjalan di main thread atau worker thread.
 */
export function isMainThread(): boolean {
    return OmniNative.syscall("worker_is_main", {}).result as boolean;
}

export default { Worker, activeWorkerCount, getWorkerData, isMainThread };
