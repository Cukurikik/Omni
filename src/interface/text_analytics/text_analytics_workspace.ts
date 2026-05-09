// @omni-layer Interface | @omni-source OscarKjell/text | @omni-lang TypeScript
// @omni-description Text analytics workspace: embedding PCA scatter plot,
// similarity matrix heatmap, and cluster visualization.

interface TextEmbPoint {
  label: string;
  x: number;
  y: number;
  cluster?: number;
}

interface SimMatrixData {
  labels: string[];
  matrix: number[][];
}

class TextAnalyticsWorkspace {
  private container: HTMLElement;
  private points: TextEmbPoint[] = [];
  private simMatrix: SimMatrixData | null = null;

  constructor(containerId: string) {
    const el = document.getElementById(containerId);
    if (!el) throw new Error(`Container ${containerId} not found`);
    this.container = el;
  }

  setPCAPoints(points: TextEmbPoint[]): void {
    this.points = points;
    this.render();
  }

  setSimilarityMatrix(data: SimMatrixData): void {
    this.simMatrix = data;
    this.render();
  }

  private render(): void {
    this.container.innerHTML = `
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
        <div style="background:#1a1f36;border-radius:12px;padding:20px">
          <h3 style="color:#93c5fd;margin-bottom:16px">🔵 PCA Projection</h3>
          ${this.renderScatterPlot()}
        </div>
        <div style="background:#1a1f36;border-radius:12px;padding:20px">
          <h3 style="color:#93c5fd;margin-bottom:16px">🔥 Similarity Matrix</h3>
          ${this.renderHeatmap()}
        </div>
      </div>
      <div style="background:#1a1f36;border-radius:12px;padding:20px;margin-top:16px">
        <h3 style="color:#93c5fd;margin-bottom:12px">📊 Cluster Summary</h3>
        ${this.renderClusterSummary()}
      </div>`;
  }

  private renderScatterPlot(): string {
    if (!this.points.length) return '<p style="color:#64748b;font-size:0.85rem">No PCA data</p>';
    const w = 300, h = 250;
    const xs = this.points.map(p => p.x);
    const ys = this.points.map(p => p.y);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);
    const rangeX = maxX - minX || 1, rangeY = maxY - minY || 1;
    const clusterColors = ['#60a5fa', '#a78bfa', '#22d3ee', '#f59e0b', '#10b981', '#f472b6'];
    const dots = this.points.map(p => {
      const cx = ((p.x - minX) / rangeX) * (w - 20) + 10;
      const cy = h - ((p.y - minY) / rangeY) * (h - 20) - 10;
      const color = clusterColors[(p.cluster || 0) % clusterColors.length];
      return `<circle cx="${cx}" cy="${cy}" r="5" fill="${color}" opacity="0.8"><title>${p.label}</title></circle>`;
    }).join('');
    return `<svg width="${w}" height="${h}" style="width:100%">${dots}</svg>`;
  }

  private renderHeatmap(): string {
    if (!this.simMatrix) return '<p style="color:#64748b;font-size:0.85rem">No similarity data</p>';
    const n = this.simMatrix.labels.length;
    const cellSize = Math.min(30, 250 / n);
    const cells = this.simMatrix.matrix.map((row, i) =>
      row.map((val, j) => {
        const intensity = Math.round(val * 255);
        return `<rect x="${j*cellSize}" y="${i*cellSize}" width="${cellSize}" height="${cellSize}" fill="rgb(${intensity},60,${255-intensity})" opacity="0.8"><title>${this.simMatrix!.labels[i]} × ${this.simMatrix!.labels[j]}: ${val.toFixed(3)}</title></rect>`;
      }).join('')
    ).join('');
    return `<svg width="${n*cellSize}" height="${n*cellSize}" style="width:100%">${cells}</svg>`;
  }

  private renderClusterSummary(): string {
    const clusters: Record<number, TextEmbPoint[]> = {};
    for (const p of this.points) {
      const c = p.cluster || 0;
      (clusters[c] = clusters[c] || []).push(p);
    }
    return Object.entries(clusters).map(([id, members]) => `
      <div style="display:inline-block;background:#0a0e17;border-radius:8px;padding:10px;margin:4px;min-width:120px">
        <div style="font-size:0.8rem;color:#60a5fa;font-weight:600">Cluster ${id}</div>
        <div style="font-size:1.1rem;font-weight:700;color:#e2e8f0">${members.length} texts</div>
      </div>`).join('');
  }
}

export { TextAnalyticsWorkspace, TextEmbPoint, SimMatrixData };
