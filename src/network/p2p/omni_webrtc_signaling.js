const express = require('express');
const { Server } = require('ws');

// Omni WebRTC Signaling Server (Node.js/JS)
// Networking & P2P Layer
// Acts as a signaling intermediary to establish peer-to-peer WebRTC connections
// between edge clients and Omni nodes for low-latency inference streaming.

const app = express();
const PORT = process.env.PORT || 3000;

// Setup HTTP server
const server = app.listen(PORT, () => {
    console.log(`Omni WebRTC Signaling Server running on port ${PORT}`);
});

// Setup WebSocket server
const wss = new Server({ server });

// Track connected clients
const clients = new Map();

wss.on('connection', (ws) => {
    const id = generateId();
    clients.set(id, ws);
    console.log(`Client connected: ${id}`);

    ws.on('message', (message) => {
        let data;
        try {
            data = JSON.parse(message);
        } catch (e) {
            console.error("Invalid JSON received");
            return;
        }

        // Signaling logic: Relay ICE candidates and SDP offers/answers
        if (data.type === 'offer' || data.type === 'answer' || data.type === 'candidate') {
            const targetId = data.target;
            const targetWs = clients.get(targetId);
            
            if (targetWs && targetWs.readyState === ws.OPEN) {
                // Attach the sender's ID and forward the payload
                data.sender = id;
                targetWs.send(JSON.stringify(data));
            } else {
                console.log(`Target client ${targetId} not found or disconnected.`);
            }
        }
    });

    ws.on('close', () => {
        clients.delete(id);
        console.log(`Client disconnected: ${id}`);
    });
});

function generateId() {
    return Math.random().toString(36).substring(2, 9);
}
