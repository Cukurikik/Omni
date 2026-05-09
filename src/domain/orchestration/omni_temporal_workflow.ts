import { proxyActivities, defineSignal, setHandler, sleep } from '@temporalio/workflow';
import type * as activities from './omni_activities';

// OMNI Business Layer: Temporal SDK Workflow for Distributed Transformer Training
// Manages the long-running training loop, fault tolerance, and cluster orchestration.

const { provisionGpuNodes, executeEpoch, aggregateGradients, teardownCluster } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 hour',
  retry: {
    initialInterval: '1 minute',
    backoffCoefficient: 2.0,
    maximumAttempts: 5,
  },
});

export const pauseTrainingSignal = defineSignal('pauseTraining');
export const resumeTrainingSignal = defineSignal('resumeTraining');

export async function OmniDistributedTrainingWorkflow(
  modelId: string,
  totalEpochs: number,
  clusterSize: number
): Promise<string> {
  let isPaused = false;
  
  setHandler(pauseTrainingSignal, () => {
    isPaused = true;
  });
  
  setHandler(resumeTrainingSignal, () => {
    isPaused = false;
  });

  // Step 1: Provision
  const clusterId = await provisionGpuNodes(clusterSize);
  
  try {
    for (let epoch = 1; epoch <= totalEpochs; epoch++) {
      // Handle interactive pausing
      while (isPaused) {
        await sleep('10 seconds');
      }

      // Step 2: Distributed Map-Reduce execution
      const metrics = await executeEpoch(modelId, clusterId, epoch);
      
      // Step 3: Gradient synchronization across ring topology
      await aggregateGradients(modelId, clusterId);
      
      if (metrics.loss < 0.001) {
        break; // Early convergence
      }
    }
  } finally {
    // Step 4: Guaranteed Teardown
    await teardownCluster(clusterId);
  }

  return `Training for ${modelId} complete.`;
}
