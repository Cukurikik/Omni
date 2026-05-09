// @omni-layer Interface | @omni-source dmlc/torchblocks | @omni-lang TypeScript
// @omni-description NLP batch evaluator UI: batch upload, progress tracking,
// per-task metric display, and exportable results table.

interface BatchItem {
  id: string;
  text: string;
  taskType: 'classification' | 'ner' | 'similarity';
  result?: Record<string, number>;
  status: 'pending' | 'processing' | 'done' | 'error';
}

interface BatchStats {
  total: number;
  done: number;
  errors: number;
  avgLatencyMs: number;
}

class NLPBatchEvaluatorUI {
  private container: HTMLElement;
  private items: BatchItem[] = [];
  private stats: BatchStats = { total: 0, done: 0, errors: 0, avgLatencyMs: 0 };

  constructor(containerId: string) {
    const el = document.getElementById(containerId);
    if (!el) throw new Error(`Container ${containerId} not found`);
    this.container = el;
    this.render();
  }

  setItems(items: BatchItem[]): void {
    this.items = items;
    this.stats = {
      total: items.length,
      done: items.filter(i => i.status === 'done').length,
      errors: items.filter(i => i.status === 'error').length,
      avgLatencyMs: 0,
    };
    this.render();
  }

  updateItem(id: string, result: Record<string, number>): void {
    const item = this.items.find(i => i.id === id);
    if (item) { item.result = result; item.status = 'done'; }
    this.stats.done = this.items.filter(i => i.status === 'done').length;
    this.render();
  }

  private render(): void {
    const progress = this.stats.total > 0 ? (this.stats.done / this.stats.total * 100) : 0;
    this.container.innerHTML = `
      <div style="background:#1a1f36;border-radius:12px;padding:20px;margin-bottom:16px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
          <h3 style="color:#93c5fd">📦 Batch Evaluator</h3>
          <span style="font-size:0.8rem;color:#64748b">${this.stats.done}/${this.stats.total} complete</span>
        </div>
        <div style="background:#0a0e17;border-radius:6px;height:8px;overflow:hidden">
          <div style="width:${progress}%;height:100%;background:linear-gradient(90deg,#60a5fa,#a78bfa);transition:width 0.5s"></div>
        </div>
      </div>
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:16px">
        ${[{l:'Total',v:this.stats.total,c:'#60a5fa'},{l:'Done',v:this.stats.done,c:'#10b981'},
           {l:'Errors',v:this.stats.errors,c:'#ef4444'},{l:'Pending',v:this.stats.total-this.stats.done-this.stats.errors,c:'#f59e0b'}]
          .map(s => `<div style="background:#1a1f36;border-radius:8px;padding:10px;text-align:center">
            <div style="font-size:1.2rem;font-weight:700;color:${s.c}">${s.v}</div>
            <div style="font-size:0.65rem;color:#64748b">${s.l}</div></div>`).join('')}
      </div>
      <div style="background:#1a1f36;border-radius:12px;padding:16px;max-height:400px;overflow-y:auto">
        <table style="width:100%;border-collapse:collapse;font-size:0.8rem">
          <thead><tr style="color:#64748b;border-bottom:1px solid #334155">
            <th style="text-align:left;padding:6px">ID</th><th>Task</th><th>Status</th><th>Result</th></tr></thead>
          <tbody>${this.items.map(item => {
            const statusColor = item.status==='done'?'#10b981':item.status==='error'?'#ef4444':item.status==='processing'?'#f59e0b':'#64748b';
            return `<tr style="border-bottom:1px solid #1e293b20">
              <td style="padding:6px;color:#94a3b8">${item.id}</td>
              <td style="padding:6px;color:#a78bfa">${item.taskType}</td>
              <td style="padding:6px;color:${statusColor}">${item.status}</td>
              <td style="padding:6px;color:#e2e8f0">${item.result ? Object.entries(item.result).map(([k,v])=>`${k}:${(v as number).toFixed(3)}`).join(' ') : '-'}</td>
            </tr>`;}).join('')}
          </tbody></table>
      </div>`;
  }
}

export { NLPBatchEvaluatorUI, BatchItem, BatchStats };
