// @omni-layer Interface | @omni-source minimaxir/imgbeddings | @omni-lang TypeScript
// @omni-description Image search gallery: visual similarity search interface
// with grid display, similarity scores, and collection browser.

interface ImageResult {
  id: string;
  url: string;
  score: number;
  metadata?: Record<string, string>;
}

interface Collection {
  id: string;
  name: string;
  totalImages: number;
  embeddingDim: number;
}

class ImageSearchGallery {
  private container: HTMLElement;
  private results: ImageResult[] = [];
  private collections: Collection[] = [];
  private selectedCollection: string = '';
  private queryMode: 'image' | 'text' = 'text';

  constructor(containerId: string) {
    const el = document.getElementById(containerId);
    if (!el) throw new Error(`Container ${containerId} not found`);
    this.container = el;
  }

  setCollections(collections: Collection[]): void {
    this.collections = collections;
    if (collections.length) this.selectedCollection = collections[0].id;
    this.render();
  }

  setResults(results: ImageResult[]): void {
    this.results = results;
    this.renderResults();
  }

  private render(): void {
    this.container.innerHTML = `
      <div style="background:#1a1f36;border-radius:12px;padding:20px;margin-bottom:16px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
          <h3 style="color:#93c5fd">🖼️ Image Similarity Search</h3>
          <div style="display:flex;gap:8px">
            <button style="padding:6px 14px;border-radius:6px;border:none;background:${this.queryMode==='text'?'#60a5fa':'#1e293b'};color:white;cursor:pointer;font-size:0.8rem">Text</button>
            <button style="padding:6px 14px;border-radius:6px;border:none;background:${this.queryMode==='image'?'#60a5fa':'#1e293b'};color:white;cursor:pointer;font-size:0.8rem">Image</button>
          </div>
        </div>
        <div style="display:flex;gap:12px">
          <input type="text" placeholder="Describe the image you're looking for..." style="flex:1;padding:10px 16px;background:#0a0e17;border:1px solid #334155;border-radius:8px;color:#e2e8f0;font-size:0.9rem">
          <select style="padding:8px 12px;background:#0a0e17;border:1px solid #334155;border-radius:8px;color:#e2e8f0;font-size:0.85rem">
            ${this.collections.map(c => `<option value="${c.id}">${c.name} (${c.totalImages})</option>`).join('')}
          </select>
        </div>
      </div>
      <div id="searchResults" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px">
        ${this.results.length ? this.renderResultCards() : '<p style="color:#64748b;grid-column:1/-1;text-align:center;padding:40px">Search to see results</p>'}
      </div>`;
  }

  private renderResultCards(): string {
    return this.results.map((r, i) => {
      const hue = Math.round(r.score * 120); // green=high, red=low
      return `<div style="background:#1a1f36;border-radius:10px;overflow:hidden;border:1px solid #1e293b;transition:transform 0.2s">
        <div style="height:180px;background:linear-gradient(135deg,hsl(${hue+200},40%,15%),hsl(${hue+240},40%,20%));display:flex;align-items:center;justify-content:center">
          <span style="font-size:2rem">🖼️</span>
        </div>
        <div style="padding:12px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
            <span style="font-size:0.8rem;color:#94a3b8">#${i+1}</span>
            <span style="font-size:0.75rem;padding:2px 8px;border-radius:10px;background:hsl(${hue},60%,15%);color:hsl(${hue},80%,70%)">${(r.score*100).toFixed(1)}%</span>
          </div>
          <div style="font-size:0.8rem;color:#64748b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${r.id}</div>
        </div>
      </div>`;
    }).join('');
  }

  private renderResults(): void {
    const area = document.getElementById('searchResults');
    if (area) area.innerHTML = this.renderResultCards();
  }
}

export { ImageSearchGallery, ImageResult, Collection };
