// @omni-layer Interface | @omni-source microsoft/DeepSpeed | @omni-lang TypeScript
// @omni-description MoE expert utilization dashboard: real-time expert load
// visualization with imbalance alerts and routing analytics.

interface ExpertLoad {
  expert_id: number;
  tokens_routed: number;
  capacity: number;
  utilization: number;
  overflow_count: number;
}

interface MoEDashboardState {
  experts: ExpertLoad[];
  total_tokens: number;
  balance_loss: number;
  step: number;
}

class MoEDashboard {
  private container: HTMLElement | null;

  constructor(containerId: string) {
    this.container = document.getElementById(containerId);
  }

  render(state: MoEDashboardState): void {
    if (!this.container) return;
    const maxUtil = Math.max(...state.experts.map(e => e.utilization), 0.01);
    const expertBars = state.experts.map(e => {
      const pct = Math.round(e.utilization * 100);
      const color = e.utilization > 0.9 ? '#ef4444' : e.utilization > 0.7 ? '#f59e0b' : '#10b981';
      return `<div style="display:flex;align-items:center;margin:3px 0;gap:8px">
        <span style="width:60px;font-size:0.75rem">Expert ${e.expert_id}</span>
        <div style="flex:1;background:#1e1e2e;height:20px;border-radius:4px;overflow:hidden">
          <div style="width:${pct}%;height:100%;background:${color};border-radius:4px;transition:width 0.3s"></div>
        </div>
        <span style="width:50px;font-size:0.7rem;text-align:right">${pct}%</span>
        ${e.overflow_count > 0 ? '<span style="color:#ef4444;font-size:0.7rem">⚠️</span>' : ''}
      </div>`;
    }).join('');

    this.container.innerHTML = `
      <div style="background:#0d1117;padding:1.5rem;border-radius:12px;color:#c9d1d9">
        <h3 style="color:#7c3aed;margin-bottom:1rem">🔀 MoE Expert Utilization — Step ${state.step}</h3>
        <div style="display:flex;gap:1rem;margin-bottom:1rem">
          <div style="text-align:center;flex:1;background:#161b22;padding:0.5rem;border-radius:6px">
            <div style="font-size:1.2rem;font-weight:700;color:#7c3aed">${state.total_tokens}</div>
            <div style="font-size:0.65rem;opacity:0.5">Total Tokens</div>
          </div>
          <div style="text-align:center;flex:1;background:#161b22;padding:0.5rem;border-radius:6px">
            <div style="font-size:1.2rem;font-weight:700;color:#f59e0b">${state.balance_loss.toFixed(4)}</div>
            <div style="font-size:0.65rem;opacity:0.5">Balance Loss</div>
          </div>
        </div>
        ${expertBars}
      </div>`;
  }
}

export { MoEDashboard };
export type { ExpertLoad, MoEDashboardState };
