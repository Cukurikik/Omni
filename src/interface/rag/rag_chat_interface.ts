// @omni-layer Interface | @omni-source run-llama/llama_index | @omni-lang TypeScript
// @omni-description RAG chat interface: document Q&A with source citations,
// retrieval scores, and context window visualization.

interface Citation { doc_id: string; text: string; score: number; }
interface RAGResponse { answer: string; citations: Citation[]; context_tokens: number; latency_ms: number; }

class RAGChatInterface {
  private history: { role: string; content: string; citations?: Citation[] }[] = [];

  addMessage(role: string, content: string, citations?: Citation[]): void {
    this.history.push({ role, content, citations });
  }

  renderChat(): string {
    return this.history.map(msg => {
      const isUser = msg.role === 'user';
      const bg = isUser ? '#1e3a5f' : '#1a1a2e';
      const citHTML = msg.citations?.map(c =>
        `<div style="background:#0d1117;padding:4px 8px;border-radius:4px;margin:2px 0;font-size:0.7rem;border-left:3px solid #7c3aed">
          <strong>${c.doc_id}</strong> (${(c.score*100).toFixed(0)}%) — ${c.text.slice(0,80)}...
        </div>`
      ).join('') || '';
      return `<div style="background:${bg};padding:1rem;border-radius:8px;margin:4px 0">
        <div style="font-size:0.7rem;opacity:0.5;margin-bottom:4px">${msg.role.toUpperCase()}</div>
        <div>${msg.content}</div>
        ${citHTML ? `<div style="margin-top:8px">${citHTML}</div>` : ''}
      </div>`;
    }).join('');
  }

  renderSourcePanel(citations: Citation[]): string {
    const sorted = [...citations].sort((a, b) => b.score - a.score);
    return sorted.map((c, i) => {
      const barWidth = Math.round(c.score * 100);
      return `<div style="margin:4px 0">
        <div style="display:flex;align-items:center;gap:8px">
          <span style="width:20px;font-size:0.75rem">#${i+1}</span>
          <div style="flex:1;background:#1e1e2e;height:12px;border-radius:3px">
            <div style="width:${barWidth}%;height:100%;background:#7c3aed;border-radius:3px"></div>
          </div>
          <span style="width:40px;font-size:0.7rem">${barWidth}%</span>
        </div>
        <div style="font-size:0.7rem;opacity:0.6;margin-left:28px">${c.doc_id}</div>
      </div>`;
    }).join('');
  }
}

export { RAGChatInterface };
export type { Citation, RAGResponse };
