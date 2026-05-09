// OMNI Interface — TypeScript Inference SDK
// Type-safe client SDK for browser and Node.js environments.

export interface InferenceConfig {
  baseUrl: string;
  apiKey?: string;
  maxRetries: number;
  timeoutMs: number;
}

export interface InferRequest {
  prompt: string;
  maxTokens?: number;
  temperature?: number;
  topP?: number;
  stopSequences?: string[];
  stream?: boolean;
}

export interface InferResponse {
  requestId: string;
  generatedText: string;
  tokenCount: number;
  latencyMs: number;
  model: string;
}

export interface EmbedResponse {
  embeddings: number[][];
  model: string;
  dimensions: number;
}

export interface SDKStats {
  totalRequests: number;
  totalErrors: number;
  avgLatencyMs: number;
  cacheHits: number;
}

export class OmniSDK {
  private config: InferenceConfig;
  private stats: SDKStats = { totalRequests: 0, totalErrors: 0, avgLatencyMs: 0, cacheHits: 0 };
  private cache = new Map<string, { result: InferResponse; expiry: number }>();

  constructor(config: Partial<InferenceConfig> = {}) {
    this.config = {
      baseUrl: config.baseUrl || 'http://localhost:8080/api/v1',
      apiKey: config.apiKey,
      maxRetries: config.maxRetries ?? 3,
      timeoutMs: config.timeoutMs ?? 30000,
    };
  }

  async infer(request: InferRequest): Promise<InferResponse> {
    const cacheKey = this.getCacheKey(request);
    const cached = this.cache.get(cacheKey);
    if (cached && cached.expiry > Date.now()) {
      this.stats.cacheHits++;
      return cached.result;
    }

    const start = Date.now();
    this.stats.totalRequests++;

    const body: InferRequest = {
      prompt: request.prompt,
      maxTokens: request.maxTokens ?? 256,
      temperature: request.temperature ?? 0.7,
      topP: request.topP ?? 0.9,
      stopSequences: request.stopSequences ?? [],
    };

    const response = await this.fetchWithRetry<InferResponse>('/infer', 'POST', body);
    response.latencyMs = Date.now() - start;
    this.updateAvgLatency(response.latencyMs);

    this.cache.set(cacheKey, { result: response, expiry: Date.now() + 60000 });
    if (this.cache.size > 500) {
      const oldest = this.cache.keys().next().value;
      if (oldest) this.cache.delete(oldest);
    }

    return response;
  }

  async *inferStream(request: InferRequest): AsyncGenerator<string> {
    const response = await fetch(`${this.config.baseUrl}/infer/stream`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ ...request, stream: true }),
      signal: AbortSignal.timeout(this.config.timeoutMs),
    });

    const reader = response.body?.getReader();
    if (!reader) throw new Error('No response body');
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });
      for (const line of chunk.split('\n')) {
        if (line.startsWith('data: ') && line !== 'data: [DONE]') {
          const data = JSON.parse(line.slice(6));
          yield data.token || '';
        }
      }
    }
  }

  async embed(texts: string[]): Promise<EmbedResponse> {
    return this.fetchWithRetry<EmbedResponse>('/embed', 'POST', { texts });
  }

  async health(): Promise<Record<string, unknown>> {
    return this.fetchWithRetry('/health', 'GET');
  }

  getStats(): SDKStats { return { ...this.stats }; }

  private async fetchWithRetry<T>(path: string, method: string, body?: unknown): Promise<T> {
    let lastError: Error | null = null;
    for (let attempt = 0; attempt < this.config.maxRetries; attempt++) {
      try {
        const res = await fetch(`${this.config.baseUrl}${path}`, {
          method,
          headers: this.getHeaders(),
          body: body ? JSON.stringify(body) : undefined,
          signal: AbortSignal.timeout(this.config.timeoutMs),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
        return await res.json() as T;
      } catch (e) {
        lastError = e as Error;
        if (attempt < this.config.maxRetries - 1) {
          await new Promise(r => setTimeout(r, Math.min(1000 * 2 ** attempt, 10000)));
        }
      }
    }
    this.stats.totalErrors++;
    throw lastError!;
  }

  private getHeaders(): Record<string, string> {
    const h: Record<string, string> = { 'Content-Type': 'application/json' };
    if (this.config.apiKey) h['Authorization'] = `Bearer ${this.config.apiKey}`;
    return h;
  }

  private getCacheKey(req: InferRequest): string {
    return `${req.prompt}:${req.maxTokens}:${req.temperature}`;
  }

  private updateAvgLatency(ms: number) {
    const n = this.stats.totalRequests;
    this.stats.avgLatencyMs = ((this.stats.avgLatencyMs * (n - 1)) + ms) / n;
  }
}
