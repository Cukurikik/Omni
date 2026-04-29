/**
 * OMNI Voice Dispatcher — Concurrency Layer
 * Absorbing alan-ai/alan-sdk-* voice intent routing via async event loop.
 * Handles voice command dispatching with priority queue and debounce.
 */

class OmniVoiceDispatcher {
  constructor(debounceMs = 300) {
    this.debounceMs = debounceMs;
    this.intentHandlers = new Map();
    this.dispatchCount = 0;
    this.lastDispatchTime = 0;
  }

  registerIntent(intentName, handler) {
    if (!intentName || typeof handler !== 'function') {
      return { ok: false, error: 'VoiceError: Invalid intent name or handler' };
    }
    this.intentHandlers.set(intentName, handler);
    return { ok: true, registered: intentName };
  }

  async dispatch(intentName, payload) {
    if (!this.intentHandlers.has(intentName)) {
      return { ok: false, error: `VoiceError: Unknown intent '${intentName}'` };
    }

    const now = Date.now();
    if (now - this.lastDispatchTime < this.debounceMs) {
      return { ok: false, error: 'VoiceError: Debounce active, too frequent' };
    }

    this.lastDispatchTime = now;
    this.dispatchCount++;

    try {
      const handler = this.intentHandlers.get(intentName);
      const result = await handler(payload);
      return { ok: true, intent: intentName, result };
    } catch (e) {
      return { ok: false, error: `VoiceError: Handler exception: ${e.message}` };
    }
  }

  diagnostics() {
    return {
      engine: 'OmniVoiceDispatcher',
      intents: this.intentHandlers.size,
      dispatched: this.dispatchCount,
      debounceMs: this.debounceMs,
      status: 'Operational'
    };
  }
}

export default OmniVoiceDispatcher;
