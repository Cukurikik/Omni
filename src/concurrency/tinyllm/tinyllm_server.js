// TinyLLM websocket non-blocking server
// JS event loop bound management

class OmniResult {
    constructor(isOk, value, error) {
        this.isOk = isOk;
        this.value = value;
        this.error = error;
    }
}

class TinyLLMWSServer {
    constructor() {
        this.MAX_CONNECTIONS = 50; // TinyLLM is for local consumer hardware
        this.activeConnections = 0;
    }

    onConnection() {
        if (this.activeConnections >= this.MAX_CONNECTIONS) {
            return new OmniResult(false, null, new Error("Local LLM max connections reached"));
        }

        this.activeConnections++;
        return new OmniResult(true, "Connected", null);
    }
    
    onDisconnect() {
        if (this.activeConnections > 0) {
            this.activeConnections--;
        }
    }
}

module.exports = { TinyLLMWSServer, OmniResult };
