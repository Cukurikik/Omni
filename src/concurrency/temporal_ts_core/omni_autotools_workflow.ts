// Omni AutoTools Workflow (Temporal SDK TS)
// Concurrency Layer: Deterministic durable workflow for tool agent trajectory.

import { proxyActivities, sleep } from '@temporalio/workflow';

interface OmniToolActivities {
  validateToolExecution(toolId: string): Promise<boolean>;
}

const { validateToolExecution } = proxyActivities<OmniToolActivities>({
  startToCloseTimeout: '1 minute',
});

export async function OmniAutoToolsOrchestrator(toolId: string): Promise<string> {
  // Temporal workflows MUST be deterministic. No random numbers, no native date calls.
  if (toolId.length === 0) {
    throw new Error("Tool ID must be provided");
  }

  const isValid = await validateToolExecution(toolId);
  if (!isValid) {
    return "TOOL_REJECTED";
  }

  // Deterministic workflow delay
  await sleep('1s');
  
  return "TOOL_EXECUTED_DETERMINISTICALLY";
}
