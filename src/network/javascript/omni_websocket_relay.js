const WebSocket = require('ws');

class OmniWebSocketRelay {
    constructor(port) {
        this.wss = new WebSocket.Server({ port });
        this.clients = new Set();
        
        this.wss.on('connection', (ws) => {
            console.log('OMNI WS Client Connected');
            this.clients.add(ws);
            
            ws.on('message', (message) => {
                this.broadcast(`[Relay]: ${message}`);
            });
            
            ws.on('close', () => {
                this.clients.delete(ws);
            });
        });
        
        console.log(`OMNI WS Relay listening on port ${port}`);
    }

    broadcast(data) {
        for (let client of this.clients) {
            if (client.readyState === WebSocket.OPEN) {
                client.send(data);
            }
        }
    }
}

module.exports = OmniWebSocketRelay;
