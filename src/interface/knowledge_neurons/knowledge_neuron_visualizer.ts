// @omni-layer Interface | @omni-source EleutherAI/knowledge-neurons | @omni-lang TypeScript
// @omni-description Knowledge neuron visualizer: interactive heatmap of neuron
// attributions across transformer layers with suppression controls.

interface NeuronAttribution {
  layer: number;
  neuron: number;
  attribution: number;
}

interface LayerStats {
  layer: number;
  avgAttribution: number;
  maxAttribution: number;
  activeNeurons: number;
}

class KnowledgeNeuronVisualizer {
  private container: HTMLElement;
  private neurons: NeuronAttribution[] = [];
  private nLayers: number;
  private dFfn: number;
  private suppressedNeurons: Set<string> = new Set();

  constructor(containerId: string, nLayers: number = 12, dFfn: number = 3072) {
    const el = document.getElementById(containerId);
    if (!el) throw new Error(`Container ${containerId} not found`);
    this.container = el;
    this.nLayers = nLayers;
    this.dFfn = dFfn;
  }

  loadAttributions(neurons: NeuronAttribution[]): void {
    this.neurons = neurons.sort((a, b) => b.attribution - a.attribution);
    this.render();
  }

  toggleSuppression(layer: number, neuron: number): void {
    const key = `${layer}:${neuron}`;
    if (this.suppressedNeurons.has(key)) {
      this.suppressedNeurons.delete(key);
    } else {
      this.suppressedNeurons.add(key);
    }
    this.render();
  }

  private getLayerStats(): LayerStats[] {
    const stats: Map<number, { sum: number; max: number; count: number }> = new Map();
    for (const n of this.neurons) {
      const s = stats.get(n.layer) || { sum: 0, max: 0, count: 0 };
      s.sum += n.attribution;
      s.max = Math.max(s.max, n.attribution);
      s.count++;
      stats.set(n.layer, s);
    }
    return Array.from(stats.entries()).map(([layer, s]) => ({
      layer,
      avgAttribution: s.sum / s.count,
      maxAttribution: s.max,
      activeNeurons: s.count,
    })).sort((a, b) => a.layer - b.layer);
  }

  private render(): void {
    const topK = this.neurons.slice(0, 20);
    const maxAttr = topK.length > 0 ? topK[0].attribution : 1;
    const layerStats = this.getLayerStats();

    this.container.innerHTML = `
      <div style="display:grid;grid-template-columns:1fr 280px;gap:16px">
        <div style="background:#1a1f36;border-radius:12px;padding:20px">
          <h3 style="color:#93c5fd;margin-bottom:16px">🧠 Top Knowledge Neurons</h3>
          <div style="display:flex;flex-direction:column;gap:6px">
            ${topK.map(n => {
              const key = `${n.layer}:${n.neuron}`;
              const suppressed = this.suppressedNeurons.has(key);
              const pct = (n.attribution / maxAttr * 100).toFixed(1);
              const color = suppressed ? '#64748b' : this.heatColor(n.attribution / maxAttr);
              return `<div style="display:flex;align-items:center;gap:8px;padding:6px 10px;background:#0a0e17;border-radius:6px;opacity:${suppressed ? 0.5 : 1}">
                <span style="font-size:0.75rem;color:#64748b;width:80px">L${n.layer}:N${n.neuron}</span>
                <div style="flex:1;height:16px;background:#1e293b;border-radius:4px;overflow:hidden">
                  <div style="width:${pct}%;height:100%;background:${color};border-radius:4px;transition:width 0.3s"></div>
                </div>
                <span style="font-size:0.75rem;color:${color};width:50px;text-align:right">${n.attribution.toFixed(4)}</span>
              </div>`;
            }).join('')}
          </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:12px">
          <div style="background:#1a1f36;border-radius:8px;padding:14px">
            <div style="font-size:1.4rem;font-weight:700;color:#60a5fa">${this.neurons.length}</div>
            <div style="font-size:0.75rem;color:#64748b">Active Neurons</div>
          </div>
          <div style="background:#1a1f36;border-radius:8px;padding:14px">
            <div style="font-size:1.4rem;font-weight:700;color:#a78bfa">${this.suppressedNeurons.size}</div>
            <div style="font-size:0.75rem;color:#64748b">Suppressed</div>
          </div>
          <div style="background:#1a1f36;border-radius:8px;padding:14px">
            <h4 style="color:#93c5fd;font-size:0.85rem;margin-bottom:8px">Layer Activity</h4>
            ${layerStats.map(ls => `<div style="display:flex;justify-content:space-between;font-size:0.8rem;padding:2px 0">
              <span style="color:#94a3b8">Layer ${ls.layer}</span>
              <span style="color:#60a5fa">${ls.activeNeurons}</span>
            </div>`).join('')}
          </div>
        </div>
      </div>`;
  }

  private heatColor(intensity: number): string {
    const r = Math.round(255 * intensity);
    const b = Math.round(255 * (1 - intensity));
    return `rgb(${r}, 60, ${b})`;
  }
}

export { KnowledgeNeuronVisualizer, NeuronAttribution, LayerStats };
