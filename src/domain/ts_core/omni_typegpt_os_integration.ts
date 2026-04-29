// Omni TypeGPT OS Integration (TypeScript)
// Domain Layer: LLM integration into desktop OS workflows.
// Ref: olyaiy/TypeGPT — Integrate LLMs into your OS.
interface TypeGPTRequest { prefix: string; suffix: string; model: string; maxTokens: number; }
interface TypeGPTResponse { completion: string; tokensUsed: number; latencyMs: number; }
export function buildRequest(prefix: string, suffix: string, model: string = 'default'): TypeGPTRequest {
  return { prefix, suffix, model, maxTokens: Math.min(4096, Math.max(1, prefix.length + suffix.length)) };
}
export function validateResponse(res: TypeGPTResponse): boolean {
  return res.completion.length > 0 && res.tokensUsed > 0 && res.latencyMs >= 0;
}
