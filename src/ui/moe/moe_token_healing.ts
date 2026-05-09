// moe_token_healing.ts — Interface / Optimization
// Layer: Interface / API — Token Healing & Chunk Stitching
//
// Because LLMs output tokens via BPE, a single word might be chunked awkwardly
// over SSE (e.g., chunk 1: " def", chunk 2: "init", chunk 3: "ion"). 
// This TypeScript module implements "Token Healing" to seamlessly buffer and 
// stitch these chunks so the UI doesn't stutter or break HTML formatting.

export class TokenHealer {
    private buffer: string = "";

    constructor() {
        console.log("[Token Healer] Initialized subword stitching engine for UI smoothness.");
    }

    /**
     * Processes an incoming raw SSE token chunk.
     * Returns a stitched string only if it forms a complete, safe boundary,
     * otherwise holds it in the buffer.
     */
    public processChunk(rawChunk: string): string | null {
        // Handle special byte-level tokens sometimes emitted by LLaMA/Mistral
        let cleanedChunk = rawChunk.replace(/<0x0A>/g, '\n');
        
        this.buffer += cleanedChunk;

        // If the buffer ends with a space or a newline, it's a safe word boundary
        if (this.buffer.endsWith(" ") || this.buffer.endsWith("\n")) {
            const flush = this.buffer;
            this.buffer = "";
            return flush;
        }

        // Punctuation is also a safe boundary
        if (/[.,!?:]$/.test(this.buffer)) {
            const flush = this.buffer;
            this.buffer = "";
            return flush;
        }

        // Buffer is mid-word (e.g. " def"), hold it.
        return null;
    }

    /**
     * Called when the stream ends to ensure no tokens are left behind.
     */
    public flushRemaining(): string {
        const flush = this.buffer;
        this.buffer = "";
        return flush;
    }
}
