/**
 * OMNI Vision Event Bus - Concurrency Layer
 * Implements high-throughput, asynchronous Publisher-Subscriber pattern natively in ECMAScript.
 * Zero external mock frameworks; completely reliant on internal event loop mechanics.
 */

class OmniVisionEventBus {
  constructor() {
    this.subscribers = new Map();
    this.metrics = {
      totalEmitted: 0,
      totalDropped: 0,
    };
  }

  /**
   * Subscribes to a visual topic.
   * @param {string} topic - The topic identifier.
   * @param {Function} callback - The async function to handle payload.
   * @returns {Object} Monadic Result
   */
  subscribe(topic, callback) {
    if (typeof topic !== 'string' || typeof callback !== 'function') {
      return { ok: false, error: 'VisionBusError: Invalid argument types' };
    }

    if (!this.subscribers.has(topic)) {
      this.subscribers.set(topic, new Set());
    }

    this.subscribers.get(topic).add(callback);

    return {
      ok: true,
      unsubscribe: () => this.subscribers.get(topic).delete(callback)
    };
  }

  /**
   * Emits a vision payload to the event bus asynchronously.
   * Maps immediately to microtask queue to unblock the main thread.
   */
  emit(topic, payload) {
    if (!this.subscribers.has(topic) || this.subscribers.get(topic).size === 0) {
      this.metrics.totalDropped++;
      return { ok: false, error: 'VisionBusError: No subscribers for topic' };
    }

    const callbacks = Array.from(this.subscribers.get(topic));
    
    // Non-blocking fire-and-forget processing via Promises
    Promise.resolve().then(() => {
      for (let i = 0; i < callbacks.length; i++) {
        try {
          callbacks[i](payload);
        } catch (e) {
          // Log explicitly, prevent cascading failure in concurrency loop
          console.error(`VisionBusError: Callback execution failed on topic ${topic}: ${e.message}`);
        }
      }
    });

    this.metrics.totalEmitted++;
    return { ok: true, matchedSubscribers: callbacks.length };
  }

  diagnostics() {
    return {
      engine: 'OmniVisionEventBus',
      topics: this.subscribers.size,
      metrics: this.metrics,
      status: 'operational'
    };
  }
}

export const visionBus = new OmniVisionEventBus();
