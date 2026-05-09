// @omni-layer Interface | @omni-source md-experiments/elastic_transformers | @omni-lang TypeScript
// @omni-description Semantic search dashboard: hybrid search interface with
// dense/sparse score comparison, result ranking, and index analytics.

interface HybridResult {
  id: string;
  hybridScore: number;
  denseScore: number;
  bm25Score: number;
  preview: string;
}

interface IndexStats {
  totalDocs: number;
  avgDocLength: number;
  indexSizeBytes: number;
}

class SemanticSearchDashboard {
  private container: HTMLElement;
  private results: HybridResult[] = [];
  private indexStats: IndexStats | null = null;
  private alpha: number = 0.7;

  constructor(containerId: string) {
    const el = document.getElementById(containerId);
    if (!el) throw new Error(`Container ${containerId} not found`);
    this.container = el;
    this.render();
  }

  setResults(results: HybridResult[]): void {
    this.results = results;
    this.render();
  }

  setIndexStats(stats: IndexStats): void {
    this.indexStats = stats;
    this.render();
  }

  setAlpha(alpha: number): void {
    this.alpha = alpha;
    this.render();
  }

  private render(): void {
    this.container.innerHTML = `
      <div style="background:#1a1f36;border-radius:12px;padding:20px;margin-bottom:16px">
        <div style="display:flex;gap:12px;align-items:center">
          <h3 style="color:#93c5fd;margin-right:auto">🔗 Hybrid Search</h3>
          <label style="font-size:0.8rem;color:#94a3b8">Dense weight: <b style="color:#60a5fa">${this.alpha.toFixed(1)}</b></label>
        </div>
        <div style="display:flex;gap:8px;margin-top:12px">
          <input type="text" placeholder="Enter search query..." style="flex:1;padding:10px 14px;background:#0a0e17;border:1px solid #334155;border-radius:8px;color:#e2e8f0;font-size:0.9rem">
          <button style="padding:8px 16px;background:linear-gradient(135deg,#60a5fa,#a78bfa);border:none;border-radius:8px;color:white;font-weight:600;cursor:pointer">Search</button>
        </div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 240px;gap:16px">
        <div>${this.renderResults()}</div>
        <div style="display:flex;flex-direction:column;gap:12px">
          ${this.renderIndexCards()}
          <div style="background:#1a1f36;border-radius:10px;padding:14px">
            <h4 style="color:#93c5fd;font-size:0.85rem;margin-bottom:10px">⚖️ Score Comparison</h4>
            ${this.renderScoreComparison()}
          </div>
        </div>
      </div>`;
  }

  private renderResults(): string {
    if (!this.results.length) return '<div style="text-align:center;color:#64748b;padding:40px">No results yet</div>';
    return this.results.map((r, i) => {
      const maxScore = Math.max(...this.results.map(x => x.hybridScore), 0.01);
      const pct = (r.hybridScore / maxScore * 100).toFixed(0);
      return `<div style="background:#1a1f36;border-radius:10px;padding:14px;margin-bottom:8px">
        <div style="display:flex;justify-content:space-between;margin-bottom:6px">
          <span style="font-size:0.85rem;color:#93c5fd;font-weight:600">#${i+1} ${r.id}</span>
          <span style="font-size:0.75rem;color:#60a5fa">${r.hybridScore.toFixed(4)}</span>
        </div>
        <div style="background:#0a0e17;border-radius:4px;height:6px;overflow:hidden;margin-bottom:6px">
          <div style="width:${pct}%;height:100%;background:linear-gradient(90deg,#60a5fa,#a78bfa);border-radius:4px"></div>
        </div>
        <div style="font-size:0.8rem;color:#94a3b8">${r.preview}</div>
        <div style="display:flex;gap:12px;margin-top:6px;font-size:0.7rem">
          <span style="color:#60a5fa">Dense: ${r.denseScore.toFixed(3)}</span>
          <span style="color:#f59e0b">BM25: ${r.bm25Score.toFixed(3)}</span>
        </div>
      </div>`;
    }).join('');
  }

  private renderIndexCards(): string {
    if (!this.indexStats) return '';
    return [
      { label: 'Documents', value: `${this.indexStats.totalDocs}`, color: '#60a5fa' },
      { label: 'Avg Length', value: `${this.indexStats.avgDocLength.toFixed(0)}`, color: '#a78bfa' },
    ].map(c => `<div style="background:#1a1f36;border-radius:8px;padding:12px;border-left:3px solid ${c.color}">
      <div style="font-size:1.1rem;font-weight:700;color:${c.color}">${c.value}</div>
      <div style="font-size:0.7rem;color:#64748b">${c.label}</div>
    </div>`).join('');
  }

  private renderScoreComparison(): string {
    if (!this.results.length) return '<div style="font-size:0.8rem;color:#64748b">No data</div>';
    const avgDense = this.results.reduce((s, r) => s + r.denseScore, 0) / this.results.length;
    const avgBm25 = this.results.reduce((s, r) => s + r.bm25Score, 0) / this.results.length;
    return `<div style="font-size:0.8rem">
      <div style="display:flex;justify-content:space-between;padding:3px 0"><span style="color:#94a3b8">Avg Dense</span><span style="color:#60a5fa">${avgDense.toFixed(4)}</span></div>
      <div style="display:flex;justify-content:space-between;padding:3px 0"><span style="color:#94a3b8">Avg BM25</span><span style="color:#f59e0b">${avgBm25.toFixed(4)}</span></div>
      <div style="display:flex;justify-content:space-between;padding:3px 0"><span style="color:#94a3b8">Alpha</span><span style="color:#a78bfa">${this.alpha}</span></div>
    </div>`;
  }
}

export { SemanticSearchDashboard, HybridResult, IndexStats };
