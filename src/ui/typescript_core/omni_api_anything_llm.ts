export interface ChunkConfig {
    chunkSize: number;
    overlap: number;
}

export class OmniAnythingLLMAPI {
    /** OMNI Interface: AnythingLLM RAG API */
    public static estimateChunks(textLen: number, config: ChunkConfig): number {
        if (textLen <= 0 || config.chunkSize <= 0) return 0;
        if (config.chunkSize >= textLen) return 1;
        const step = Math.max(1, config.chunkSize - config.overlap);
        return Math.floor((textLen - config.chunkSize) / step) + 1;
    }
}
