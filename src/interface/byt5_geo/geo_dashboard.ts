// @omni-layer Interface | @omni-source Yachay-AI/byt5-geotagging | @omni-lang TypeScript
// @omni-description Geolocation dashboard: interactive map visualization
// with prediction markers, region heatmap, and accuracy metrics.

interface GeoPrediction {
  text: string;
  latitude: number;
  longitude: number;
  confidence: number;
  region: string;
}

interface AccuracyStats {
  n_predictions: number;
  mean_error_km: number;
  median_error_km: number;
  accuracy_100km: number;
  accuracy_500km: number;
}

class GeoLocationDashboard {
  private container: HTMLElement;
  private predictions: GeoPrediction[] = [];
  private accuracy: AccuracyStats | null = null;

  constructor(containerId: string) {
    const el = document.getElementById(containerId);
    if (!el) throw new Error(`Container ${containerId} not found`);
    this.container = el;
  }

  setPredictions(predictions: GeoPrediction[]): void {
    this.predictions = predictions;
    this.render();
  }

  setAccuracy(stats: AccuracyStats): void {
    this.accuracy = stats;
    this.render();
  }

  private render(): void {
    const regionDist = this.getRegionDistribution();
    this.container.innerHTML = `
      <div style="display:grid;grid-template-columns:1fr 300px;gap:16px">
        <div>
          <div style="background:#1a1f36;border-radius:12px;padding:20px;margin-bottom:12px">
            <h3 style="color:#93c5fd;margin-bottom:16px">🗺️ Prediction Map</h3>
            ${this.renderMap()}
          </div>
          <div style="background:#1a1f36;border-radius:12px;padding:20px">
            <h3 style="color:#93c5fd;margin-bottom:12px">📋 Recent Predictions</h3>
            ${this.renderPredictionTable()}
          </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:12px">
          ${this.renderAccuracyCards()}
          <div style="background:#1a1f36;border-radius:10px;padding:14px">
            <h4 style="color:#93c5fd;font-size:0.85rem;margin-bottom:10px">🌍 Region Distribution</h4>
            ${Object.entries(regionDist).map(([r, n]) => `
              <div style="display:flex;justify-content:space-between;padding:4px 0;font-size:0.8rem">
                <span style="color:#94a3b8">${r}</span>
                <span style="color:#60a5fa;font-weight:600">${n}</span>
              </div>`).join('')}
          </div>
        </div>
      </div>`;
  }

  private renderMap(): string {
    const width = 500, height = 250;
    const markers = this.predictions.map(p => {
      const x = ((p.longitude + 180) / 360) * width;
      const y = ((90 - p.latitude) / 180) * height;
      const r = 3 + p.confidence * 4;
      const hue = Math.round(p.confidence * 120);
      return `<circle cx="${x}" cy="${y}" r="${r}" fill="hsl(${hue},70%,50%)" opacity="0.7"><title>${p.text} (${p.latitude.toFixed(2)}, ${p.longitude.toFixed(2)})</title></circle>`;
    }).join('');
    return `<svg width="${width}" height="${height}" style="width:100%;background:#0a0e17;border-radius:8px">
      <rect x="0" y="0" width="${width}" height="${height}" fill="#0a0e17"/>
      <line x1="0" y1="${height/2}" x2="${width}" y2="${height/2}" stroke="#1e293b"/>
      <line x1="${width/2}" y1="0" x2="${width/2}" y2="${height}" stroke="#1e293b"/>
      ${markers}
    </svg>`;
  }

  private renderPredictionTable(): string {
    return this.predictions.slice(0, 8).map(p => `
      <div style="display:grid;grid-template-columns:1fr 80px 80px 60px;gap:8px;padding:6px 0;border-bottom:1px solid #1e293b20;font-size:0.8rem">
        <span style="color:#94a3b8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${p.text}</span>
        <span style="color:#60a5fa">${p.latitude.toFixed(2)}°</span>
        <span style="color:#a78bfa">${p.longitude.toFixed(2)}°</span>
        <span style="color:#22d3ee">${(p.confidence*100).toFixed(0)}%</span>
      </div>`).join('');
  }

  private renderAccuracyCards(): string {
    if (!this.accuracy) return '';
    const cards = [
      { label: 'Mean Error', value: `${this.accuracy.mean_error_km.toFixed(0)} km`, color: '#60a5fa' },
      { label: 'Acc@100km', value: `${(this.accuracy.accuracy_100km*100).toFixed(1)}%`, color: '#22d3ee' },
      { label: 'Acc@500km', value: `${(this.accuracy.accuracy_500km*100).toFixed(1)}%`, color: '#a78bfa' },
      { label: 'Predictions', value: `${this.accuracy.n_predictions}`, color: '#f59e0b' },
    ];
    return cards.map(c => `<div style="background:#1a1f36;border-radius:8px;padding:12px;border-left:3px solid ${c.color}">
      <div style="font-size:1.2rem;font-weight:700;color:${c.color}">${c.value}</div>
      <div style="font-size:0.7rem;color:#64748b">${c.label}</div>
    </div>`).join('');
  }

  private getRegionDistribution(): Record<string, number> {
    const dist: Record<string, number> = {};
    for (const p of this.predictions) {
      dist[p.region] = (dist[p.region] || 0) + 1;
    }
    return dist;
  }
}

export { GeoLocationDashboard, GeoPrediction, AccuracyStats };
