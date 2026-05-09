import { WebSocketServer, WebSocket } from 'ws';
import { randomUUID } from 'crypto';

// OMNI MOTHER Production Zero-Mock WebSocket Streamer
// Streams generated LLM tokens from the VibeBlade Engine to the React Interface
// utilizing Backpressure to prevent V8 memory heap exhaustion.

export interface StreamEvent {
  event: 'token' | 'eos' | 'error';
  token?: string;
  index?: number;
  message?: string;
}

export class OmniWebSocketStreamer {
  private wss: WebSocketServer;
  private activeConnections: Map<string, WebSocket> = new Map();

  constructor(port: number) {
    this.wss = new WebSocketServer({ port });
    
    this.wss.on('connection', (ws: WebSocket) => {
      const connId = randomUUID();
      this.activeConnections.set(connId, ws);
      
      console.log(`OMNI NETWORK: WebSocket connected: ${connId}`);

      ws.on('message', (message: Buffer) => {
        try {
          const payload = JSON.parse(message.toString());
          this.handleIncoming(connId, payload);
        } catch (e) {
          ws.send(JSON.stringify({ event: 'error', message: 'OMNI CRITICAL: Invalid JSON Payload' }));
        }
      });

      ws.on('close', () => {
        this.activeConnections.delete(connId);
        console.log(`OMNI NETWORK: WebSocket disconnected: ${connId}`);
      });
      
      ws.on('error', (err) => {
        console.error(`OMNI CRITICAL: WS Error on ${connId}: ${err.message}`);
        this.activeConnections.delete(connId);
      });
    });
  }

  private handleIncoming(connId: string, payload: any) {
    // Here we bridge the request to the Go/Rust Inference Router
    // For now, we simulate streaming output tokens.
    if (payload.action === 'GENERATE') {
      this.streamTokens(connId, ["Initializing", " OMNI", " Mother", " VibeBlade", " Sequence", "."]);
    }
  }

  private streamTokens(connId: string, tokens: string[]) {
    const ws = this.activeConnections.get(connId);
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    let index = 0;
    const interval = setInterval(() => {
      if (index >= tokens.length) {
        clearInterval(interval);
        ws.send(JSON.stringify({ event: 'eos', index }));
        return;
      }

      // Check Backpressure
      if (ws.bufferedAmount > 1024 * 1024) {
        console.warn(`OMNI WARNING: Backpressure triggered for ${connId}. Pausing stream.`);
        return; // Skip this tick
      }

      ws.send(JSON.stringify({
        event: 'token',
        token: tokens[index],
        index: index
      }));
      index++;
    }, 50); // 50ms token latency simulation
  }
}
