// @omni-layer Interface | @omni-source lucidrains/ETSformer-pytorch | @omni-lang TypeScript
// @omni-description Time series forecast dashboard: interactive chart with
// decomposition view, model comparison, and forecast confidence bands.

interface ForecastData {
  timestamp: string;
  actual: number;
  predicted: number;
  level: number;
  trend: number;
  seasonal: number;
  lower_bound: number;
  upper_bound: number;
}

interface ModelMetrics {
  name: string;
  mse: number;
  mae: number;
  mape: number;
}

class ETSFormerDashboard {
  private container: HTMLElement;
  private data: ForecastData[] = [];
  private models: ModelMetrics[] = [];

  constructor(containerId: string) {
    const el = document.getElementById(containerId);
    if (!el) throw new Error(`Container ${containerId} not found`);
    this.container = el;
  }

  loadData(data: ForecastData[]): void {
    this.data = data;
    this.render();
  }

  loadModels(models: ModelMetrics[]): void {
    this.models = models;
    this.renderModelComparison();
  }

  private render(): void {
    this.container.innerHTML = `
      <div style="display:grid;grid-template-columns:1fr 300px;gap:16px">
        <div id="forecastChart" style="background:#1a1f36;border-radius:12px;padding:20px;min-height:300px">
          <h3 style="color:#93c5fd;margin-bottom:12px">📈 Forecast</h3>
          ${this.renderChart()}
        </div>
        <div style="display:flex;flex-direction:column;gap:12px">
          ${this.renderMetricCards()}
        </div>
      </div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px">
        ${this.renderDecomposition()}
      </div>`;
  }

  private renderChart(): string {
    if (!this.data.length) return '<p style="color:#64748b">No data loaded</p>';
    const maxVal = Math.max(...this.data.map(d => Math.max(d.actual, d.predicted, d.upper_bound)));
    const height = 200;
    const width = 600;
    const bars = this.data.map((d, i) => {
      const x = (i / this.data.length) * width;
      const hA = (d.actual / maxVal) * height;
      const hP = (d.predicted / maxVal) * height;
      return `<rect x="${x}" y="${height-hA}" width="3" height="${hA}" fill="#60a5fa" opacity="0.7"/>
              <rect x="${x+4}" y="${height-hP}" width="3" height="${hP}" fill="#a78bfa" opacity="0.7"/>`;
    }).join('');
    return `<svg width="${width}" height="${height}" style="width:100%">${bars}</svg>
            <div style="display:flex;gap:16px;margin-top:8px;font-size:0.8rem">
              <span style="color:#60a5fa">● Actual</span>
              <span style="color:#a78bfa">● Predicted</span>
            </div>`;
  }

  private renderMetricCards(): string {
    if (!this.data.length) return '';
    const mse = this.data.reduce((s, d) => s + (d.actual - d.predicted) ** 2, 0) / this.data.length;
    const mae = this.data.reduce((s, d) => s + Math.abs(d.actual - d.predicted), 0) / this.data.length;
    const last = this.data[this.data.length - 1];
    return [
      { label: 'MSE', value: mse.toFixed(4), color: '#60a5fa' },
      { label: 'MAE', value: mae.toFixed(4), color: '#22d3ee' },
      { label: 'Last Level', value: last.level.toFixed(2), color: '#a78bfa' },
      { label: 'Last Trend', value: last.trend.toFixed(4), color: '#f59e0b' },
    ].map(m => `<div style="background:#1a1f36;border-radius:8px;padding:14px;border-left:3px solid ${m.color}">
      <div style="font-size:1.3rem;font-weight:700;color:${m.color}">${m.value}</div>
      <div style="font-size:0.75rem;color:#64748b">${m.label}</div></div>`).join('');
  }

  private renderDecomposition(): string {
    return ['Level', 'Trend', 'Seasonal'].map(comp => {
      const key = comp.toLowerCase() as keyof ForecastData;
      return `<div style="background:#1a1f36;border-radius:8px;padding:16px">
        <h4 style="color:#93c5fd;margin-bottom:8px">${comp}</h4>
        <div style="font-size:0.85rem;color:#94a3b8">${this.data.length} points</div></div>`;
    }).join('');
  }

  private renderModelComparison(): void {
    if (!this.models.length) return;
    const html = this.models.map((m, i) => `
      <tr style="border-bottom:1px solid #1e293b">
        <td style="padding:8px;color:${i===0?'#60a5fa':'#94a3b8'}">${i+1}. ${m.name}</td>
        <td style="padding:8px">${m.mse.toFixed(4)}</td>
        <td style="padding:8px">${m.mae.toFixed(4)}</td>
        <td style="padding:8px">${m.mape.toFixed(2)}%</td>
      </tr>`).join('');
    const table = document.createElement('div');
    table.innerHTML = `<div style="background:#1a1f36;border-radius:12px;padding:20px;margin-top:16px">
      <h3 style="color:#93c5fd;margin-bottom:12px">🏆 Model Comparison</h3>
      <table style="width:100%;border-collapse:collapse;font-size:0.85rem">
        <thead><tr style="color:#64748b;border-bottom:1px solid #334155">
          <th style="text-align:left;padding:8px">Model</th><th>MSE</th><th>MAE</th><th>MAPE</th></tr></thead>
        <tbody>${html}</tbody></table></div>`;
    this.container.appendChild(table);
  }
}

export { ETSFormerDashboard, ForecastData, ModelMetrics };
