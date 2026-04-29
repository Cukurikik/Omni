// nlux Conversational AI Stream Manager
// WebSocket-bound streaming for LLM chat responses

class OmniResult {
    constructor(isOk, value, error) {
        this.isOk = isOk; this.value = value; this.error = error;
    }
}

class NLUXStreamManager {
    constructor() {
        this.MAX_STREAMS = 10000;
        this.MAX_MSG_SIZE = 65536; // 64KB per message
        this.activeStreams = new Map();
    }

    createStream(sessionId, adapter) {
        if (this.activeStreams.size >= this.MAX_STREAMS) {
            return new OmniResult(false, null, new Error("Max concurrent streams reached"));
        }
        const stream = { sessionId, adapter, tokens: [], startTime: Date.now(), active: true };
        this.activeStreams.set(sessionId, stream);
        return new OmniResult(true, sessionId, null);
    }

    pushToken(sessionId, token) {
        const stream = this.activeStreams.get(sessionId);
        if (!stream || !stream.active) {
            return new OmniResult(false, null, new Error("Stream not found or inactive"));
        }
        if (token.length > this.MAX_MSG_SIZE) {
            return new OmniResult(false, null, new Error("Token chunk exceeds 64KB limit"));
        }
        stream.tokens.push(token);
        return new OmniResult(true, stream.tokens.length, null);
    }

    endStream(sessionId) {
        const stream = this.activeStreams.get(sessionId);
        if (!stream) return new OmniResult(false, null, new Error("Stream not found"));
        stream.active = false;
        this.activeStreams.delete(sessionId);
        return new OmniResult(true, { totalTokens: stream.tokens.length }, null);
    }
}

module.exports = { NLUXStreamManager, OmniResult };
