export class OmniAIRemindAPI {
    public static lruEvict<T>(cache: Map<string, {item: T; age: number}>, maxSize: number): string | null {
        if (cache.size < maxSize) return null;
        let oldest = '', maxAge = -1;
        for (const [k, v] of cache) { if (v.age > maxAge) { maxAge = v.age; oldest = k; } }
        cache.delete(oldest);
        return oldest;
    }
}
