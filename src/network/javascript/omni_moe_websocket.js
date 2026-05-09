/**
 * OMNI Framework - MoE WebSocket Streaming Server (Node.js)
 * Connects web clients to the MoE inference engine for low-latency,
 * token-by-token streaming responses. Uses Redis Pub/Sub to receive
 * tokens from the Go API Gateway / C++ execution engine.
 */

const { WebSocketServer } = require('ws');
const Redis = require('ioredis');

const PORT = 8081;
const wss = new WebSocketServer({ port: PORT });
const redisSubscriber = new Redis({ host: 'omni-redis', port: 6379 });

console.log(`OMNI Node.js: WebSocket Server listening on port ${PORT}`);

// Subscribe to the global inference stream channel
redisSubscriber.subscribe('moe_inference_stream', (err, count) => {
    if (err) {
        console.error('Failed to subscribe: %s', err.message);
    } else {
        console.log(`OMNI Node.js: Subscribed successfully. Waiting for tokens...`);
    }
});

// Maintain a map of session IDs to WebSocket connections
const activeSessions = new Map();

wss.on('connection', function connection(ws) {
    let currentSessionId = null;

    ws.on('message', function message(data) {
        try {
            const req = JSON.parse(data);
            if (req.action === 'start_stream') {
                currentSessionId = req.session_id;
                activeSessions.set(currentSessionId, ws);
                console.log(`OMNI Node.js: Client initiated session ${currentSessionId}`);
                
                // In a full implementation, we would HTTP POST to the Go Gateway
                // to start the inference process, passing the session_id.
            }
        } catch (e) {
            console.error("Invalid message format");
        }
    });

    ws.on('close', () => {
        if (currentSessionId) {
            activeSessions.delete(currentSessionId);
            console.log(`OMNI Node.js: Session ${currentSessionId} closed.`);
        }
    });
});

// Listen for tokens coming from the backend engine via Redis
redisSubscriber.on('message', (channel, message) => {
    if (channel === 'moe_inference_stream') {
        const payload = JSON.parse(message);
        // payload format: { session_id: "uuid", text: "word", is_final: false }
        
        const clientWs = activeSessions.get(payload.session_id);
        if (clientWs && clientWs.readyState === 1) { // WebSocket.OPEN
            clientWs.send(JSON.stringify({
                text: payload.text,
                is_final: payload.is_final
            }));
            
            if (payload.is_final) {
                // Keep connection open for next prompt, but could delete from map
            }
        }
    }
});
