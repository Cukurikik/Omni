// OMNI TGI: Stop Sequence Controller
// TypeScript logic to halt LLM generation early if a specific substring is emitted.
// Source: huggingface/text-generation-inference

export class StopSequenceController {
    private stopSequences: string[];
    private buffer: string;

    constructor(stopSequences: string[]) {
        this.stopSequences = stopSequences;
        this.buffer = "";
    }

    /**
     * Feeds the newest generated text chunk.
     * Returns true if a stop sequence was detected.
     */
    public processChunk(chunk: string): boolean {
        this.buffer += chunk;

        // Check if any stop sequence exists in the buffer
        for (const seq of this.stopSequences) {
            if (this.buffer.includes(seq)) {
                return true; // Stop generation
            }
        }

        // Optimization: Keep the buffer size manageable.
        // We only need to keep the tail of the buffer equal to the length of the longest stop sequence - 1.
        let maxSeqLength = 0;
        for (const seq of this.stopSequences) {
            if (seq.length > maxSeqLength) maxSeqLength = seq.length;
        }

        if (this.buffer.length > maxSeqLength * 2) {
            this.buffer = this.buffer.substring(this.buffer.length - maxSeqLength);
        }

        return false; // Continue generation
    }
    
    /**
     * Trims the stop sequence from the final output if requested
     */
    public cleanFinalOutput(finalText: string): string {
        for (const seq of this.stopSequences) {
            const idx = finalText.indexOf(seq);
            if (idx !== -1) {
                return finalText.substring(0, idx);
            }
        }
        return finalText;
    }
}
