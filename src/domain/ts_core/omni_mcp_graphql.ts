// Omni MCP GraphQL Query Types (TypeScript)
// Ref: ErickWendel/erickwendel-contributions-mcp — MIT
export interface MCPToolInput { name: string; type: string; required: boolean; }
export interface MCPToolDef { name: string; description: string; inputs: MCPToolInput[]; }
export interface MCPCallResult { tool: string; result: any; error?: string; }

export function buildGraphQLSchema(tools: MCPToolDef[]): string {
  const types = tools.map(t => {
    const args = t.inputs.map(i => `${i.name}: ${i.type}${i.required ? '!' : ''}`).join(', ');
    return `  ${t.name}(${args}): JSON`;
  }).join('\n');
  return `type Query {\n${types}\n}`;
}

export function validateToolCall(def: MCPToolDef, args: Record<string, any>): { valid: boolean; missing: string[] } {
  const missing = def.inputs.filter(i => i.required && !(i.name in args)).map(i => i.name);
  return { valid: missing.length === 0, missing };
}
