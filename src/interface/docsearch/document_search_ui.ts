// @omni-layer Interface | @omni-source yuanzhoulvpi2017/DocumentSearch | @omni-lang TypeScript
// @omni-description Document search interface: search bar with result cards,
// relevance scoring, chunk highlighting, and corpus statistics.

interface SearchResult {
  docId: string;
  chunkIdx: number;
  score: number;
  preview: string;
}

interface CorpusStats {
  name: string;
  totalDocs: number;
  totalChunks: number;
  avgChunkSize: number;
}

class DocumentSearchUI {
  private container: HTMLElement;
  private results: SearchResult[] = [];
  private corpusStats: CorpusStats | null = null;
  private queryTime: number = 0;

  constructor(containerId: string) {
    const el = document.getElementById(containerId);
    if (!el) throw new Error(`Container ${containerId} not found`);
    this.container = el;
    this.render();
  }

  setResults(results: SearchResult[], queryTimeMs: number): void {
    this.results = results;
    this.queryTime = queryTimeMs;
    this.render();
  }

  setCorpusStats(stats: CorpusStats): void {
    this.corpusStats = stats;
    this.render();
  }

  private render(): void {
    this.container.innerHTML = `
      <div style="max-width:800px;margin:0 auto">
        <div style="background:#1a1f36;border-radius:12px;padding:20px;margin-bottom:16px">
          <h3 style="color:#93c5fd;margin-bottom:12px">🔍 Document Search</h3>
          <div style="display:flex;gap:8px">
            <input type="text" id="docSearchInput" placeholder="Search your documents..." style="flex:1;padding:12px 16px;background:#0a0e17;border:1px solid #334155;border-radius:8px;color:#e2e8f0;font-size:0.95rem">
            <button style="padding:10px 20px;background:linear-gradient(135deg,#60a5fa,#a78bfa);border:none;border-radius:8px;color:white;font-weight:600;cursor:pointer">Search</button>
          </div>
          ${this.queryTime > 0 ? `<div style="margin-top:8px;font-size:0.8rem;color:#64748b">${this.results.length} results in ${this.queryTime.toFixed(0)}ms</div>` : ''}
        </div>
        <div style="display:grid;grid-template-columns:1fr 220px;gap:16px">
          <div>
            ${this.results.length ? this.renderResults() : '<div style="text-align:center;color:#64748b;padding:40px">Enter a query to search</div>'}
          </div>
          <div style="display:flex;flex-direction:column;gap:12px">
            ${this.renderCorpusInfo()}
          </div>
        </div>
      </div>`;
  }

  private renderResults(): string {
    return this.results.map((r, i) => {
      const scorePct = (r.score * 100).toFixed(1);
      const hue = Math.round(r.score * 120);
      return `<div style="background:#1a1f36;border-radius:10px;padding:16px;margin-bottom:8px;border-left:3px solid hsl(${hue},60%,50%)">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
          <span style="font-size:0.8rem;color:#93c5fd;font-weight:600">📄 ${r.docId}</span>
          <span style="font-size:0.75rem;padding:2px 8px;border-radius:10px;background:hsl(${hue},40%,15%);color:hsl(${hue},70%,60%)">${scorePct}%</span>
        </div>
        <div style="font-size:0.85rem;color:#94a3b8;line-height:1.5">${r.preview}...</div>
        <div style="font-size:0.7rem;color:#64748b;margin-top:6px">Chunk #${r.chunkIdx}</div>
      </div>`;
    }).join('');
  }

  private renderCorpusInfo(): string {
    if (!this.corpusStats) return '';
    return `<div style="background:#1a1f36;border-radius:10px;padding:14px">
      <h4 style="color:#93c5fd;font-size:0.85rem;margin-bottom:10px">📚 Corpus</h4>
      <div style="font-size:0.8rem">
        <div style="padding:3px 0"><span style="color:#94a3b8">Name:</span> <span style="color:#e2e8f0">${this.corpusStats.name}</span></div>
        <div style="padding:3px 0"><span style="color:#94a3b8">Documents:</span> <span style="color:#60a5fa;font-weight:600">${this.corpusStats.totalDocs}</span></div>
        <div style="padding:3px 0"><span style="color:#94a3b8">Chunks:</span> <span style="color:#a78bfa;font-weight:600">${this.corpusStats.totalChunks}</span></div>
        <div style="padding:3px 0"><span style="color:#94a3b8">Avg Size:</span> <span style="color:#22d3ee">${this.corpusStats.avgChunkSize}</span></div>
      </div>
    </div>`;
  }
}

export { DocumentSearchUI, SearchResult, CorpusStats };
