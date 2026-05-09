// @omni-layer Interface | @omni-source EleutherAI/lm-evaluation-harness | @omni-lang TypeScript
// @omni-description LM Eval leaderboard: interactive model comparison with
// radar charts, per-task breakdowns, and ranking tables.

interface ModelScore { model: string; scores: Record<string, number>; avg: number; rank: number; }

class LMEvalLeaderboard {
  private entries: ModelScore[] = [];

  addModel(model: string, scores: Record<string, number>): void {
    const avg = Object.values(scores).reduce((s, v) => s + v, 0) / Math.max(Object.keys(scores).length, 1);
    this.entries.push({ model, scores, avg, rank: 0 });
    this.entries.sort((a, b) => b.avg - a.avg);
    this.entries.forEach((e, i) => e.rank = i + 1);
  }

  renderTable(): string {
    const tasks = [...new Set(this.entries.flatMap(e => Object.keys(e.scores)))];
    const header = `<tr><th>#</th><th>Model</th><th>Avg</th>${tasks.map(t => `<th>${t}</th>`).join('')}</tr>`;
    const rows = this.entries.map(e =>
      `<tr><td>${e.rank}</td><td style="font-weight:600">${e.model}</td><td style="color:#7c3aed">${(e.avg*100).toFixed(1)}%</td>${tasks.map(t => `<td>${((e.scores[t]||0)*100).toFixed(1)}%</td>`).join('')}</tr>`
    ).join('');
    return `<table style="width:100%;border-collapse:collapse;font-size:0.85rem">${header}${rows}</table>`;
  }

  renderRadar(canvas: HTMLCanvasElement, modelIdx: number): void {
    const ctx = canvas.getContext('2d');
    if (!ctx || modelIdx >= this.entries.length) return;
    const e = this.entries[modelIdx];
    const tasks = Object.keys(e.scores);
    const n = tasks.length;
    const cx = canvas.width/2, cy = canvas.height/2, r = Math.min(cx, cy) - 20;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#0a0a1a'; ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#333'; ctx.lineWidth = 1;
    for (let ring = 1; ring <= 4; ring++) {
      ctx.beginPath();
      for (let i = 0; i <= n; i++) {
        const angle = (i / n) * Math.PI * 2 - Math.PI/2;
        const x = cx + Math.cos(angle) * r * ring / 4;
        const y = cy + Math.sin(angle) * r * ring / 4;
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      }
      ctx.stroke();
    }
    ctx.fillStyle = 'rgba(124,58,237,0.3)'; ctx.strokeStyle = '#7c3aed'; ctx.lineWidth = 2;
    ctx.beginPath();
    tasks.forEach((t, i) => {
      const angle = (i / n) * Math.PI * 2 - Math.PI/2;
      const val = e.scores[t] || 0;
      const x = cx + Math.cos(angle) * r * val;
      const y = cy + Math.sin(angle) * r * val;
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.closePath(); ctx.fill(); ctx.stroke();
  }
}

export { LMEvalLeaderboard };
export type { ModelScore };
