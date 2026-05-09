// @omni-layer Business | @omni-source karpathy/nanoGPT | @omni-lang TypeScript
// @omni-description Training dashboard API service: metrics collection, loss
// tracking, and experiment comparison for NanoGPT runs.

interface TrainingMetrics {
  step: number;
  train_loss: number;
  val_loss: number;
  learning_rate: number;
  grad_norm: number;
  tokens_per_sec: number;
  timestamp: string;
}

interface Experiment {
  id: string;
  name: string;
  config: Record<string, any>;
  metrics: TrainingMetrics[];
  status: 'running' | 'completed' | 'failed';
  created_at: string;
}

class TrainingDashboardService {
  private experiments: Map<string, Experiment> = new Map();

  createExperiment(id: string, name: string, config: Record<string, any>): { data?: Experiment; error?: string } {
    if (this.experiments.has(id)) return { error: `Experiment ${id} exists` };
    const exp: Experiment = { id, name, config, metrics: [], status: 'running', created_at: new Date().toISOString() };
    this.experiments.set(id, exp);
    return { data: exp };
  }

  logMetrics(expId: string, metrics: TrainingMetrics): { data?: any; error?: string } {
    const exp = this.experiments.get(expId);
    if (!exp) return { error: 'Experiment not found' };
    exp.metrics.push(metrics);
    return { data: { step: metrics.step, total_steps: exp.metrics.length } };
  }

  getExperimentSummary(expId: string): { data?: any; error?: string } {
    const exp = this.experiments.get(expId);
    if (!exp) return { error: 'Not found' };
    const m = exp.metrics;
    if (m.length === 0) return { data: { id: expId, status: exp.status, n_steps: 0 } };
    const latest = m[m.length - 1];
    const bestVal = Math.min(...m.map(x => x.val_loss));
    return { data: {
      id: expId, name: exp.name, status: exp.status,
      n_steps: m.length, latest_loss: latest.train_loss,
      best_val_loss: bestVal, avg_throughput: m.reduce((s, x) => s + x.tokens_per_sec, 0) / m.length,
      config: exp.config
    }};
  }

  compareExperiments(ids: string[]): { data?: any; error?: string } {
    const results = ids.map(id => this.getExperimentSummary(id));
    const valid = results.filter(r => r.data).map(r => r.data);
    return { data: { comparisons: valid, n_experiments: valid.length } };
  }
}

export { TrainingDashboardService };
export type { TrainingMetrics, Experiment };
