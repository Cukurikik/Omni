// @omni-layer Interface | @omni-source lucidrains/coconut-pytorch | @omni-lang TypeScript
// @omni-description Thought Chain Debugger UI: interactive visualization for
// continuous thought token states and reasoning paths.

interface ThoughtState {
  depth: number;
  score: number;
  reasoning_type: string;
  embedding_norm: number;
  parent_idx: number;
}

interface ThoughtChainView {
  chain_id: string;
  thoughts: ThoughtState[];
  best_path: number[];
  status: string;
}

class ThoughtChainDebugger {
  private container: HTMLElement | null;

  constructor(containerId: string) {
    this.container = document.getElementById(containerId);
  }

  render(chain: ThoughtChainView): void {
    if (!this.container) return;
    const maxScore = Math.max(...chain.thoughts.map(t => t.score), 1);
    const pathSet = new Set(chain.best_path);
    const nodesHTML = chain.thoughts.map((t, i) => {
      const isOnPath = pathSet.has(i);
      const intensity = t.score / maxScore;
      const bg = isOnPath
        ? `rgba(88,166,255,${0.3 + intensity * 0.7})`
        : `rgba(100,100,100,${0.2 + intensity * 0.3})`;
      return `<div style="display:inline-block;margin:4px;padding:8px 12px;background:${bg};border-radius:8px;border:${isOnPath ? '2px solid #58a6ff' : '1px solid #333'};font-size:0.8rem">
        <div><strong>D${t.depth}</strong> | ${t.reasoning_type}</div>
        <div style="opacity:0.7">Score: ${t.score.toFixed(3)} | Norm: ${t.embedding_norm.toFixed(2)}</div>
      </div>`;
    }).join('');

    this.container.innerHTML = `
      <div style="background:#0d1117;padding:1.5rem;border-radius:12px;color:#c9d1d9">
        <h3 style="color:#58a6ff;margin-bottom:1rem">🧠 Chain: ${chain.chain_id} [${chain.status}]</h3>
        <div style="display:flex;flex-wrap:wrap;gap:4px">${nodesHTML}</div>
        <div style="margin-top:1rem;font-size:0.8rem;opacity:0.6">
          Best path: ${chain.best_path.join(' → ')} | Thoughts: ${chain.thoughts.length}
        </div>
      </div>`;
  }
}

export { ThoughtChainDebugger };
export type { ThoughtState, ThoughtChainView };
