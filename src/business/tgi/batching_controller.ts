// OMNI TEXT-GENERATION-INFERENCE: Dynamic Batching Controller
// TypeScript logic determining when to trigger inference based on queue size and latency SLA.
// Source: huggingface/text-generation-inference

export interface InferenceRequest {
    id: string;
    promptTokens: number;
    queuedAtMs: number;
}

export class BatchingController {
    private maxBatchSize: number;
    private maxWaitTimeMs: number; // Max time a request can sit in queue before forcing a batch
    private queue: InferenceRequest[] = [];

    constructor(maxBatchSize: number = 32, maxWaitTimeMs: number = 20) {
        this.maxBatchSize = maxBatchSize;
        this.maxWaitTimeMs = maxWaitTimeMs;
    }

    public enqueue(request: InferenceRequest): void {
        this.queue.push(request);
    }

    /**
     * Called on a high-frequency event loop (e.g., every 1ms).
     * Returns a batch of requests if conditions are met, otherwise null.
     */
    public tick(currentTimeMs: number): InferenceRequest[] | null {
        if (this.queue.length === 0) {
            return null;
        }

        const oldestRequest = this.queue[0];
        const waitTime = currentTimeMs - oldestRequest.queuedAtMs;

        // Condition 1: Max Wait Time SLA Exceeded
        // Condition 2: Queue size reaches max batch size
        if (waitTime >= this.maxWaitTimeMs || this.queue.length >= this.maxBatchSize) {
            const batchSize = Math.min(this.queue.length, this.maxBatchSize);
            const batch = this.queue.splice(0, batchSize);
            return batch;
        }

        return null; // Keep waiting to form a larger batch
    }
}
