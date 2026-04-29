// OMNI SUPABASE: Realtime Client
// TypeScript implementation of a resilient WebSocket client for Supabase Realtime subscriptions.
// Source: supabase/realtime

import { WebSocket } from 'ws';

export type RealtimeEvent = {
    schema: string;
    table: string;
    type: 'INSERT' | 'UPDATE' | 'DELETE';
    record: any;
    old_record?: any;
};

export class OmniRealtimeClient {
    private ws: WebSocket | null = null;
    private endpoint: string;
    private apikey: string;
    private reconnectAttempts = 0;
    private maxReconnects = 5;

    constructor(endpoint: string, apikey: string) {
        this.endpoint = endpoint;
        this.apikey = apikey;
    }

    public connect(onEvent: (evt: RealtimeEvent) => void): void {
        const url = `${this.endpoint}?apikey=${this.apikey}&vsn=1.0.0`;
        this.ws = new WebSocket(url);

        this.ws.on('open', () => {
            console.log('[Omni Realtime] Connected to Phoenix Channels');
            this.reconnectAttempts = 0;
            
            // Join the realtime:public channel
            const joinMsg = {
                topic: 'realtime:public',
                event: 'phx_join',
                payload: {},
                ref: '1'
            };
            this.ws?.send(JSON.stringify(joinMsg));
        });

        this.ws.on('message', (data: string) => {
            try {
                const msg = JSON.parse(data);
                if (msg.event === 'postgres_changes') {
                    onEvent(msg.payload as RealtimeEvent);
                }
            } catch (e) {
                console.error('[Omni Realtime] Failed to parse message', e);
            }
        });

        this.ws.on('close', () => {
            console.warn('[Omni Realtime] Connection closed. Attempting reconnect...');
            this.handleReconnect(onEvent);
        });

        this.ws.on('error', (err) => {
            console.error('[Omni Realtime] Socket error', err);
        });
    }

    private handleReconnect(onEvent: (evt: RealtimeEvent) => void) {
        if (this.reconnectAttempts >= this.maxReconnects) {
            console.error('[Omni Realtime] Max reconnect attempts reached. Halting.');
            return;
        }

        const backoffMs = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
        this.reconnectAttempts++;

        setTimeout(() => {
            console.log(`[Omni Realtime] Reconnecting (Attempt ${this.reconnectAttempts})...`);
            this.connect(onEvent);
        }, backoffMs);
    }
}
