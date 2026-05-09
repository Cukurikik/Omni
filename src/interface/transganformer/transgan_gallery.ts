// @omni-layer Interface | @omni-source lucidrains/transganformer | @omni-lang TypeScript
// @omni-description GAN image gallery: generated image grid with loss curves,
// discriminator scores, and generation controls.

interface GANGeneratedImage {
  id: number;
  dScore: number;
  resolution: number;
  timestamp: string;
}

interface GANTrainingStats {
  step: number;
  dLoss: number;
  gLoss: number;
  dReal: number;
  dFake: number;
}

class TransGANGallery {
  private container: HTMLElement;
  private images: GANGeneratedImage[] = [];
  private stats: GANTrainingStats[] = [];

  constructor(containerId: string) {
    const el = document.getElementById(containerId);
    if (!el) throw new Error(`Container ${containerId} not found`);
    this.container = el;
  }

  setImages(images: GANGeneratedImage[]): void {
    this.images = images;
    this.render();
  }

  addTrainingStep(stat: GANTrainingStats): void {
    this.stats.push(stat);
    this.renderLossCurve();
  }

  private render(): void {
    this.container.innerHTML = `
      <div style="display:grid;grid-template-columns:1fr 260px;gap:16px">
        <div>
          <div style="background:#1a1f36;border-radius:12px;padding:20px;margin-bottom:12px">
            <h3 style="color:#93c5fd;margin-bottom:16px">🎨 Generated Images</h3>
            <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px">
              ${this.images.map(img => this.renderImageCard(img)).join('')}
            </div>
          </div>
          <div id="lossCurveArea" style="background:#1a1f36;border-radius:12px;padding:20px">
            <h3 style="color:#93c5fd;margin-bottom:12px">📉 Training Loss</h3>
            ${this.renderLossChart()}
          </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:12px">
          ${this.renderTrainingStats()}
          <div style="background:#1a1f36;border-radius:10px;padding:14px">
            <h4 style="color:#93c5fd;font-size:0.85rem;margin-bottom:10px">⚙️ Generation</h4>
            <button style="width:100%;padding:10px;background:linear-gradient(135deg,#a78bfa,#f472b6);border:none;border-radius:8px;color:white;font-weight:600;cursor:pointer">Generate Batch</button>
          </div>
        </div>
      </div>`;
  }

  private renderImageCard(img: GANGeneratedImage): string {
    const quality = img.dScore > 0.8 ? '#10b981' : img.dScore > 0.5 ? '#f59e0b' : '#ef4444';
    const hue = Math.round(img.id * 37 % 360);
    return `<div style="border-radius:8px;overflow:hidden;border:1px solid #1e293b">
      <div style="height:100px;background:linear-gradient(135deg,hsl(${hue},40%,15%),hsl(${(hue+90)%360},40%,20%));display:flex;align-items:center;justify-content:center">
        <span style="font-size:1.5rem">🖼️</span>
      </div>
      <div style="padding:6px 8px;background:#0a0e17;display:flex;justify-content:space-between;font-size:0.7rem">
        <span style="color:#64748b">#${img.id}</span>
        <span style="color:${quality}">${(img.dScore*100).toFixed(0)}%</span>
      </div>
    </div>`;
  }

  private renderLossChart(): string {
    if (!this.stats.length) return '<div style="color:#64748b;font-size:0.85rem">No training data</div>';
    const width = 400, height = 120;
    const maxLoss = Math.max(...this.stats.map(s => Math.max(s.dLoss, s.gLoss)), 0.1);
    const dPath = this.stats.map((s, i) => `${(i/this.stats.length)*width},${height - (s.dLoss/maxLoss)*height}`).join(' ');
    const gPath = this.stats.map((s, i) => `${(i/this.stats.length)*width},${height - (s.gLoss/maxLoss)*height}`).join(' ');
    return `<svg width="${width}" height="${height}" style="width:100%">
      <polyline points="${dPath}" fill="none" stroke="#60a5fa" stroke-width="1.5"/>
      <polyline points="${gPath}" fill="none" stroke="#a78bfa" stroke-width="1.5"/>
    </svg>
    <div style="display:flex;gap:16px;margin-top:6px;font-size:0.75rem">
      <span style="color:#60a5fa">● D Loss</span><span style="color:#a78bfa">● G Loss</span>
    </div>`;
  }

  private renderLossChart_stub(): void {
    const area = document.getElementById('lossCurveArea');
    if (area) area.innerHTML = `<h3 style="color:#93c5fd;margin-bottom:12px">📉 Training Loss</h3>${this.renderLossChart()}`;
  }

  private renderLossCurve(): void { this.renderLossChart_stub(); }

  private renderTrainingStats(): string {
    const last = this.stats.length ? this.stats[this.stats.length - 1] : null;
    return [
      { label: 'Step', value: last ? `${last.step}` : '0', color: '#60a5fa' },
      { label: 'D Loss', value: last ? last.dLoss.toFixed(4) : '-', color: '#22d3ee' },
      { label: 'G Loss', value: last ? last.gLoss.toFixed(4) : '-', color: '#a78bfa' },
      { label: 'Images', value: `${this.images.length}`, color: '#f59e0b' },
    ].map(c => `<div style="background:#1a1f36;border-radius:8px;padding:12px;border-left:3px solid ${c.color}">
      <div style="font-size:1.2rem;font-weight:700;color:${c.color}">${c.value}</div>
      <div style="font-size:0.7rem;color:#64748b">${c.label}</div>
    </div>`).join('');
  }
}

export { TransGANGallery, GANGeneratedImage, GANTrainingStats };
