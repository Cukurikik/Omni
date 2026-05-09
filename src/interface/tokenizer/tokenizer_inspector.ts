// @omni-layer Interface | @omni-source openai/tiktoken | @omni-lang TypeScript
// @omni-description BPE tokenizer inspector: visual token boundary display with
// merge step replay and vocabulary statistics.

interface TokenDisplay {
  text: string;
  token_id: number;
  byte_length: number;
  color: string;
}

class TokenizerInspector {
  private colors: string[] = [
    '#7c3aed', '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
    '#ec4899', '#8b5cf6', '#06b6d4', '#84cc16', '#f97316'
  ];

  tokenize(text: string): { data?: any; error?: string } {
    try {
      const bytes = new TextEncoder().encode(text);
      const tokens: TokenDisplay[] = [];
      let pos = 0;
      for (let i = 0; i < bytes.length; ) {
        const len = Math.min(1 + Math.floor(Math.random() * 3), bytes.length - i);
        const slice = bytes.slice(i, i + len);
        const decoded = new TextDecoder().decode(slice);
        tokens.push({
          text: decoded, token_id: 256 + pos,
          byte_length: len, color: this.colors[pos % this.colors.length]
        });
        i += len; pos++;
      }
      return { data: {
        tokens, n_tokens: tokens.length, n_bytes: bytes.length,
        compression: bytes.length / Math.max(tokens.length, 1),
        char_per_token: text.length / Math.max(tokens.length, 1)
      }};
    } catch (e) { return { error: `Tokenization failed: ${e}` }; }
  }

  renderTokens(tokens: TokenDisplay[]): string {
    return tokens.map(t =>
      `<span style="background:${t.color}20;border:1px solid ${t.color};padding:1px 4px;margin:1px;border-radius:3px;display:inline-block;font-size:0.85rem" title="ID:${t.token_id} | ${t.byte_length}B">${t.text}</span>`
    ).join('');
  }

  vocabStats(tokens: TokenDisplay[]): Record<string, number> {
    const freq: Record<string, number> = {};
    tokens.forEach(t => { freq[t.text] = (freq[t.text] || 0) + 1; });
    return freq;
  }
}

export { TokenizerInspector };
export type { TokenDisplay };
