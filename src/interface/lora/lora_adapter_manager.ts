// @omni-layer Interface | @omni-source huggingface/peft | @omni-lang TypeScript
// @omni-description LoRA adapter manager UI: visual adapter configuration,
// training progress, and merge/deploy controls.

interface LoRAConfig { rank: number; alpha: number; target_modules: string[]; dropout: number; }
interface TrainingProgress { step: number; loss: number; lr: number; eta_sec: number; }

class LoRAAdapterManager {
  private adapters: Map<string, { config: LoRAConfig; progress: TrainingProgress[] }> = new Map();

  createAdapter(name: string, config: LoRAConfig): { data?: any; error?: string } {
    if (this.adapters.has(name)) return { error: `${name} exists` };
    this.adapters.set(name, { config, progress: [] });
    const paramRatio = (config.rank * 2) / (768 * 768) * 100;
    return { data: { name, config, param_ratio_pct: paramRatio.toFixed(4) } };
  }

  logProgress(name: string, prog: TrainingProgress): { data?: any; error?: string } {
    const adapter = this.adapters.get(name);
    if (!adapter) return { error: 'Not found' };
    adapter.progress.push(prog);
    return { data: { step: prog.step, total_logged: adapter.progress.length } };
  }

  renderConfigCard(name: string): string {
    const adapter = this.adapters.get(name);
    if (!adapter) return '<div>Not found</div>';
    const c = adapter.config;
    return `<div style="background:#161b22;padding:1rem;border-radius:10px;color:#c9d1d9;font-size:0.85rem">
      <h4 style="color:#7c3aed;margin-bottom:0.5rem">🔧 ${name}</h4>
      <div>Rank: <strong>${c.rank}</strong> | Alpha: <strong>${c.alpha}</strong> | Dropout: ${c.dropout}</div>
      <div>Targets: ${c.target_modules.map(m => `<code style="background:#0d1117;padding:1px 4px;border-radius:3px">${m}</code>`).join(' ')}</div>
      <div style="margin-top:0.5rem;opacity:0.6">Steps: ${adapter.progress.length} | Latest loss: ${adapter.progress.length > 0 ? adapter.progress[adapter.progress.length-1].loss.toFixed(4) : 'N/A'}</div>
    </div>`;
  }

  listAdapters(): string[] { return Array.from(this.adapters.keys()); }
}

export { LoRAAdapterManager };
export type { LoRAConfig, TrainingProgress };
