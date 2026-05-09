// @omni-layer Interface | @omni-source jakobhoeg/browser-ai | @omni-lang TypeScript
// @omni-description Browser AI chat: client-side inference chat interface with
// streaming response, model selection, and memory monitoring.

interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  tokens: number;
  latencyMs?: number;
}

interface ModelOption {
  id: string;
  name: string;
  parameterSize: string;
  maxContext: number;
  quantization: string;
}

class BrowserAIChat {
  private container: HTMLElement;
  private messages: ChatMessage[] = [];
  private models: ModelOption[] = [];
  private selectedModel: string = '';
  private memoryUsageMb: number = 0;

  constructor(containerId: string) {
    const el = document.getElementById(containerId);
    if (!el) throw new Error(`Container ${containerId} not found`);
    this.container = el;
  }

  setModels(models: ModelOption[]): void {
    this.models = models;
    if (models.length) this.selectedModel = models[0].id;
    this.render();
  }

  addMessage(msg: ChatMessage): void {
    this.messages.push(msg);
    this.render();
  }

  setMemoryUsage(mb: number): void {
    this.memoryUsageMb = mb;
    this.render();
  }

  private render(): void {
    const totalTokens = this.messages.reduce((s, m) => s + m.tokens, 0);
    const avgLatency = this.messages.filter(m => m.latencyMs).reduce((s, m) => s + (m.latencyMs || 0), 0) / Math.max(this.messages.filter(m => m.latencyMs).length, 1);

    this.container.innerHTML = `
      <div style="display:grid;grid-template-columns:1fr 240px;gap:16px;height:600px">
        <div style="display:flex;flex-direction:column">
          <div style="background:#1a1f36;border-radius:12px;flex:1;overflow-y:auto;padding:16px;margin-bottom:12px">
            ${this.messages.length ? this.messages.map(m => this.renderMessage(m)).join('') : '<div style="text-align:center;color:#64748b;padding:40px">Start a conversation</div>'}
          </div>
          <div style="display:flex;gap:8px">
            <input type="text" id="chatInput" placeholder="Type your message..." style="flex:1;padding:12px;background:#1a1f36;border:1px solid #334155;border-radius:8px;color:#e2e8f0;font-size:0.9rem">
            <button style="padding:10px 20px;background:linear-gradient(135deg,#60a5fa,#a78bfa);border:none;border-radius:8px;color:white;font-weight:600;cursor:pointer">Send</button>
          </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:12px">
          <div style="background:#1a1f36;border-radius:10px;padding:14px">
            <h4 style="color:#93c5fd;font-size:0.85rem;margin-bottom:10px">🤖 Model</h4>
            ${this.models.map(m => `<div style="padding:6px 8px;background:${m.id===this.selectedModel?'#1e3a5f':'#0a0e17'};border-radius:6px;margin:3px 0;font-size:0.8rem;cursor:pointer">
              <div style="color:#e2e8f0">${m.name}</div>
              <div style="color:#64748b;font-size:0.7rem">${m.parameterSize} • ${m.quantization}</div>
            </div>`).join('')}
          </div>
          ${this.renderStatCards(totalTokens, avgLatency)}
        </div>
      </div>`;
  }

  private renderMessage(msg: ChatMessage): string {
    const isUser = msg.role === 'user';
    return `<div style="display:flex;justify-content:${isUser?'flex-end':'flex-start'};margin-bottom:8px">
      <div style="max-width:80%;padding:10px 14px;border-radius:12px;background:${isUser?'#1e3a5f':'#1a1f36'};border:1px solid ${isUser?'#60a5fa40':'#1e293b'}">
        <div style="font-size:0.85rem;color:#e2e8f0">${msg.content}</div>
        <div style="font-size:0.65rem;color:#64748b;margin-top:4px">${msg.tokens} tokens${msg.latencyMs ? ` • ${msg.latencyMs.toFixed(0)}ms` : ''}</div>
      </div>
    </div>`;
  }

  private renderStatCards(tokens: number, latency: number): string {
    return [
      { label: 'Tokens', value: `${tokens}`, color: '#60a5fa' },
      { label: 'Avg Latency', value: `${latency.toFixed(0)}ms`, color: '#22d3ee' },
      { label: 'Memory', value: `${this.memoryUsageMb.toFixed(0)}MB`, color: '#a78bfa' },
      { label: 'Messages', value: `${this.messages.length}`, color: '#f59e0b' },
    ].map(c => `<div style="background:#1a1f36;border-radius:8px;padding:10px;border-left:3px solid ${c.color}">
      <div style="font-size:1rem;font-weight:700;color:${c.color}">${c.value}</div>
      <div style="font-size:0.65rem;color:#64748b">${c.label}</div>
    </div>`).join('');
  }
}

export { BrowserAIChat, ChatMessage, ModelOption };
