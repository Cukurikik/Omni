// Omni Langforge Chain Builder (TypeScript)
// Domain Layer: Deterministic LangChain pipeline composition for deployment.
// Ref: mme/langforge — Toolkit for creating and deploying LangChain apps.

interface ChainStep { name: string; type: 'llm' | 'tool' | 'retriever'; config: Record<string, unknown>; }
interface Pipeline { steps: ChainStep[]; hash: string; }

export function buildPipeline(steps: ChainStep[]): Pipeline {
  if (steps.length === 0) throw new Error('Pipeline must have at least one step');
  let hash = '';
  for (const s of steps) hash += `${s.name}:${s.type};`;
  const encoded = Array.from(new TextEncoder().encode(hash)).reduce((a, b) => ((a << 5) - a + b) | 0, 0);
  return { steps, hash: Math.abs(encoded).toString(16).padStart(8, '0') };
}

export function validateChain(pipeline: Pipeline): boolean {
  const names = new Set<string>();
  for (const s of pipeline.steps) {
    if (names.has(s.name)) return false;
    names.add(s.name);
  }
  return true;
}
