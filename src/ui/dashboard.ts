// ===========================================================================
// OMNI UI LAYER — DASHBOARD ANALYTICS COMPONENT
// ===========================================================================
// Domain Layer   : UI (Static typing, contract-first API)
// Language        : TypeScript
// Function        : Dashboard analytics component with real-time metric
//                   aggregation, chart data formatting, widget registry,
//                   time-window filtering, and responsive layout management
// ===========================================================================

// ---- Types ----------------------------------------------------------------

type TimeWindow = '1h' | '6h' | '24h' | '7d' | '30d' | 'custom';
type WidgetType = 'counter' | 'lineChart' | 'barChart' | 'pieChart' | 'table' | 'heatmap' | 'gauge';
type MetricAggregation = 'sum' | 'avg' | 'min' | 'max' | 'count' | 'p50' | 'p95' | 'p99';

interface DataPoint {
    timestamp: number;
    value: number;
    label?: string;
}

interface MetricSeries {
    name: string;
    unit: string;        // "ms", "req/s", "%", "bytes", etc.
    dataPoints: DataPoint[];
    aggregation: MetricAggregation;
}

interface WidgetConfig {
    id: string;
    title: string;
    type: WidgetType;
    metrics: string[];    // metric series names
    position: { row: number; col: number; width: number; height: number };
    refreshIntervalMs: number;
    thresholds?: { warning: number; critical: number };
}

interface DashboardLayout {
    name: string;
    columns: number;
    widgets: WidgetConfig[];
}

// ---- Metric Aggregators ---------------------------------------------------

function aggregate(points: DataPoint[], method: MetricAggregation): number {
    if (points.length === 0) return 0;
    const values = points.map(p => p.value).sort((a, b) => a - b);

    switch (method) {
        case 'sum':   return values.reduce((a, b) => a + b, 0);
        case 'avg':   return values.reduce((a, b) => a + b, 0) / values.length;
        case 'min':   return values[0];
        case 'max':   return values[values.length - 1];
        case 'count': return values.length;
        case 'p50':   return values[Math.floor(values.length * 0.5)];
        case 'p95':   return values[Math.floor(values.length * 0.95)];
        case 'p99':   return values[Math.floor(values.length * 0.99)];
    }
}

function filterByTimeWindow(points: DataPoint[], window: TimeWindow): DataPoint[] {
    const now = Date.now();
    const windowMs: Record<string, number> = {
        '1h': 3600000,
        '6h': 21600000,
        '24h': 86400000,
        '7d': 604800000,
        '30d': 2592000000,
    };
    const cutoff = now - (windowMs[window] || 86400000);
    return points.filter(p => p.timestamp >= cutoff);
}

// ---- Dashboard Engine -----------------------------------------------------

class DashboardEngine {
    private metrics: Map<string, MetricSeries> = new Map();
    private widgets: Map<string, WidgetConfig> = new Map();
    private layout: DashboardLayout;

    constructor(layoutName: string, columns: number = 12) {
        this.layout = { name: layoutName, columns, widgets: [] };
        console.log(`[DASHBOARD-OMNI-TS] Dashboard initialized: "${layoutName}" (${columns}-col grid)`);
    }

    // ---- Metric Management ------------------------------------------------

    registerMetric(series: MetricSeries): void {
        this.metrics.set(series.name, series);
        console.log(`[DASHBOARD-OMNI-TS] Metric registered: ${series.name} (${series.unit}, ${series.aggregation})`);
    }

    pushDataPoint(metricName: string, value: number, timestamp?: number): void {
        const series = this.metrics.get(metricName);
        if (!series) return;
        series.dataPoints.push({
            timestamp: timestamp || Date.now(),
            value,
        });
    }

    getMetricValue(metricName: string, window: TimeWindow): number {
        const series = this.metrics.get(metricName);
        if (!series) return 0;
        const filtered = filterByTimeWindow(series.dataPoints, window);
        return aggregate(filtered, series.aggregation);
    }

    getMetricHistory(metricName: string, window: TimeWindow, bucketCount: number = 60): DataPoint[] {
        const series = this.metrics.get(metricName);
        if (!series) return [];
        const filtered = filterByTimeWindow(series.dataPoints, window);
        if (filtered.length === 0) return [];

        // Bucket into equal time intervals
        const minTs = filtered[0].timestamp;
        const maxTs = filtered[filtered.length - 1].timestamp;
        const bucketWidth = (maxTs - minTs) / bucketCount;

        const buckets: DataPoint[] = [];
        for (let i = 0; i < bucketCount; i++) {
            const start = minTs + i * bucketWidth;
            const end = start + bucketWidth;
            const inBucket = filtered.filter(p => p.timestamp >= start && p.timestamp < end);
            buckets.push({
                timestamp: start,
                value: inBucket.length > 0
                    ? aggregate(inBucket, series.aggregation)
                    : 0,
            });
        }

        return buckets;
    }

    // ---- Widget Management ------------------------------------------------

    addWidget(config: WidgetConfig): void {
        this.widgets.set(config.id, config);
        this.layout.widgets.push(config);
        console.log(`[DASHBOARD-OMNI-TS] Widget added: ${config.id} (${config.type})`);
    }

    removeWidget(widgetId: string): boolean {
        const removed = this.widgets.delete(widgetId);
        this.layout.widgets = this.layout.widgets.filter(w => w.id !== widgetId);
        return removed;
    }

    // ---- Render Data (for frontend consumption) ---------------------------

    renderWidget(widgetId: string, window: TimeWindow): object | null {
        const config = this.widgets.get(widgetId);
        if (!config) return null;

        const data: Record<string, any> = {
            id: config.id,
            title: config.title,
            type: config.type,
        };

        switch (config.type) {
            case 'counter':
                data['value'] = this.getMetricValue(config.metrics[0], window);
                data['unit'] = this.metrics.get(config.metrics[0])?.unit || '';
                break;

            case 'gauge':
                data['value'] = this.getMetricValue(config.metrics[0], window);
                data['thresholds'] = config.thresholds;
                break;

            case 'lineChart':
            case 'barChart':
                data['series'] = config.metrics.map(m => ({
                    name: m,
                    data: this.getMetricHistory(m, window),
                }));
                break;

            case 'table':
                data['rows'] = config.metrics.map(m => ({
                    metric: m,
                    value: this.getMetricValue(m, window),
                    unit: this.metrics.get(m)?.unit || '',
                }));
                break;
        }

        return data;
    }

    renderAll(window: TimeWindow): object[] {
        return this.layout.widgets
            .map(w => this.renderWidget(w.id, window))
            .filter(Boolean) as object[];
    }

    getLayout(): DashboardLayout { return this.layout; }
}

export { DashboardEngine, MetricSeries, WidgetConfig, DashboardLayout };
