// OMNI Prometheus TSDB Ingest Engine — Interface Layer (TypeScript)
// Absorbing prometheus/prometheus time series structural boundaries
// Label cardinality constraint enforcement

export type PromResult<T> = {
    ok: boolean;
    value: T | null;
    error: string;
};

export interface PromSample {
    timestamp_ms: number;
    value: number;
}

export interface PromTimeSeries {
    labels: Record<string, string>; // Canonical representation via JSON stringification hash
    samples: PromSample[];
}

export class OmniPrometheusTsdbIngest {
    private ingestion_runs: number = 0;
    private max_cardinality: number;
    private tsdb: Map<string, PromTimeSeries> = new Map();

    constructor(max_cardinality: number = 1000) {
        this.max_cardinality = max_cardinality;
    }

    private compute_label_hash(labels: Record<string, string>): string {
        const sortedKeys = Object.keys(labels).sort();
        let hashData = "";
        for (const k of sortedKeys) {
            hashData += `${k}="${labels[k]}",`;
        }
        return `{${hashData.slice(0, -1)}}`; // E.g. {instance="localhost",job="api"}
    }

    public ingest_tensor(labels: Record<string, string>, timestamp: number, value: number): PromResult<boolean> {
        try {
            if (!labels || Object.keys(labels).length === 0) {
                return { ok: false, value: false, error: "Missing metric name or labels." };
            }

            const hash = this.compute_label_hash(labels);

            if (!this.tsdb.has(hash)) {
                if (this.tsdb.size >= this.max_cardinality) {
                    return { ok: false, value: false, error: "PrometheusError: High cardinality bounds exceeded." };
                }
                this.tsdb.set(hash, { labels, samples: [] });
            }

            const series = this.tsdb.get(hash)!;
            
            // TSDB append-only block assurance
            if (series.samples.length > 0 && series.samples[series.samples.length - 1].timestamp_ms > timestamp) {
                 return { ok: false, value: false, error: "PrometheusError: Out of order sample timestamp boundary." };
            }

            series.samples.push({ timestamp_ms: timestamp, value });
            this.ingestion_runs++;

            return { ok: true, value: true, error: "" };
        } catch (e: any) {
             return { ok: false, value: false, error: `Panic: ${e.message}` };
        }
    }

    public query_range(labels_subset: Record<string, string>, start_ms: number, end_ms: number): PromResult<PromSample[]> {
        // Mock query mathematical scan map
        try {
            const results: PromSample[] = [];
            const hashKeys = Array.from(this.tsdb.keys());

            for (const hash of hashKeys) {
                const series = this.tsdb.get(hash)!;
                let match = true;
                for (const pk in labels_subset) {
                    if (series.labels[pk] !== labels_subset[pk]) {
                        match = false;
                        break;
                    }
                }
                
                if (match) {
                    for (const s of series.samples) {
                        if (s.timestamp_ms >= start_ms && s.timestamp_ms <= end_ms) {
                            results.push(s);
                        }
                    }
                }
            }
            return { ok: true, value: results, error: "" };
        } catch (e: any) {
            return { ok: false, value: null, error: `Query Panic: ${e.message}` };
        }
    }

    public diagnostics(): Record<string, any> {
        return {
            engine: "OmniPrometheusTsdbIngest",
            active_series: this.tsdb.size,
            samples_ingested: this.ingestion_runs,
            status: "Operational"
        };
    }
}
