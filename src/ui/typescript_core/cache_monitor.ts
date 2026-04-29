export interface CacheStats {
    hits: number;
    misses: number;
}
export function getHitRatio(stats: CacheStats): number {
    const total = stats.hits + stats.misses;
    return total === 0 ? 0 : stats.hits / total;
}
