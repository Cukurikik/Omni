// @omni-layer Interface | @omni-lang TypeScript | @omni-batch 18 | @omni-semester 16
// @omni-repo avikumart/LLM-GenAI + Nicolepcx/Transformers-in-Action
// @omni-description Transformer playground dashboard: TypeScript UI for
// interactive transformer visualization, attention heatmaps, and token analysis.

interface TokenInfo {
  id: number;
  text: string;
  position: number;
  embedding: number[];
}

interface AttentionHead {
  headIdx: number;
  layerIdx: number;
  weights: number[][];
}

interface TransformerVizState {
  tokens: TokenInfo[];
  attentionHeads: AttentionHead[];
  selectedLayer: number;
  selectedHead: number;
  highlightedToken: number | null;
}

class TransformerPlayground {
  private state: TransformerVizState;
  private readonly maxLayers = 12;
  private readonly maxHeads = 12;

  constructor() {
    this.state = {
      tokens: [],
      attentionHeads: [],
      selectedLayer: 0,
      selectedHead: 0,
      highlightedToken: null,
    };
  }

  tokenize(text: string): TokenInfo[] {
    const words = text.split(/\s+/).filter(w => w.length > 0);
    this.state.tokens = words.map((w, i) => ({
      id: this.hashToken(w),
      text: w,
      position: i,
      embedding: this.computeEmbedding(w, i),
    }));
    this.computeAttention();
    return this.state.tokens;
  }

  private hashToken(word: string): number {
    let h = 0;
    for (let i = 0; i < word.length; i++) {
      h = ((h << 5) - h + word.charCodeAt(i)) | 0;
    }
    return Math.abs(h) % 32000;
  }

  private computeEmbedding(word: string, pos: number): number[] {
    const dim = 64;
    const emb = new Array(dim).fill(0);
    for (let d = 0; d < dim; d++) {
      emb[d] = Math.sin(this.hashToken(word) * 0.001 * (d + 1))
             + Math.cos(pos * 0.01 * (d + 1)) * 0.5;
    }
    const norm = Math.sqrt(emb.reduce((s, v) => s + v * v, 0)) + 1e-10;
    return emb.map(v => v / norm);
  }

  private computeAttention(): void {
    const n = this.state.tokens.length;
    this.state.attentionHeads = [];
    for (let layer = 0; layer < this.maxLayers; layer++) {
      for (let head = 0; head < this.maxHeads; head++) {
        const weights: number[][] = [];
        for (let i = 0; i < n; i++) {
          const row: number[] = [];
          for (let j = 0; j < n; j++) {
            const dot = this.state.tokens[i].embedding
              .slice(0, 8)
              .reduce((s, v, k) => s + v * (this.state.tokens[j].embedding[k] || 0), 0);
            row.push(dot * (1 + layer * 0.1) * (1 + head * 0.05));
          }
          const maxR = Math.max(...row);
          const exps = row.map(v => Math.exp(v - maxR));
          const sumE = exps.reduce((a, b) => a + b, 0) + 1e-10;
          weights.push(exps.map(e => e / sumE));
        }
        this.state.attentionHeads.push({ headIdx: head, layerIdx: layer, weights });
      }
    }
  }

  getAttentionWeights(layer: number, head: number): number[][] | null {
    const found = this.state.attentionHeads.find(
      h => h.layerIdx === layer && h.headIdx === head
    );
    return found?.weights ?? null;
  }

  getTokenImportance(tokenIdx: number): number[] {
    const layers: number[] = [];
    for (let l = 0; l < this.maxLayers; l++) {
      const weights = this.getAttentionWeights(l, 0);
      if (weights && tokenIdx < weights.length) {
        const avgAttn = weights.reduce((s, row) => s + (row[tokenIdx] || 0), 0) / weights.length;
        layers.push(avgAttn);
      }
    }
    return layers;
  }

  getState(): TransformerVizState {
    return { ...this.state };
  }
}

export { TransformerPlayground, TokenInfo, AttentionHead, TransformerVizState };
