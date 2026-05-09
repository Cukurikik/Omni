// @omni-layer Concurrency | @omni-lang JavaScript | @omni-batch 18 | @omni-semester 16
// @omni-description Node.js event-driven transformer inference broker
// with WebSocket streaming, queue management, and backpressure control.

const EventEmitter = require('events');

class InferenceBroker extends EventEmitter {
  constructor(maxConcurrent = 8, queueLimit = 1000) {
    super();
    this.maxConcurrent = maxConcurrent;
    this.queueLimit = queueLimit;
    this.queue = [];
    this.active = new Map();
    this.stats = { processed: 0, failed: 0, totalLatencyMs: 0 };
  }

  submit(request) {
    if (this.queue.length >= this.queueLimit) {
      this.emit('backpressure', { queueSize: this.queue.length });
      return { status: 'rejected', reason: 'queue_full' };
    }
    const id = `req_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    const entry = { id, request, status: 'queued', createdAt: Date.now() };
    this.queue.push(entry);
    this.emit('queued', { id, queueSize: this.queue.length });
    this._processNext();
    return { status: 'queued', requestId: id, position: this.queue.length };
  }

  _processNext() {
    while (this.active.size < this.maxConcurrent && this.queue.length > 0) {
      const entry = this.queue.shift();
      entry.status = 'processing';
      entry.startedAt = Date.now();
      this.active.set(entry.id, entry);
      this._executeInference(entry)
        .then(result => this._onComplete(entry, result))
        .catch(err => this._onError(entry, err));
    }
  }

  async _executeInference(entry) {
    const { request } = entry;
    const tokens = request.tokenIds || [];
    const outputLen = Math.min(request.maxTokens || 64, 256);
    const output = [];
    for (let i = 0; i < outputLen; i++) {
      const seed = tokens.reduce((a, b) => a + b, 0) + i;
      const tokenId = Math.abs(Math.round(Math.sin(seed * 0.001) * 16000)) % 32000;
      output.push(tokenId);
      if (request.stream) {
        this.emit('token', { requestId: entry.id, tokenId, step: i });
      }
      if (tokenId === 2) break;
    }
    return { outputIds: output, model: request.modelId || 'default' };
  }

  _onComplete(entry, result) {
    const latency = Date.now() - entry.startedAt;
    this.stats.processed++;
    this.stats.totalLatencyMs += latency;
    this.active.delete(entry.id);
    this.emit('completed', { requestId: entry.id, result, latencyMs: latency });
    this._processNext();
  }

  _onError(entry, error) {
    this.stats.failed++;
    this.active.delete(entry.id);
    this.emit('error', { requestId: entry.id, error: error.message });
    this._processNext();
  }

  getStats() {
    return {
      ...this.stats,
      avgLatencyMs: this.stats.processed > 0
        ? this.stats.totalLatencyMs / this.stats.processed : 0,
      activeRequests: this.active.size,
      queuedRequests: this.queue.length,
    };
  }

  drain() {
    return new Promise(resolve => {
      const check = () => {
        if (this.active.size === 0 && this.queue.length === 0) resolve();
        else setTimeout(check, 50);
      };
      check();
    });
  }
}

module.exports = { InferenceBroker };
