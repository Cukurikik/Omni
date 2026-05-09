// @omni-layer Interface | @omni-source TheophileBlard/french-sentiment | @omni-lang TypeScript
// @omni-description Sentiment analysis dashboard: multilingual sentiment gauge,
// trend chart, language breakdown, and brand monitoring widgets.

interface SentimentResult {
  text: string;
  label: string;
  confidence: number;
  language: string;
}

interface SentimentTrend {
  period: string;
  avgSentiment: number;
  totalAnalyses: number;
}

class SentimentDashboard {
  private container: HTMLElement;
  private results: SentimentResult[] = [];
  private trends: SentimentTrend[] = [];

  constructor(containerId: string) {
    const el = document.getElementById(containerId);
    if (!el) throw new Error(`Container ${containerId} not found`);
    this.container = el;
  }

  setResults(results: SentimentResult[]): void {
    this.results = results;
    this.render();
  }

  setTrends(trends: SentimentTrend[]): void {
    this.trends = trends;
    this.render();
  }

  private render(): void {
    const dist = this.getDistribution();
    const langBreakdown = this.getLanguageBreakdown();

    this.container.innerHTML = `
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
        ${this.renderSentimentGauge()}
        ${this.renderDistributionBars(dist)}
      </div>
      <div style="display:grid;grid-template-columns:1fr 260px;gap:16px">
        <div style="background:#1a1f36;border-radius:12px;padding:20px">
          <h3 style="color:#93c5fd;margin-bottom:12px">📋 Recent Analyses</h3>
          ${this.results.slice(-10).reverse().map(r => this.renderResultRow(r)).join('')}
        </div>
        <div style="display:flex;flex-direction:column;gap:12px">
          <div style="background:#1a1f36;border-radius:10px;padding:14px">
            <h4 style="color:#93c5fd;font-size:0.85rem;margin-bottom:10px">🌐 Languages</h4>
            ${Object.entries(langBreakdown).map(([l, n]) => `
              <div style="display:flex;justify-content:space-between;font-size:0.8rem;padding:3px 0">
                <span style="color:#94a3b8">${l}</span>
                <span style="color:#60a5fa;font-weight:600">${n}</span>
              </div>`).join('')}
          </div>
          <div style="background:#1a1f36;border-radius:8px;padding:12px;border-left:3px solid #60a5fa">
            <div style="font-size:1.2rem;font-weight:700;color:#60a5fa">${this.results.length}</div>
            <div style="font-size:0.7rem;color:#64748b">Total Analyses</div>
          </div>
        </div>
      </div>`;
  }

  private renderSentimentGauge(): string {
    const avgConf = this.results.length ? this.results.reduce((s, r) => s + r.confidence, 0) / this.results.length : 0;
    return `<div style="background:#1a1f36;border-radius:12px;padding:20px;text-align:center">
      <h3 style="color:#93c5fd;margin-bottom:16px">🎯 Avg Confidence</h3>
      <div style="font-size:2.5rem;font-weight:700;color:#60a5fa">${(avgConf*100).toFixed(1)}%</div>
    </div>`;
  }

  private renderDistributionBars(dist: Record<string, number>): string {
    const max = Math.max(...Object.values(dist), 1);
    const colors: Record<string, string> = {
      very_negative: '#dc2626', negative: '#ef4444', neutral: '#64748b', positive: '#10b981', very_positive: '#059669'
    };
    return `<div style="background:#1a1f36;border-radius:12px;padding:20px">
      <h3 style="color:#93c5fd;margin-bottom:16px">📊 Distribution</h3>
      ${Object.entries(dist).map(([label, count]) => `
        <div style="margin-bottom:6px">
          <div style="display:flex;justify-content:space-between;font-size:0.75rem;margin-bottom:2px">
            <span style="color:#94a3b8">${label.replace('_',' ')}</span><span style="color:${colors[label] || '#64748b'}">${count}</span>
          </div>
          <div style="background:#0a0e17;border-radius:4px;height:10px;overflow:hidden">
            <div style="width:${(count/max)*100}%;height:100%;background:${colors[label] || '#64748b'};border-radius:4px"></div>
          </div>
        </div>`).join('')}
    </div>`;
  }

  private renderResultRow(r: SentimentResult): string {
    const colors: Record<string, string> = {
      very_negative: '#dc2626', negative: '#ef4444', neutral: '#64748b', positive: '#10b981', very_positive: '#059669'
    };
    return `<div style="display:grid;grid-template-columns:1fr 100px 60px 50px;gap:8px;padding:6px 0;border-bottom:1px solid #1e293b20;font-size:0.8rem">
      <span style="color:#94a3b8;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${r.text}</span>
      <span style="color:${colors[r.label] || '#64748b'}">${r.label.replace('_',' ')}</span>
      <span style="color:#60a5fa">${(r.confidence*100).toFixed(0)}%</span>
      <span style="color:#64748b">${r.language}</span>
    </div>`;
  }

  private getDistribution(): Record<string, number> {
    const d: Record<string, number> = { very_negative: 0, negative: 0, neutral: 0, positive: 0, very_positive: 0 };
    for (const r of this.results) d[r.label] = (d[r.label] || 0) + 1;
    return d;
  }

  private getLanguageBreakdown(): Record<string, number> {
    const b: Record<string, number> = {};
    for (const r of this.results) b[r.language] = (b[r.language] || 0) + 1;
    return b;
  }
}

export { SentimentDashboard, SentimentResult, SentimentTrend };
