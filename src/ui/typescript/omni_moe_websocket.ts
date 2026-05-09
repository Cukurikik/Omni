// OMNI MOTHER: WebSocket Client for Real-time Dashboard Updates
// Avoids GraphQL polling overhead by streaming events.

export class OmniMoEWebSocket {
    private ws: WebSocket | null = null;
    private url: string;
    private onMessageCallback: (data: any) => void;

    constructor(url: string, onMessage: (data: any) => void) {
        this.url = url;
        this.onMessageCallback = onMessage;
    }

    connect() {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
            console.log('[OMNI] WebSocket connected to MoE telemetry stream');
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.onMessageCallback(data);
            } catch (err) {
                console.error('[OMNI ERROR] Invalid WS payload', err);
            }
        };

        this.ws.onclose = () => {
            console.warn('[OMNI] WebSocket closed, retrying in 5s...');
            setTimeout(() => this.connect(), 5000);
        };

        this.ws.onerror = (err) => {
            console.error('[OMNI ERROR] WebSocket error', err);
            this.ws?.close();
        };
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}
