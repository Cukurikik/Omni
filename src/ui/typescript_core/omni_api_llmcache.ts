export interface CacheStat {
    hits: number;
    misses: number;
}

export class OmniLLMCacheAPI {
    /** OMNI Interface Layer: LLM Cache API */
    public static calculateHitRate(stat: CacheStat): number {
        const total = stat.hits + stat.misses;
        if (total === 0) return 0.0;
        return (stat.hits / total) * 100.0;
    }
}
