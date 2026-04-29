// Omni ToolEmu Dashboard (TypeScript)
export interface ToolRisk { tool: string; score: number; level: string; flags: string[] }
export function assessRisk(tool: string, action: string, args: string[]): ToolRisk {
  let score = 0; const flags: string[] = [];
  const dangerous: Record<string,number> = {delete:0.9,write:0.6,execute:0.8,send:0.5};
  for (const [k,v] of Object.entries(dangerous)) if (action.toLowerCase().includes(k)) { score = Math.max(score,v); flags.push(k); }
  return {tool, score: Math.round(score*1e4)/1e4, level: score>0.7?'critical':score>0.4?'high':'low', flags};
}
