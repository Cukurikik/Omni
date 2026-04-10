// ==========================================
// 💾 OMNI-LAND: IMMORTAL QUEUE BINDINGS
// ==========================================
// Pemusnahan Redis & RabbitMQ. Antrean persisten
// yang dijamin WAL (Write-Ahead Logging) di SSD.
//
// IMPORT: import { dispatchBackgroundJob, onJob } from 'omni/queue';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
};

export interface JobConfig {
    name: string;
    payload: Record<string, unknown>;
    maxRetry?: number;
}

export interface JobResult {
    jobId: string;
    status: string;
}

/**
 * ⚡ SPEK DEWA: Menambahkan tugas ke dalam antrean abadi.
 * Tidak butuh Redis! WAL Golang menjamin ZERO data loss.
 * 
 * Jika server mati listrik 1 detik setelah dispatch,
 * OMNI-AURA akan melanjutkan tugas ini saat boot ulang!
 * 
 * @example
 * ```ts
 * import { dispatchBackgroundJob } from 'omni/queue';
 * 
 * dispatchBackgroundJob({
 *     name: "send_receipt_email",
 *     payload: { email: "user@example.com", orderId: "ORD-123" }
 * });
 * ```
 */
export function dispatchBackgroundJob(job: JobConfig): string {
    const response = OmniNative.syscall("queue_dispatch", {
        name: job.name,
        payload: job.payload,
        max_retry: job.maxRetry ?? 3,
    });

    if (response.error) {
        throw new Error(`[OMNI-AURA] Gagal mencatat WAL: ${response.error}`);
    }

    return response.jobId as string;
}

/**
 * Mendaftarkan handler untuk jenis job tertentu.
 * Worker OMNI-AURA akan memanggil handler ini secara otomatis.
 */
export function onJob(jobName: string, handler: (payload: Record<string, unknown>) => void): void {
    OmniNative.syscall("queue_register", {
        name: jobName,
        handlerName: String((handler as unknown as { name?: string }).name || "anonymous"),
    });
}

/**
 * Mendapatkan statistik queue engine.
 */
export function getQueueStats(): {
    totalDispatched: number;
    totalProcessed: number;
    totalFailed: number;
    queueDepth: number;
} {
    const response = OmniNative.syscall("queue_stats", {});
    return response as {
        totalDispatched: number;
        totalProcessed: number;
        totalFailed: number;
        queueDepth: number;
    };
}

export default { dispatchBackgroundJob, onJob, getQueueStats };
