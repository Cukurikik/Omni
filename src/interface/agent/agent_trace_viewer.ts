// @omni-layer Interface | @omni-source langchain-ai/langchain | @omni-lang TypeScript
// @omni-description Agent trace viewer: step-by-step ReAct reasoning visualization
// with tool usage, thought bubbles, and execution timeline.

interface AgentStep { step: number; thought: string; tool: string; input: string; observation: string; duration_ms: number; }
interface AgentTrace { query: string; steps: AgentStep[]; final_answer: string; total_ms: number; }

class AgentTraceViewer {
  render(trace: AgentTrace): string {
    const stepsHTML = trace.steps.map(s => {
      const toolColor = s.tool === 'final_answer' ? '#10b981' : '#7c3aed';
      return `<div style="display:flex;gap:12px;margin:8px 0">
        <div style="display:flex;flex-direction:column;align-items:center;width:30px">
          <div style="width:24px;height:24px;border-radius:50%;background:${toolColor};display:flex;align-items:center;justify-content:center;font-size:0.7rem;font-weight:700">${s.step + 1}</div>
          <div style="width:2px;flex:1;background:#333;margin-top:4px"></div>
        </div>
        <div style="flex:1;background:#161b22;padding:12px;border-radius:8px;border:1px solid rgba(255,255,255,0.05)">
          <div style="font-size:0.75rem;color:#7c3aed;margin-bottom:4px">💭 ${s.thought}</div>
          <div style="font-size:0.8rem;margin:4px 0">🔧 <code style="background:#0d1117;padding:2px 6px;border-radius:3px">${s.tool}</code></div>
          <div style="font-size:0.75rem;opacity:0.6">📝 ${s.observation.slice(0, 100)}</div>
          <div style="font-size:0.65rem;opacity:0.4;margin-top:4px">${s.duration_ms}ms</div>
        </div>
      </div>`;
    }).join('');

    return `<div style="background:#0d1117;padding:1.5rem;border-radius:12px;color:#c9d1d9;max-width:600px">
      <h3 style="color:#7c3aed;margin-bottom:4px">🤖 Agent Trace</h3>
      <div style="font-size:0.8rem;opacity:0.6;margin-bottom:1rem">Q: ${trace.query}</div>
      ${stepsHTML}
      <div style="background:#10b98120;padding:12px;border-radius:8px;border:1px solid #10b981;margin-top:8px">
        <div style="font-size:0.75rem;color:#10b981;margin-bottom:4px">✅ Final Answer</div>
        <div>${trace.final_answer}</div>
        <div style="font-size:0.65rem;opacity:0.4;margin-top:4px">Total: ${trace.total_ms}ms | Steps: ${trace.steps.length}</div>
      </div>
    </div>`;
  }
}

export { AgentTraceViewer };
export type { AgentStep, AgentTrace };
