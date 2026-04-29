// Omni Rubra Tool Registry (TypeScript)
// Domain Layer: Type-safe tool registration for function-calling LLMs.
// Ref: rubra-ai/rubra
interface ToolSchema { name: string; params: Record<string, string>; description: string; }
const registry = new Map<string, ToolSchema>();
export function registerTool(schema: ToolSchema): boolean {
  if (registry.has(schema.name)) return false;
  registry.set(schema.name, schema);
  return true;
}
export function lookupTool(name: string): ToolSchema | undefined { return registry.get(name); }
export function listTools(): string[] { return Array.from(registry.keys()); }
