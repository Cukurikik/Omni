// @omni-layer Interface | @omni-source desaixie/zeroverse | @omni-lang TypeScript
// @omni-description 3D asset browser: gallery view of procedural meshes with
// reconstruction status, preview thumbnails, and job monitoring.

interface Asset3D {
  id: string;
  name: string;
  status: 'draft' | 'processing' | 'ready' | 'published';
  nVertices: number;
  nViews: number;
  seed: number;
  quality: 'low' | 'medium' | 'high' | 'ultra';
  version: number;
}

interface ReconJob {
  id: string;
  assetId: string;
  status: string;
  nPrimitives: number;
  nViews: number;
}

class Asset3DBrowser {
  private container: HTMLElement;
  private assets: Asset3D[] = [];
  private jobs: ReconJob[] = [];
  private filter: string = 'all';

  constructor(containerId: string) {
    const el = document.getElementById(containerId);
    if (!el) throw new Error(`Container ${containerId} not found`);
    this.container = el;
  }

  setAssets(assets: Asset3D[]): void {
    this.assets = assets;
    this.render();
  }

  setJobs(jobs: ReconJob[]): void {
    this.jobs = jobs;
    this.render();
  }

  private render(): void {
    const filtered = this.filter === 'all' ? this.assets : this.assets.filter(a => a.status === this.filter);
    const statusColors: Record<string, string> = { draft: '#64748b', processing: '#f59e0b', ready: '#10b981', published: '#60a5fa' };

    this.container.innerHTML = `
      <div style="background:#1a1f36;border-radius:12px;padding:16px;margin-bottom:16px;display:flex;gap:8px;align-items:center">
        <h3 style="color:#93c5fd;margin-right:auto">🎨 3D Asset Browser</h3>
        ${['all','draft','processing','ready','published'].map(f => `
          <button style="padding:4px 12px;border-radius:6px;border:none;font-size:0.75rem;cursor:pointer;background:${this.filter===f?'#60a5fa':'#1e293b'};color:${this.filter===f?'white':'#94a3b8'}">${f}</button>`).join('')}
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px">
        ${filtered.map(a => {
          const color = statusColors[a.status] || '#64748b';
          const hue = (a.seed * 37) % 360;
          return `<div style="background:#1a1f36;border-radius:10px;overflow:hidden;border:1px solid #1e293b">
            <div style="height:140px;background:linear-gradient(135deg,hsl(${hue},30%,15%),hsl(${(hue+60)%360},30%,20%));display:flex;align-items:center;justify-content:center;position:relative">
              <span style="font-size:2.5rem">🏗️</span>
              <span style="position:absolute;top:8px;right:8px;padding:2px 8px;border-radius:10px;font-size:0.65rem;background:${color}20;color:${color};border:1px solid ${color}40">${a.status}</span>
            </div>
            <div style="padding:12px">
              <div style="font-weight:600;color:#e2e8f0;margin-bottom:4px">${a.name}</div>
              <div style="display:flex;gap:8px;font-size:0.75rem;color:#64748b">
                <span>🔺 ${a.nVertices}</span><span>👁️ ${a.nViews}</span><span>v${a.version}</span>
              </div>
              <div style="margin-top:6px;font-size:0.7rem;color:#94a3b8">Quality: ${a.quality} | Seed: ${a.seed}</div>
            </div>
          </div>`;
        }).join('')}
      </div>
      ${this.jobs.length ? this.renderJobs() : ''}`;
  }

  private renderJobs(): string {
    return `<div style="background:#1a1f36;border-radius:12px;padding:16px;margin-top:16px">
      <h4 style="color:#93c5fd;margin-bottom:10px">⚙️ Active Jobs</h4>
      ${this.jobs.map(j => `<div style="display:flex;justify-content:space-between;padding:6px 0;font-size:0.8rem;border-bottom:1px solid #1e293b20">
        <span style="color:#94a3b8">${j.id.substring(0,8)}</span>
        <span style="color:#e2e8f0">${j.nPrimitives} prims / ${j.nViews} views</span>
        <span style="color:${j.status==='completed'?'#10b981':'#f59e0b'}">${j.status}</span>
      </div>`).join('')}
    </div>`;
  }
}

export { Asset3DBrowser, Asset3D, ReconJob };
