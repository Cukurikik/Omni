// Omni LocalLLM ReAct Agent (TypeScript)
// Domain Layer: Guided ReAct agent with structured observation/action loop.
// Ref: QuangBK/localLLM_guidance — Local LLM ReAct Agent.

interface ReActStep { thought: string; action: string; observation: string; }

export function parseReActTrace(raw: string): ReActStep[] {
  const steps: ReActStep[] = [];
  const blocks = raw.split('Thought:').filter(b => b.trim());
  for (const block of blocks) {
    const thoughtMatch = block.split('Action:');
    const thought = (thoughtMatch[0] || '').trim();
    const rest = (thoughtMatch[1] || '');
    const actionMatch = rest.split('Observation:');
    const action = (actionMatch[0] || '').trim();
    const observation = (actionMatch[1] || '').trim();
    if (thought) steps.push({ thought, action, observation });
  }
  return steps;
}

export function validateReActLoop(steps: ReActStep[]): boolean {
  return steps.every(s => s.thought.length > 0 && s.action.length > 0);
}
