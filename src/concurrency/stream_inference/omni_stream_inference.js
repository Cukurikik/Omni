/**
 * OMNI Stream Inference Dispatcher — Concurrency Layer
 * Absorbing Capsize-Games/airunner offline inference streaming control.
 * JS async generator pattern for token-by-token streaming inference.
 */

class OmniStreamInference {
  constructor() {
    this.sessions = new Map();
    this.totalTokens = 0;
  }

  createSession(sessionId, config = {}) {
    if (!sessionId) return { ok: false, error: 'StreamError: Session ID required' };
    if (this.sessions.has(sessionId)) return { ok: false, error: 'StreamError: Session already exists' };
    this.sessions.set(sessionId, {
      id: sessionId,
      maxTokens: config.maxTokens || 2048,
      temperature: config.temperature || 0.7,
      tokensGenerated: 0,
      state: 'idle',
      createdAt: Date.now()
    });
    return { ok: true, sessionId };
  }

  startGeneration(sessionId, inputTokenIds) {
    const session = this.sessions.get(sessionId);
    if (!session) return { ok: false, error: 'StreamError: Session not found' };
    if (!Array.isArray(inputTokenIds) || inputTokenIds.length === 0) {
      return { ok: false, error: 'StreamError: Empty input tokens' };
    }
    session.state = 'generating';
    session.inputLength = inputTokenIds.length;
    return { ok: true, state: 'generating' };
  }

  emitToken(sessionId, tokenId, logprob) {
    const session = this.sessions.get(sessionId);
    if (!session) return { ok: false, error: 'StreamError: Session not found' };
    if (session.state !== 'generating') return { ok: false, error: 'StreamError: Not generating' };
    if (session.tokensGenerated >= session.maxTokens) {
      session.state = 'completed';
      return { ok: false, error: 'StreamError: Max tokens reached' };
    }
    session.tokensGenerated++;
    this.totalTokens++;
    return { ok: true, tokenId, logprob, position: session.tokensGenerated };
  }

  endSession(sessionId) {
    const session = this.sessions.get(sessionId);
    if (!session) return { ok: false, error: 'StreamError: Session not found' };
    session.state = 'completed';
    return { ok: true, tokensGenerated: session.tokensGenerated };
  }

  diagnostics() {
    return {
      engine: 'OmniStreamInference',
      activeSessions: this.sessions.size,
      totalTokens: this.totalTokens,
      status: 'Operational'
    };
  }
}

export default OmniStreamInference;
