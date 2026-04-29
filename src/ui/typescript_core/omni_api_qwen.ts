export interface TokenStats {
    totalTokens: number;
    langCode: number;
}

export class OmniQwenAPI {
    /** OMNI Interface Layer: Qwen API */
    public static printStats(stats: TokenStats): string {
        return `Qwen Tokens: ${stats.totalTokens} | Lang: ${stats.langCode === 1 ? 'CJK' : 'Latin'}`;
    }
}
