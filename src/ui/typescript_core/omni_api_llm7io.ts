export interface GatewayRequest {
    provider: string;
    payload: string;
    maxLatency: number;
}

export class OmniLLM7ioAPI {
    /** OMNI Interface Layer: LLM7io API */
    public static constructHeaders(req: GatewayRequest, apiKey: string): Record<string, string> {
        if (!apiKey) throw new Error("API Key is required");
        return {
            "Authorization": `Bearer ${apiKey}`,
            "X-Target-Provider": req.provider,
            "X-Max-Latency": req.maxLatency.toString()
        };
    }
}
