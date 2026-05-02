/**
 * @omni-domain Interface Layer (MarkLLM)
 * @omni-source various/markllm
 * @omni-description MarkLLM Dashboard mimicking watermarking metrics UI.
 * @omni-requirement zero-mock, monadic-error
 */

export class OmniResult<T> {
    constructor(public readonly ok: boolean, public readonly value: T | null, public readonly err: Error | null) {}
    static ok<T>(v: T) { return new OmniResult<T>(true, v, null); }
    static err<T>(e: Error) { return new OmniResult<T>(false, null, e); }
}

export interface WatermarkMetrics {
    modelId: string;
    detectionRate: number;
    falsePositiveRate: number;
    latencyMs: number;
}

export class MarkLLMDashboard {
    private metricsCache: Map<string, WatermarkMetrics> = new Map();

    public updateMetrics(metrics: WatermarkMetrics): OmniResult<boolean> {
        if (!metrics.modelId) {
            return OmniResult.err(new Error("Model ID is required"));
        }
        if (metrics.detectionRate < 0 || metrics.detectionRate > 1) {
            return OmniResult.err(new Error("Detection rate must be between 0 and 1"));
        }

        this.metricsCache.set(metrics.modelId, metrics);
        return OmniResult.ok(true);
    }

    public renderDashboardHtml(): OmniResult<string> {
        if (this.metricsCache.size === 0) {
            return OmniResult.err(new Error("No data to render"));
        }

        let html = `<div class="markllm-dashboard">\n`;
        html += `  <h2>Watermarking Performance</h2>\n`;
        html += `  <table border="1">\n`;
        html += `    <tr><th>Model</th><th>Detection Rate</th><th>FPR</th><th>Latency</th></tr>\n`;
        
        for (const [modelId, data] of this.metricsCache.entries()) {
            html += `    <tr>\n`;
            html += `      <td>${modelId}</td>\n`;
            html += `      <td>${(data.detectionRate * 100).toFixed(2)}%</td>\n`;
            html += `      <td>${(data.falsePositiveRate * 100).toFixed(2)}%</td>\n`;
            html += `      <td>${data.latencyMs}ms</td>\n`;
            html += `    </tr>\n`;
        }
        html += `  </table>\n</div>`;
        
        return OmniResult.ok(html);
    }
}
