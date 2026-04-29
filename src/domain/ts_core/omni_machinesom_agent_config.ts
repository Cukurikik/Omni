// Omni MachineSoM Agent Config (TypeScript)
// Domain: Multi-agent collaboration configuration.
// Ref: zjunlp/MachineSoM — ACL 2024
type SoMStrategy = 'debate' | 'majority_vote' | 'reflection' | 'dictator';
interface AgentConfig { id: string; model: string; role: string; strategy: SoMStrategy; }
export function validateConfig(agents: AgentConfig[]): boolean {
  const ids = new Set(agents.map(a => a.id));
  return ids.size === agents.length && agents.every(a => a.model.length > 0);
}
export function selectLeader(agents: AgentConfig[]): AgentConfig | undefined {
  return agents.find(a => a.role === 'leader') || agents[0];
}
