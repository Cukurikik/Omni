// moe_sse_streaming.ts — Interface / Network
// Layer: Interface / API — Server-Sent Events (SSE) Client
//
// MoE inference yields tokens dynamically. Standard HTTP waits for the entire
// response. This TypeScript module connects to the Go Gateway via SSE
// (EventSource) to stream generated tokens to the UI in real-time as they 
// emerge from the GPU cluster.

export class MoEStreamingClient {
    private eventSource: EventSource | null = null;

    constructor(private gatewayUrl: string) {
        console.log(`[SSE Client] Configured MoE Streaming endpoint: ${gatewayUrl}`);
    }

    /**
     * Connects to the Go Gateway and streams tokens via Server-Sent Events.
     */
    public startStream(
        prompt: string, 
        tenantToken: string,
        onToken: (token: string) => void,
        onError: (err: any) => void,
        onComplete: () => void
    ): void {
        const url = new URL(this.gatewayUrl);
        url.searchParams.append('prompt', encodeURIComponent(prompt));
        url.searchParams.append('auth', tenantToken);

        this.eventSource = new EventSource(url.toString());

        this.eventSource.onmessage = (event) => {
            try {
                // Assuming Go backend sends: data: {"token": "hello", "is_final": false}
                const payload = JSON.parse(event.data);
                
                if (payload.is_final) {
                    this.closeStream();
                    onComplete();
                } else {
                    onToken(payload.token);
                }
            } catch (err) {
                console.error("[SSE Client] Payload parsing error:", err);
            }
        };

        this.eventSource.onerror = (err) => {
            console.error("[SSE Client] Connection lost or failed.");
            this.closeStream();
            onError(err);
        };
        
        console.log("[SSE Client] Stream connected. Awaiting tokens...");
    }

    public closeStream(): void {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
            console.log("[SSE Client] Stream closed.");
        }
    }
}
