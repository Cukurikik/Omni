// moe_listen_moe_radio_bridge.js — Network
// Layer: Network — LISTEN.moe Webcast Bridge
// Inspired by: LISTEN.moe-html (Anime Radio Playlist Stream)

import { WebSocket } from 'ws';
import { EventEmitter } from 'events';

export class ListenMoeBridge extends EventEmitter {
    constructor() {
        super();
        this.wsEndpoint = 'wss://listen.moe/gateway_v2';
        this.ws = null;
        this.heartbeatInterval = null;
    }

    connect() {
        this.ws = new WebSocket(this.wsEndpoint);

        this.ws.on('open', () => {
            console.log('[LISTEN.moe] Connected to Anime Radio Gateway');
        });

        this.ws.on('message', (data) => {
            try {
                const payload = JSON.parse(data.toString());
                this.handleOpcode(payload);
            } catch (err) {
                console.error('[LISTEN.moe] Parse error:', err);
            }
        });

        this.ws.on('close', () => {
            console.log('[LISTEN.moe] Disconnected. Reconnecting in 5s...');
            clearInterval(this.heartbeatInterval);
            setTimeout(() => this.connect(), 5000);
        });
    }

    handleOpcode(payload) {
        switch (payload.op) {
            case 0: // HELLO
                const interval = payload.d.heartbeat;
                this.heartbeatInterval = setInterval(() => {
                    this.ws.send(JSON.stringify({ op: 9 }));
                }, interval);
                break;
            case 1: // EVENT (Track Update)
                if (payload.t === 'TRACK_UPDATE') {
                    this.emit('track_change', payload.d);
                }
                break;
        }
    }
}
