export interface FilterConfig {
    minWords: number;
    maxWords: number;
    minEntropy: number;
}

export class OmniDataJuicerAPI {
    /** OMNI Interface Layer: DataJuicer API */
    public static applyRules(text: string, config: FilterConfig, entropy: number): boolean {
        const words = text.split(/\s+/).length;
        if (words < config.minWords || words > config.maxWords) return false;
        if (entropy < config.minEntropy) return false;
        return true;
    }
}
