// @omni-layer Interface | @omni-source huggingface/text-generation-inference
// @omni-description TGI inference playground: interactive text generation with
// streaming output, parameter tuning, and latency metrics.
// @omni-lang TypeScript | @omni-batch 16 | @omni-semester 16

interface GenerationParams {
  max_new_tokens: number;
  temperature: number;
  top_p: number;
  top_k: number;
  repetition_penalty: number;
  do_sample: boolean;
}

interface StreamingToken {
  token: string;
  token_id: number;
  logprob: number;
  cumulative_text: string;
  latency_ms: number;
}

class TGIPlayground {
  private params: GenerationParams;
  private history: StreamingToken[] = [];

  constructor() {
    this.params = {
      max_new_tokens: 256, temperature: 0.7, top_p: 0.9,
      top_k: 50, repetition_penalty: 1.1, do_sample: true
    };
  }

  updateParam<K extends keyof GenerationParams>(key: K, value: GenerationParams[K]): void {
    this.params[key] = value;
  }

  simulateGeneration(prompt: string): { data?: any; error?: string } {
    try {
      const tokens: StreamingToken[] = [];
      const words = "The quick brown fox jumps over the lazy dog in the moonlight".split(" ");
      let text = "";
      const startTime = Date.now();
      for (let i = 0; i < Math.min(this.params.max_new_tokens, 50); i++) {
        const word = words[i % words.length];
        text += (i > 0 ? " " : "") + word;
        tokens.push({
          token: word, token_id: word.charCodeAt(0) * 100 + i,
          logprob: -Math.random() * 3, cumulative_text: text,
          latency_ms: 20 + Math.random() * 30
        });
      }
      const totalMs = Date.now() - startTime;
      this.history = tokens;
      return { data: {
        generated_text: text, n_tokens: tokens.length,
        total_latency_ms: totalMs,
        tokens_per_second: tokens.length / Math.max(totalMs / 1000, 0.001),
        params: { ...this.params }
      }};
    } catch (e) { return { error: `Generation failed: ${e}` }; }
  }

  getHistory(): StreamingToken[] { return this.history; }
}

export { TGIPlayground };
export type { GenerationParams, StreamingToken };
