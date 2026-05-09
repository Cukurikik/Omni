// @omni-layer Event | @omni-lang MQTT (JavaScript/Node.js) | @omni-batch 17
// @omni-description IoT inference bridge: MQTT pub/sub client for
// edge-to-cloud inference requests with QoS and topic routing.

const mqtt = require('mqtt');

class OmniMQTTBridge {
  constructor(brokerUrl, options = {}) {
    this.brokerUrl = brokerUrl;
    this.clientId = options.clientId || `omni-inference-${Date.now()}`;
    this.topicPrefix = options.topicPrefix || 'omni/inference';
    this.qos = options.qos || 1;
    this.client = null;
    this.handlers = new Map();
    this.stats = { published: 0, received: 0, errors: 0 };
  }

  connect() {
    return new Promise((resolve, reject) => {
      this.client = mqtt.connect(this.brokerUrl, {
        clientId: this.clientId,
        clean: true,
        connectTimeout: 5000,
        reconnectPeriod: 3000,
      });
      this.client.on('connect', () => { console.log(`[OMNI-MQTT] Connected: ${this.clientId}`); resolve(); });
      this.client.on('error', (err) => { this.stats.errors++; reject(err); });
      this.client.on('message', (topic, payload) => this._handleMessage(topic, payload));
    });
  }

  subscribeInferenceRequests(modelId) {
    const topic = `${this.topicPrefix}/request/${modelId}`;
    this.client.subscribe(topic, { qos: this.qos }, (err) => {
      if (err) { this.stats.errors++; return; }
      console.log(`[OMNI-MQTT] Subscribed: ${topic}`);
    });
  }

  publishInferenceResult(modelId, requestId, result) {
    const topic = `${this.topicPrefix}/response/${modelId}/${requestId}`;
    const payload = JSON.stringify({
      request_id: requestId,
      model_id: modelId,
      output: result.output,
      confidence: result.confidence,
      latency_ms: result.latency_ms,
      timestamp: Date.now(),
    });
    this.client.publish(topic, payload, { qos: this.qos }, (err) => {
      if (err) this.stats.errors++;
      else this.stats.published++;
    });
  }

  publishTelemetry(deviceId, metrics) {
    const topic = `${this.topicPrefix}/telemetry/${deviceId}`;
    this.client.publish(topic, JSON.stringify({
      device_id: deviceId,
      gpu_utilization: metrics.gpuUtil || 0,
      memory_usage_mb: metrics.memoryMb || 0,
      inference_count: metrics.inferenceCount || 0,
      avg_latency_ms: metrics.avgLatency || 0,
      timestamp: Date.now(),
    }), { qos: 0 });
  }

  onInferenceRequest(modelId, handler) {
    this.handlers.set(`${this.topicPrefix}/request/${modelId}`, handler);
  }

  _handleMessage(topic, payload) {
    this.stats.received++;
    try {
      const data = JSON.parse(payload.toString());
      const handler = this.handlers.get(topic);
      if (handler) handler(data, topic);
    } catch (e) { this.stats.errors++; }
  }

  getStats() { return { ...this.stats, connected: this.client?.connected || false }; }

  disconnect() {
    if (this.client) this.client.end();
  }
}

module.exports = { OmniMQTTBridge };
