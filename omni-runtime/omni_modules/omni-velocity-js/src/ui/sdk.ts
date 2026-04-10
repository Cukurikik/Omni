// omni-velocity-js â€” Type-Safe TypeScript SDK

export interface ClientConfig { endpoint: string; apiKey?: string; timeout?: number; retries?: number; }
export interface RequestOptions { method: 'GET' | 'POST' | 'PUT' | 'DELETE'; path: string; body?: unknown; headers?: Record<string, string>; }
export interface ApiResponse<T> { success: boolean; data?: T; error?: string; status: number; latency: number; }

export class TypeSafeClient {
  private config: ClientConfig;
  constructor(config: ClientConfig) { this.config = { timeout: 30000, retries: 3, ...config }; }

  async request<T>(opts: RequestOptions): Promise<ApiResponse<T>> {
    const start = Date.now();
    try {
      const url = this.config.endpoint + opts.path;
      const headers: Record<string, string> = { 'Content-Type': 'application/json', ...opts.headers };
      if (this.config.apiKey) headers['Authorization'] = 'Bearer ' + this.config.apiKey;
      const res = await fetch(url, { method: opts.method, headers, body: opts.body ? JSON.stringify(opts.body) : undefined });
      const data = await res.json() as T;
      return { success: res.ok, data, status: res.status, latency: Date.now() - start };
    } catch (e) {
      return { success: false, error: (e as Error).message, status: 0, latency: Date.now() - start };
    }
  }

  async get<T>(path: string): Promise<ApiResponse<T>> { return this.request({ method: 'GET', path }); }
  async post<T>(path: string, body: unknown): Promise<ApiResponse<T>> { return this.request({ method: 'POST', path, body }); }
  async put<T>(path: string, body: unknown): Promise<ApiResponse<T>> { return this.request({ method: 'PUT', path, body }); }
  async delete<T>(path: string): Promise<ApiResponse<T>> { return this.request({ method: 'DELETE', path }); }
}