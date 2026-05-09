/**
 * moe_dashboard_api.ts — MoE Model Dashboard API Client
 * Layer: UI / Interface — MoE Monitoring
 *
 * TypeScript API client for the MoE serving gateway. Provides
 * type-safe methods for inference, expert monitoring, load balance
 * visualization, and shard health tracking.
 */

export interface MoEInferenceRequest {
  request_id: string;
  input_ids: number[];
  max_tokens: number;
  top_k?: number;
  top_p?: number;
  temperature?: number;
  stream?: boolean;
}

export interface MoEInferenceResponse {
  request_id: string;
  output_ids: number[];
  expert_utilization: number[];
  latency_ms: number;
  tokens_per_sec: number;
}

export interface ExpertShardInfo {
  shard_id: number;
  expert_range: [number, number];
  host: string;
  port: number;
  is_healthy: boolean;
  load_factor: number;
}

export interface GatewayHealth {
  status: string;
  healthy_shards: number;
  total_shards: number;
  active_requests: number;
}

export interface GatewayMetrics {
  total_requests: number;
  total_tokens: number;
  avg_latency_ms: number;
  error_count: number;
}

export interface ExpertUsageSnapshot {
  timestamp: number;
  expert_utilization: number[];
  load_balance_score: number;
  router_entropy: number;
}

export type ConnectionStatus = "connected" | "disconnected" | "reconnecting";

/** Result type for monadic error handling (no try/catch). */
export type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

function ok<T>(value: T): Result<T> {
  return { ok: true, value };
}

function err<T>(error: Error): Result<T> {
  return { ok: false, error };
}

/**
 * MoE Dashboard API Client.
 *
 * Provides type-safe, monadic access to the MoE serving gateway
 * for inference requests, monitoring, and management.
 */
export class MoEDashboardAPI {
  private baseUrl: string;
  private connectionStatus: ConnectionStatus = "disconnected";
  private metricsHistory: ExpertUsageSnapshot[] = [];
  private maxHistorySize: number = 1000;
  private pollingInterval: number | null = null;

  constructor(baseUrl: string = "http://localhost:8080") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  /** Run inference on the MoE model. */
  async infer(request: MoEInferenceRequest): Promise<Result<MoEInferenceResponse>> {
    const response = await this.fetchJson<MoEInferenceResponse>(
      "/v1/inference",
      { method: "POST", body: JSON.stringify(request) }
    );

    if (response.ok) {
      this.recordUsageSnapshot(response.value.expert_utilization);
    }
    return response;
  }

  /** Check gateway health. */
  async getHealth(): Promise<Result<GatewayHealth>> {
    return this.fetchJson<GatewayHealth>("/v1/health");
  }

  /** Get serving metrics. */
  async getMetrics(): Promise<Result<GatewayMetrics>> {
    return this.fetchJson<GatewayMetrics>("/v1/metrics");
  }

  /** Get shard information. */
  async getShards(): Promise<Result<ExpertShardInfo[]>> {
    return this.fetchJson<ExpertShardInfo[]>("/v1/shards");
  }

  /** Get cached metrics history for visualization. */
  getMetricsHistory(): ExpertUsageSnapshot[] {
    return [...this.metricsHistory];
  }

  /** Start periodic metrics polling. */
  startPolling(intervalMs: number = 5000): void {
    this.stopPolling();
    this.pollingInterval = window.setInterval(async () => {
      const health = await this.getHealth();
      if (health.ok) {
        this.connectionStatus = "connected";
      } else {
        this.connectionStatus = "reconnecting";
      }
    }, intervalMs) as unknown as number;
    this.connectionStatus = "connected";
  }

  /** Stop periodic polling. */
  stopPolling(): void {
    if (this.pollingInterval !== null) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
  }

  /** Get current connection status. */
  getConnectionStatus(): ConnectionStatus {
    return this.connectionStatus;
  }

  /** Compute load balance score from expert utilization. */
  computeLoadBalanceScore(utilization: number[]): number {
    if (utilization.length === 0) return 0;
    const mean = utilization.reduce((a, b) => a + b, 0) / utilization.length;
    const variance = utilization.reduce((sum, u) => sum + (u - mean) ** 2, 0) / utilization.length;
    const cv = Math.sqrt(variance) / (mean + 1e-8);
    // Score: 1.0 = perfectly balanced, 0.0 = totally imbalanced
    return Math.max(0, 1.0 - cv);
  }

  /** Compute routing entropy from utilization. */
  computeRouterEntropy(utilization: number[]): number {
    const total = utilization.reduce((a, b) => a + b, 0);
    if (total === 0) return 0;
    let entropy = 0;
    for (const u of utilization) {
      const p = u / total;
      if (p > 0) entropy -= p * Math.log2(p);
    }
    const maxEntropy = Math.log2(utilization.length);
    return maxEntropy > 0 ? entropy / maxEntropy : 0;
  }

  /** Record a usage snapshot for historical tracking. */
  private recordUsageSnapshot(utilization: number[]): void {
    const snapshot: ExpertUsageSnapshot = {
      timestamp: Date.now(),
      expert_utilization: utilization,
      load_balance_score: this.computeLoadBalanceScore(utilization),
      router_entropy: this.computeRouterEntropy(utilization),
    };
    this.metricsHistory.push(snapshot);
    if (this.metricsHistory.length > this.maxHistorySize) {
      this.metricsHistory.shift();
    }
  }

  /** Generic fetch wrapper with monadic error handling. */
  private async fetchJson<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<Result<T>> {
    const url = `${this.baseUrl}${path}`;
    const defaultHeaders: Record<string, string> = {
      "Content-Type": "application/json",
      Accept: "application/json",
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers: { ...defaultHeaders, ...(options.headers as Record<string, string>) },
      });

      if (!response.ok) {
        const body = await response.text();
        return err(new Error(`HTTP ${response.status}: ${body}`));
      }

      const data: T = await response.json();
      return ok(data);
    } catch (e) {
      this.connectionStatus = "disconnected";
      return err(e instanceof Error ? e : new Error(String(e)));
    }
  }
}

/** Format expert utilization as a text bar chart. */
export function formatExpertUtilization(utilization: number[]): string {
  const maxBar = 40;
  const maxVal = Math.max(...utilization, 0.001);
  return utilization
    .map((u, i) => {
      const barLen = Math.round((u / maxVal) * maxBar);
      const bar = "█".repeat(barLen) + "░".repeat(maxBar - barLen);
      return `Expert ${String(i).padStart(3)}: ${bar} ${(u * 100).toFixed(1)}%`;
    })
    .join("\n");
}
