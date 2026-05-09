// OMNI MOTHER: Resilient WebSocket Manager (Production Grade)

export class OmniWebSocketManager {
    private url: string;
    private ws: WebSocket | null = null;
    private reconnectAttempts = 0;

    constructor(url: string) {
        this.url = url;
    }

    public connect(onMessage: (data: any) => void) {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
            console.log(`[OMNI WS] Connected to ${this.url}`);
            this.reconnectAttempts = 0;
        };

        this.ws.onmessage = (event) => {
            try {
                const payload = JSON.parse(event.data);
                onMessage(payload);
            } catch (e) {
                console.error("[OMNI WS] Parse error", e);
            }
        };

        this.ws.onclose = () => {
            console.warn(`[OMNI WS] Disconnected. Reconnecting in ${this.reconnectAttempts}s...`);
            setTimeout(() => this.connect(onMessage), Math.min(5000, 1000 * Math.pow(2, this.reconnectAttempts++)));
        };
    }

    public send(data: any) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }
}
