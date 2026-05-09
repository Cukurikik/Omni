// OMNI Interface Layer — TypeScript Full-Stack Inference Client SDK
// Type-safe API client for OMNI transformer inference endpoints.

interface InferenceRequest {
  prompt: string;
  maxTokens?: number;
  temperature?: number;
  topP?: number;
  topK?: number;
  stream?: boolean;
  stopSequences?: string[];
}

interface InferenceResponse {
  requestId: string;
  generatedText: string;
  tokensGenerated: number;
  latencyMs: number;
  finishReason: 'stop' | 'max_tokens' | 'error';
  usage: { promptTokens: number; completionTokens: number; totalTokens: number };
}

interface StreamChunk {
  delta: string;
  tokenIndex: number;
  finishReason: string | null;
}

interface ModelInfo {
  id: string;
  name: string;
  parameters: number;
  maxContext: number;
  supportedTasks: string[];
}

type EventCallback = (chunk: StreamChunk) => void;

class OmniInferenceClient {
  private baseUrl: string;
  private apiKey: string;
  private timeout: number;
  private retryCount: number;

  constructor(config: { baseUrl: string; apiKey: string; timeout?: number; retries?: number }) {
    this.baseUrl = config.baseUrl.replace(/\/$/, '');
    this.apiKey = config.apiKey;
    this.timeout = config.timeout ?? 30000;
    this.retryCount = config.retries ?? 3;
  }

  private async fetchWithRetry(url: string, options: RequestInit, retries: number = this.retryCount): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`,
          ...options.headers,
        },
      });

      if (!response.ok && retries > 0 && response.status >= 500) {
        await new Promise(r => setTimeout(r, 1000 * (this.retryCount - retries + 1)));
        return this.fetchWithRetry(url, options, retries - 1);
      }

      return response;
    } catch (err) {
      if (retries > 0) {
        await new Promise(r => setTimeout(r, 1000));
        return this.fetchWithRetry(url, options, retries - 1);
      }
      throw err;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  async infer(request: InferenceRequest): Promise<InferenceResponse> {
    const response = await this.fetchWithRetry(`${this.baseUrl}/api/v1/infer`, {
      method: 'POST',
      body: JSON.stringify({
        prompt: request.prompt,
        max_tokens: request.maxTokens ?? 256,
        temperature: request.temperature ?? 0.7,
        top_p: request.topP ?? 0.9,
        top_k: request.topK ?? 50,
        stop_sequences: request.stopSequences ?? [],
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Inference failed (${response.status}): ${error}`);
    }

    return response.json();
  }

  async *stream(request: InferenceRequest): AsyncGenerator<StreamChunk> {
    const response = await this.fetchWithRetry(`${this.baseUrl}/api/v1/stream`, {
      method: 'POST',
      body: JSON.stringify({ ...request, stream: true }),
    });

    if (!response.ok || !response.body) {
      throw new Error(`Stream failed: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() ?? '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6).trim();
          if (data === '[DONE]') return;
          try {
            yield JSON.parse(data) as StreamChunk;
          } catch { /* skip malformed */ }
        }
      }
    }
  }

  async listModels(): Promise<ModelInfo[]> {
    const response = await this.fetchWithRetry(`${this.baseUrl}/api/v1/models`, { method: 'GET' });
    return response.json();
  }

  async health(): Promise<{ status: string; activeRequests: number }> {
    const response = await this.fetchWithRetry(`${this.baseUrl}/api/v1/health`, { method: 'GET' });
    return response.json();
  }
}

// Embedding client for RAG
class OmniEmbeddingClient {
  private client: OmniInferenceClient;

  constructor(config: { baseUrl: string; apiKey: string }) {
    this.client = new OmniInferenceClient(config);
  }

  async embed(texts: string[]): Promise<number[][]> {
    const response = await fetch(`${(this.client as any).baseUrl}/api/v1/embed`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${(this.client as any).apiKey}` },
      body: JSON.stringify({ texts }),
    });
    const data = await response.json();
    return data.embeddings;
  }

  cosineSimilarity(a: number[], b: number[]): number {
    let dot = 0, normA = 0, normB = 0;
    for (let i = 0; i < a.length; i++) {
      dot += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }
    return dot / (Math.sqrt(normA) * Math.sqrt(normB));
  }
}

export { OmniInferenceClient, OmniEmbeddingClient };
export type { InferenceRequest, InferenceResponse, StreamChunk, ModelInfo };
