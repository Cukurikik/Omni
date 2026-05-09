// @omni-layer Interface | @omni-source kanishkamisra/minicons | @omni-lang TypeScript
// @omni-description LM Scoring visualization component: interactive surprisal chart
// with token-level coloring and perplexity trends.

interface TokenScore {
  token: string;
  token_id: number;
  surprisal: number;
  log_prob: number;
  rank: number;
}

interface ScoringVisualization {
  sequence_id: string;
  tokens: TokenScore[];
  perplexity: number;
  mean_surprisal: number;
  entropy: number;
}

class LMScoringVisualizer {
  private container: HTMLElement | null = null;
  private colorScale: (value: number) => string;

  constructor(containerId: string) {
    this.container = document.getElementById(containerId);
    this.colorScale = (v: number) => {
      const r = Math.min(255, Math.floor(v * 255));
      const g = Math.max(0, Math.floor(255 - v * 255));
      return `rgb(${r},${g},60)`;
    };
  }

  render(data: ScoringVisualization): void {
    if (!this.container) return;
    const maxSurp = Math.max(...data.tokens.map(t => t.surprisal), 1);
    const tokensHTML = data.tokens.map(t => {
      const normalized = t.surprisal / maxSurp;
      const color = this.colorScale(normalized);
      return `<span class="token" style="background:${color};padding:2px 4px;margin:1px;border-radius:3px;display:inline-block;cursor:pointer" title="Surprisal: ${t.surprisal.toFixed(2)} bits\nRank: ${t.rank}\nLog-prob: ${t.log_prob.toFixed(4)}">${t.token}</span>`;
    }).join('');
    this.container.innerHTML = `
      <div class="scoring-viz">
        <div class="metrics" style="display:flex;gap:1rem;margin-bottom:1rem">
          <div><strong>PPL:</strong> ${data.perplexity.toFixed(2)}</div>
          <div><strong>Mean Surprisal:</strong> ${data.mean_surprisal.toFixed(2)} bits</div>
          <div><strong>Entropy:</strong> ${data.entropy.toFixed(4)}</div>
        </div>
        <div class="tokens">${tokensHTML}</div>
      </div>`;
  }

  renderChart(data: ScoringVisualization, canvas: HTMLCanvasElement): void {
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const w = canvas.width, h = canvas.height;
    const n = data.tokens.length;
    const maxS = Math.max(...data.tokens.map(t => t.surprisal), 1);
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = '#1a1a2e'; ctx.fillRect(0, 0, w, h);
    const barW = w / n;
    data.tokens.forEach((t, i) => {
      const barH = (t.surprisal / maxS) * (h - 20);
      ctx.fillStyle = this.colorScale(t.surprisal / maxS);
      ctx.fillRect(i * barW, h - 20 - barH, barW - 1, barH);
    });
    ctx.strokeStyle = '#e94560'; ctx.lineWidth = 2; ctx.beginPath();
    const meanY = h - 20 - (data.mean_surprisal / maxS) * (h - 20);
    ctx.moveTo(0, meanY); ctx.lineTo(w, meanY); ctx.stroke();
  }
}

export { LMScoringVisualizer };
export type { TokenScore, ScoringVisualization };
