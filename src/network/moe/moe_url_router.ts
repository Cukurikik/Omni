// moe_url_router.ts — Network / Edge Routing
// Layer: Network / Edge — High-Speed Short URL Resolution
//
// Uses MoE conceptual mapping for URL shortener routing (inspired by short.moe).
// Routes short IDs to the appropriate physical database shard ("expert") to resolve
// the destination URL extremely quickly at the edge.

export interface URLResolutionResult {
    shortId: string;
    targetUrl: string;
    shardId: number;
    latencyMs: number;
}

export class MoEEdgeRouter {
    private numShards: number;
    
    constructor(numShards: number = 16) {
        this.numShards = numShards;
    }

    /**
     * Consistently hashes a short ID to determine which database shard ("expert")
     * holds the full URL record.
     */
    private determineShard(shortId: string): number {
        let hash = 0;
        for (let i = 0; i < shortId.length; i++) {
            const char = shortId.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32bit integer
        }
        return Math.abs(hash) % this.numShards;
    }

    /**
     * Resolves a short URL. Simulates querying the target shard.
     */
    public async resolve(shortId: string): Promise<URLResolutionResult> {
        const start = Date.now();
        
        // 1. "Route" to the expert shard
        const shardId = this.determineShard(shortId);
        
        // 2. Query the shard (Mock network call)
        const targetUrl = await this.queryShard(shardId, shortId);
        
        const latencyMs = Date.now() - start;
        
        return {
            shortId,
            targetUrl,
            shardId,
            latencyMs
        };
    }

    private async queryShard(shardId: number, shortId: string): Promise<string> {
        // Simulate DB latency (1-5ms)
        await new Promise(resolve => setTimeout(resolve, Math.random() * 4 + 1));
        
        // Return mock destination
        return `https://omni-framework.dev/resolved/${shortId}`;
    }
}

// Usage Example
async function main() {
    const router = new MoEEdgeRouter(16);
    const result = await router.resolve("AbCdE");
    console.log(`[Edge Router] Resolved in ${result.latencyMs}ms from Shard ${result.shardId}`);
}
