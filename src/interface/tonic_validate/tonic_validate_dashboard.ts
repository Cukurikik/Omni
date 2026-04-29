import { OmniResult, OmniError } from "@omni-bridge/core";

export interface TonicMetricData {
    mean: number;
    lowerBound: number;
    upperBound: number;
    variance: number;
}

export class TonicDashboardRenderer {
    private readonly MAX_CHARTS = 10;
    private currentCharts = 0;
    
    public renderMetricChart(metricName: string, data: TonicMetricData): OmniResult<string, OmniError> {
        if (this.currentCharts >= this.MAX_CHARTS) {
            return { ok: false, error: { code: "OMNI_UI_LIMIT", message: "Max charts rendered on screen" } };
        }
        
        if (data.mean < 0 || data.mean > 1) {
             return { ok: false, error: { code: "OMNI_DATA_ERR", message: "Metric mean out of bounds [0, 1]" } };
        }
        
        this.currentCharts++;
        
        // Return pure HTML template without external dependencies for safety
        const htmlTemplate = `
            <div class="tonic-chart-card">
                <h3>Metric: ${metricName}</h3>
                <div class="stats">
                    <span>Mean: ${data.mean.toFixed(4)}</span>
                    <span>95% CI: [${data.lowerBound.toFixed(4)}, ${data.upperBound.toFixed(4)}]</span>
                    <span>Variance: ${data.variance.toFixed(6)}</span>
                </div>
            </div>
        `;
        
        return { ok: true, payload: htmlTemplate };
    }
    
    public resetRenderer(): void {
        this.currentCharts = 0;
    }
}
