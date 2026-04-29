import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';

// Omni Temporal MCP Contribution Workflow
// Enforces Saga patterns for cross-platform model context synchronization.

const { fetchContributions } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
});

export async function OmniMCPWorkflow(developerId: string): Promise<string> {
  if (!developerId) {
    throw new Error("Developer ID must be provided");
  }

  try {
    // Deterministic workflow execution
    const result = await fetchContributions(developerId);
    return `Workflow Complete: ${result}`;
  } catch (err: any) {
    throw new Error(`Workflow failed: ${err.message}`);
  }
}
