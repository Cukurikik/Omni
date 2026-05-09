// @omni-layer Interface | @omni-source sgrvinod/chess-transformers | @omni-lang TypeScript
// @omni-description Chess analysis board: interactive board with move arrows,
// evaluation bar, and engine suggestion display.

interface ChessMove {
  from: string;
  to: string;
  confidence: number;
  isCapture: boolean;
  isPromotion: boolean;
}

interface PositionEval {
  materialScore: number;
  centerControl: number;
  evaluation: number;
}

class ChessAnalysisBoard {
  private container: HTMLElement;
  private position: string[][] = [];
  private suggestedMoves: ChessMove[] = [];
  private evaluation: PositionEval | null = null;

  constructor(containerId: string) {
    const el = document.getElementById(containerId);
    if (!el) throw new Error(`Container ${containerId} not found`);
    this.container = el;
    this.initPosition();
  }

  private initPosition(): void {
    this.position = [
      ['♜','♞','♝','♛','♚','♝','♞','♜'],
      ['♟','♟','♟','♟','♟','♟','♟','♟'],
      ['','','','','','','',''],
      ['','','','','','','',''],
      ['','','','','','','',''],
      ['','','','','','','',''],
      ['♙','♙','♙','♙','♙','♙','♙','♙'],
      ['♖','♘','♗','♕','♔','♗','♘','♖']
    ];
    this.render();
  }

  setSuggestions(moves: ChessMove[]): void {
    this.suggestedMoves = moves.sort((a, b) => b.confidence - a.confidence);
    this.render();
  }

  setEvaluation(eval_: PositionEval): void {
    this.evaluation = eval_;
    this.render();
  }

  private render(): void {
    this.container.innerHTML = `
      <div style="display:grid;grid-template-columns:auto 40px 280px;gap:16px;align-items:start">
        <div style="background:#1a1f36;border-radius:12px;padding:16px">
          <div style="display:grid;grid-template-columns:repeat(8,48px);grid-template-rows:repeat(8,48px);border-radius:6px;overflow:hidden">
            ${this.renderBoard()}
          </div>
          <div style="display:flex;justify-content:center;gap:2px;margin-top:4px">
            ${'abcdefgh'.split('').map(f => `<div style="width:48px;text-align:center;font-size:0.7rem;color:#64748b">${f}</div>`).join('')}
          </div>
        </div>
        <div style="background:#1a1f36;border-radius:8px;height:384px;width:24px;position:relative;overflow:hidden">
          ${this.renderEvalBar()}
        </div>
        <div style="display:flex;flex-direction:column;gap:12px">
          <div style="background:#1a1f36;border-radius:10px;padding:14px">
            <h4 style="color:#93c5fd;font-size:0.85rem;margin-bottom:10px">🤖 Engine Suggestions</h4>
            ${this.renderSuggestions()}
          </div>
          ${this.evaluation ? this.renderEvalStats() : ''}
        </div>
      </div>`;
  }

  private renderBoard(): string {
    let html = '';
    for (let r = 0; r < 8; r++) {
      for (let f = 0; f < 8; f++) {
        const isLight = (r + f) % 2 === 0;
        const bg = isLight ? '#b58863' : '#f0d9b5';
        const piece = this.position[r][f];
        html += `<div style="background:${bg};display:flex;align-items:center;justify-content:center;font-size:1.8rem;cursor:pointer">${piece}</div>`;
      }
    }
    return html;
  }

  private renderEvalBar(): string {
    if (!this.evaluation) return '<div style="height:50%;background:#e2e8f0"></div>';
    const pct = Math.max(5, Math.min(95, 50 + this.evaluation.evaluation * 5));
    return `<div style="position:absolute;bottom:0;width:100%;height:${pct}%;background:#e2e8f0;transition:height 0.5s"></div>
            <div style="position:absolute;top:0;width:100%;height:${100-pct}%;background:#1e293b"></div>`;
  }

  private renderSuggestions(): string {
    if (!this.suggestedMoves.length) return '<div style="color:#64748b;font-size:0.8rem">No suggestions</div>';
    return this.suggestedMoves.slice(0, 5).map((m, i) => {
      const pct = (m.confidence * 100).toFixed(1);
      return `<div style="display:flex;align-items:center;gap:8px;padding:6px 8px;background:#0a0e17;border-radius:6px;margin:3px 0;font-size:0.85rem">
        <span style="color:${i===0?'#60a5fa':'#94a3b8'};font-weight:700;width:20px">${i+1}.</span>
        <span style="font-weight:600">${m.from}${m.isCapture?'x':'→'}${m.to}</span>
        ${m.isPromotion ? '<span style="color:#f59e0b;font-size:0.7rem">♛</span>' : ''}
        <span style="margin-left:auto;color:#60a5fa;font-size:0.8rem">${pct}%</span>
      </div>`;
    }).join('');
  }

  private renderEvalStats(): string {
    if (!this.evaluation) return '';
    return `<div style="background:#1a1f36;border-radius:10px;padding:14px">
      <h4 style="color:#93c5fd;font-size:0.85rem;margin-bottom:10px">📊 Position</h4>
      <div style="font-size:0.8rem">
        <div style="display:flex;justify-content:space-between;padding:3px 0"><span style="color:#94a3b8">Material</span><span style="color:#60a5fa">${this.evaluation.materialScore.toFixed(2)}</span></div>
        <div style="display:flex;justify-content:space-between;padding:3px 0"><span style="color:#94a3b8">Center</span><span style="color:#a78bfa">${this.evaluation.centerControl.toFixed(2)}</span></div>
        <div style="display:flex;justify-content:space-between;padding:3px 0"><span style="color:#94a3b8">Eval</span><span style="color:#22d3ee;font-weight:700">${this.evaluation.evaluation > 0 ? '+' : ''}${this.evaluation.evaluation.toFixed(2)}</span></div>
      </div>
    </div>`;
  }
}

export { ChessAnalysisBoard, ChessMove, PositionEval };
