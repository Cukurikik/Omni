// Omni LLM API Starterkit Server (Deno/Bun)
// Ref: tleers/llm-api-starterkit
const PORT = parseInt(Deno.env.get("PORT") || "8000");
interface GenerateRequest { prompt: string; max_tokens: number; temperature: number; }
function validateRequest(req: GenerateRequest): string | null {
  if (!req.prompt) return "Missing prompt";
  if (req.max_tokens < 1 || req.max_tokens > 4096) return "max_tokens out of range";
  if (req.temperature < 0 || req.temperature > 2) return "temperature out of range";
  return null;
}
function estimateTokens(text: string): number { return Math.max(1, Math.floor(text.length / 4)); }
export { validateRequest, estimateTokens };
