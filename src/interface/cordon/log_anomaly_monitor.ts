// @omni-layer Interface | @omni-source calebevans/cordon | @omni-lang TypeScript
// @omni-description Log anomaly monitor: real-time log stream with anomaly
// highlighting, template grouping, and severity filtering.

interface LogLine {
  timestamp: string;
  line: string;
  template: string;
  isAnomaly: boolean;
  distance: number;
  severity: 'debug' | 'info' | 'warning' | 'error' | 'critical';
}

interface AnomalyStats {
  totalLines: number;
  anomalies: number;
  anomalyRate: number;
  uniqueTemplates: number;
}

class LogAnomalyMonitor {
  private container: HTMLElement;
  private logs: LogLine[] = [];
  private stats: AnomalyStats | null = null;
  private filter: string = 'all';

  constructor(containerId: string) {
    const el = document.getElementById(containerId);
    if (!el) throw new Error(`Container ${containerId} not found`);
    this.container = el;
  }

  addLogs(lines: LogLine[]): void {
    this.logs = [...this.logs, ...lines].slice(-200);
    this.render();
  }

  setStats(stats: AnomalyStats): void {
    this.stats = stats;
    this.render();
  }

  private render(): void {
    const filtered = this.filter === 'all' ? this.logs :
      this.filter === 'anomaly' ? this.logs.filter(l => l.isAnomaly) :
      this.logs.filter(l => l.severity === this.filter);

    this.container.innerHTML = `
      <div style="display:grid;grid-template-columns:1fr 260px;gap:16px">
        <div>
          <div style="background:#1a1f36;border-radius:12px;padding:16px;margin-bottom:12px;display:flex;gap:8px;align-items:center">
            <h3 style="color:#93c5fd;margin-right:auto">📊 Log Stream</h3>
            ${['all','anomaly','error','critical'].map(f => `
              <button style="padding:4px 12px;border-radius:6px;border:none;font-size:0.75rem;cursor:pointer;background:${this.filter===f?'#60a5fa':'#1e293b'};color:${this.filter===f?'white':'#94a3b8'}">${f}</button>`).join('')}
          </div>
          <div style="background:#0a0e17;border-radius:8px;max-height:500px;overflow-y:auto;font-family:monospace;font-size:0.75rem">
            ${filtered.slice(-50).reverse().map(l => this.renderLogLine(l)).join('')}
          </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:12px">
          ${this.renderStatCards()}
          <div style="background:#1a1f36;border-radius:10px;padding:14px">
            <h4 style="color:#93c5fd;font-size:0.85rem;margin-bottom:10px">🔥 Anomaly Rate</h4>
            ${this.renderAnomalyGauge()}
          </div>
        </div>
      </div>`;
  }

  private renderLogLine(l: LogLine): string {
    const colors: Record<string, string> = {
      debug: '#64748b', info: '#94a3b8', warning: '#f59e0b', error: '#ef4444', critical: '#dc2626'
    };
    const bg = l.isAnomaly ? '#7f1d1d20' : 'transparent';
    const border = l.isAnomaly ? 'border-left:2px solid #ef4444' : '';
    return `<div style="padding:4px 8px;${border};background:${bg};border-bottom:1px solid #1e293b10">
      <span style="color:#64748b">${l.timestamp}</span>
      <span style="color:${colors[l.severity]};font-weight:600;margin:0 4px">[${l.severity.toUpperCase()}]</span>
      <span style="color:${l.isAnomaly ? '#fca5a5' : '#e2e8f0'}">${l.line.substring(0, 120)}</span>
      ${l.isAnomaly ? `<span style="color:#ef4444;font-size:0.65rem;margin-left:8px">⚠ ${l.distance.toFixed(3)}</span>` : ''}
    </div>`;
  }

  private renderStatCards(): string {
    if (!this.stats) return '';
    return [
      { label: 'Total Lines', value: this.stats.totalLines, color: '#60a5fa' },
      { label: 'Anomalies', value: this.stats.anomalies, color: '#ef4444' },
      { label: 'Templates', value: this.stats.uniqueTemplates, color: '#a78bfa' },
    ].map(c => `<div style="background:#1a1f36;border-radius:8px;padding:12px;border-left:3px solid ${c.color}">
      <div style="font-size:1.2rem;font-weight:700;color:${c.color}">${c.value}</div>
      <div style="font-size:0.7rem;color:#64748b">${c.label}</div>
    </div>`).join('');
  }

  private renderAnomalyGauge(): string {
    const rate = this.stats ? this.stats.anomalyRate * 100 : 0;
    const hue = Math.round((1 - rate / 100) * 120);
    return `<div style="background:#0a0e17;border-radius:8px;height:20px;overflow:hidden">
      <div style="height:100%;width:${rate}%;background:hsl(${hue},60%,45%);border-radius:8px;transition:width 0.5s"></div>
    </div>
    <div style="text-align:center;font-size:1.1rem;font-weight:700;color:hsl(${hue},60%,60%);margin-top:6px">${rate.toFixed(1)}%</div>`;
  }
}

export { LogAnomalyMonitor, LogLine, AnomalyStats };
