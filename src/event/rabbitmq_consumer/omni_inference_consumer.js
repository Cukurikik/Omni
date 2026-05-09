// @omni-layer Event | @omni-lang JavaScript | @omni-batch 18 | @omni-semester 16
// @omni-description RabbitMQ inference event consumer: processes transformer
// inference requests from queue with retry, DLQ, and metric emission.

const EventEmitter = require('events');

class RabbitMQConsumer extends EventEmitter {
  constructor(config = {}) {
    super();
    this.queue = config.queue || 'omni.inference.requests';
    this.dlq = config.dlq || 'omni.inference.dlq';
    this.maxRetries = config.maxRetries || 3;
    this.prefetch = config.prefetch || 10;
    this.stats = { consumed: 0, processed: 0, failed: 0, retried: 0 };
    this._handlers = new Map();
    this._running = false;
  }

  registerHandler(modelType, handler) {
    this._handlers.set(modelType, handler);
  }

  async start() {
    this._running = true;
    this.emit('started', { queue: this.queue });
  }

  async stop() {
    this._running = false;
    this.emit('stopped', { stats: this.stats });
  }

  async processMessage(msg) {
    this.stats.consumed++;
    const startTime = Date.now();
    try {
      const payload = typeof msg === 'string' ? JSON.parse(msg) : msg;
      const modelType = payload.model_type || 'default';
      const handler = this._handlers.get(modelType) || this._handlers.get('default');
      if (!handler) {
        throw new Error(`No handler for model type: ${modelType}`);
      }
      const retryCount = payload._retry_count || 0;
      const result = await handler(payload);
      const latency = Date.now() - startTime;
      this.stats.processed++;
      this.emit('processed', {
        requestId: payload.request_id,
        modelType,
        latencyMs: latency,
        result: result,
      });
      return { status: 'processed', result, latencyMs: latency };
    } catch (error) {
      const payload = typeof msg === 'string' ? JSON.parse(msg) : msg;
      const retryCount = (payload._retry_count || 0) + 1;
      if (retryCount <= this.maxRetries) {
        this.stats.retried++;
        payload._retry_count = retryCount;
        this.emit('retry', { requestId: payload.request_id, attempt: retryCount });
        return { status: 'retry', attempt: retryCount };
      }
      this.stats.failed++;
      this.emit('dlq', { requestId: payload.request_id, error: error.message });
      return { status: 'dlq', error: error.message };
    }
  }

  getStats() {
    return {
      ...this.stats,
      successRate: this.stats.consumed > 0
        ? ((this.stats.processed / this.stats.consumed) * 100).toFixed(1) + '%'
        : '0%',
    };
  }
}

module.exports = { RabbitMQConsumer };
