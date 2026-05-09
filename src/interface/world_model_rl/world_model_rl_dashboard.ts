// @omni-layer Interface | @omni-source lucidrains/improving-transformers-world-model-for-rl | @omni-lang TypeScript
// @omni-description RL world model dashboard: trajectory visualization with
// reward curves, value estimation, and imagined rollout display.

interface TrajectoryStep {
  step: number;
  reward: number;
  value: number;
  stateNorm: number;
}

interface RolloutResult {
  totalReward: number;
  discountedReturn: number;
  nSteps: number;
  avgReward: number;
}

class WorldModelRLDashboard {
  private container: HTMLElement;
  private trajectory: TrajectoryStep[] = [];
  private rollout: RolloutResult | null = null;

  constructor(containerId: string) {
    const el = document.getElementById(containerId);
    if (!el) throw new Error(`Container ${containerId} not found`);
    this.container = el;
  }

  setTrajectory(steps: TrajectoryStep[]): void {
    this.trajectory = steps;
    this.render();
  }

  setRollout(result: RolloutResult): void {
    this.rollout = result;
    this.render();
  }

  private render(): void {
    this.container.innerHTML = `
      <div style="display:grid;grid-template-columns:1fr 240px;gap:16px">
        <div>
          <div style="background:#1a1f36;border-radius:12px;padding:20px;margin-bottom:12px">
            <h3 style="color:#93c5fd;margin-bottom:12px">📊 Reward Curve</h3>
            ${this.renderRewardChart()}
          </div>
          <div style="background:#1a1f36;border-radius:12px;padding:20px">
            <h3 style="color:#93c5fd;margin-bottom:12px">🧠 Value Estimation</h3>
            ${this.renderValueChart()}
          </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:12px">
          ${this.renderRolloutCards()}
          <div style="background:#1a1f36;border-radius:10px;padding:14px">
            <h4 style="color:#93c5fd;font-size:0.85rem;margin-bottom:10px">📜 Steps</h4>
            <div style="max-height:250px;overflow-y:auto">
              ${this.trajectory.slice(-15).reverse().map(s => `
                <div style="display:flex;justify-content:space-between;padding:3px 0;font-size:0.75rem;border-bottom:1px solid #1e293b20">
                  <span style="color:#64748b">t=${s.step}</span>
                  <span style="color:${s.reward>=0?'#10b981':'#ef4444'}">${s.reward.toFixed(3)}</span>
                </div>`).join('')}
            </div>
          </div>
        </div>
      </div>`;
  }

  private renderRewardChart(): string {
    if (!this.trajectory.length) return '<p style="color:#64748b;font-size:0.85rem">No data</p>';
    const w = 400, h = 100;
    const maxR = Math.max(...this.trajectory.map(s => Math.abs(s.reward)), 0.1);
    const mid = h / 2;
    const points = this.trajectory.map((s, i) => `${(i/this.trajectory.length)*w},${mid - (s.reward/maxR)*mid}`).join(' ');
    return `<svg width="${w}" height="${h}" style="width:100%">
      <line x1="0" y1="${mid}" x2="${w}" y2="${mid}" stroke="#334155" stroke-dasharray="4"/>
      <polyline points="${points}" fill="none" stroke="#10b981" stroke-width="2"/>
    </svg>`;
  }

  private renderValueChart(): string {
    if (!this.trajectory.length) return '<p style="color:#64748b;font-size:0.85rem">No data</p>';
    const w = 400, h = 80;
    const maxV = Math.max(...this.trajectory.map(s => Math.abs(s.value)), 0.1);
    const points = this.trajectory.map((s, i) => `${(i/this.trajectory.length)*w},${h - ((s.value + maxV)/(2*maxV))*h}`).join(' ');
    return `<svg width="${w}" height="${h}" style="width:100%">
      <polyline points="${points}" fill="none" stroke="#a78bfa" stroke-width="2"/>
    </svg>`;
  }

  private renderRolloutCards(): string {
    if (!this.rollout) return '';
    return [
      { label: 'Total Reward', value: this.rollout.totalReward.toFixed(3), color: '#10b981' },
      { label: 'Return', value: this.rollout.discountedReturn.toFixed(3), color: '#60a5fa' },
      { label: 'Steps', value: `${this.rollout.nSteps}`, color: '#a78bfa' },
      { label: 'Avg Reward', value: this.rollout.avgReward.toFixed(4), color: '#f59e0b' },
    ].map(c => `<div style="background:#1a1f36;border-radius:8px;padding:12px;border-left:3px solid ${c.color}">
      <div style="font-size:1.1rem;font-weight:700;color:${c.color}">${c.value}</div>
      <div style="font-size:0.7rem;color:#64748b">${c.label}</div>
    </div>`).join('');
  }
}

export { WorldModelRLDashboard, TrajectoryStep, RolloutResult };
