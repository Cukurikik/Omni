// OMNI STANFORD ALPACA: Quality Filter
// TypeScript logic to prune low-quality, toxic, or redundant synthetic instructions.
// Source: tatsu-lab/stanford_alpaca

export interface InstructionPair {
    id: string;
    instruction: string;
    input?: string;
    output: string;
}

export class QualityFilter {
    private bannedWords: Set<string>;

    constructor() {
        // Mock set of banned words (toxicity, AI disclaimers)
        this.bannedWords = new Set([
            "as an ai", "language model", "openai", "i cannot fulfill", "illegal", "toxic_word_mock"
        ]);
    }

    /**
     * Checks if the text contains AI disclaimers or banned words.
     */
    private containsBannedContent(text: string): boolean {
        const lowerText = text.toLowerCase();
        for (const word of this.bannedWords) {
            if (lowerText.includes(word)) {
                return true;
            }
        }
        return false;
    }

    /**
     * Checks if the instruction is too short or lacks verbs.
     */
    private isTooShort(text: string): boolean {
        const words = text.split(/\s+/);
        return words.length < 3;
    }

    /**
     * Main filtering pipeline.
     * Returns true if the pair is VALID and should be KEPT.
     * Returns false if it should be FILTERED OUT.
     */
    public isValid(pair: InstructionPair): boolean {
        if (!pair.instruction || !pair.output) return false;

        // 1. Length checks
        if (this.isTooShort(pair.instruction) || this.isTooShort(pair.output)) {
            return false;
        }

        // 2. AI Disclaimer / Toxicity checks
        if (this.containsBannedContent(pair.instruction) || this.containsBannedContent(pair.output)) {
            return false;
        }

        // 3. Output repeating instruction check (Bad generation)
        if (pair.output.trim().toLowerCase() === pair.instruction.trim().toLowerCase()) {
            return false;
        }

        // Note: ROUGE-L similarity check against existing dataset is usually done here via a vector DB.
        
        return true;
    }

    public batchFilter(pairs: InstructionPair[]): InstructionPair[] {
        return pairs.filter(p => this.isValid(p));
    }
}
