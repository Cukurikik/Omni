// OMNI Concurrency Layer — JavaScript Event Loop Inference Worker
// Non-blocking inference via Web Workers and event-driven architecture.

class OmniInferenceWorker {
  constructor(config = {}) {
    this.modelEndpoint = config.endpoint || 'http://localhost:8080/api/v1';
    this.maxConcurrent = config.maxConcurrent || 10;
    this.timeout = config.timeout || 30000;
    this.activeRequests = 0;
    this.queue = [];
    this.stats = { total: 0, errors: 0, totalLatencyMs: 0 };
  }

  async infer(prompt, options = {}) {
    if (this.activeRequests >= this.maxConcurrent) {
      return new Promise((resolve, reject) => {
        this.queue.push({ prompt, options, resolve, reject });
      });
    }
    return this._executeInference(prompt, options);
  }

  async _executeInference(prompt, options) {
    this.activeRequests++;
    const start = performance.now();
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(`${this.modelEndpoint}/infer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          max_tokens: options.maxTokens || 256,
          temperature: options.temperature || 0.7,
          top_p: options.topP || 0.9,
        }),
        signal: controller.signal,
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const result = await response.json();
      const latency = performance.now() - start;
      this.stats.total++;
      this.stats.totalLatencyMs += latency;
      return { ...result, latencyMs: latency };
    } catch (err) {
      this.stats.errors++;
      throw err;
    } finally {
      clearTimeout(timeoutId);
      this.activeRequests--;
      this._processQueue();
    }
  }

  async *stream(prompt, options = {}) {
    const response = await fetch(`${this.modelEndpoint}/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, stream: true, ...options }),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      for (const line of lines) {
        if (line.startsWith('data: ') && line !== 'data: [DONE]') {
          try { yield JSON.parse(line.slice(6)); } catch {}
        }
      }
    }
  }

  _processQueue() {
    while (this.queue.length > 0 && this.activeRequests < this.maxConcurrent) {
      const { prompt, options, resolve, reject } = this.queue.shift();
      this._executeInference(prompt, options).then(resolve).catch(reject);
    }
  }

  getStats() {
    return {
      ...this.stats,
      avgLatencyMs: this.stats.total > 0 ? this.stats.totalLatencyMs / this.stats.total : 0,
      queueDepth: this.queue.length,
      activeRequests: this.activeRequests,
    };
  }
}

// Softmax utility (for client-side logit processing)
function softmax(logits) {
  const max = Math.max(...logits);
  const exps = logits.map(x => Math.exp(x - max));
  const sum = exps.reduce((a, b) => a + b, 0);
  return exps.map(x => x / sum);
}

// Cosine similarity
function cosineSimilarity(a, b) {
  let dot = 0, normA = 0, normB = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i]; normA += a[i] ** 2; normB += b[i] ** 2;
  }
  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}

if (typeof module !== 'undefined') {
  module.exports = { OmniInferenceWorker, softmax, cosineSimilarity };
}
