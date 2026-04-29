// OMNI Divine Memory Integration: Inspired by LLMsPracticalGuide
// Business Layer - Temporal SDK Worker binding to local nodes

import { Worker } from '@temporalio/worker';
import * as activities from './activities';

async function run() {
  const worker = await Worker.create({
    workflowsPath: require.resolve('./llm_practical_temporal'),
    activities,
    taskQueue: 'llm-guide-tasks',
    
    // Physical bounds for memory and thread management
    maxConcurrentActivityTaskExecutions: 50,
    maxConcurrentWorkflowTaskExecutions: 20,
  });

  console.log('OMNI Temporal Worker for LLM Guide initialized with strict concurrency bounds.');
  await worker.run();
}

run().catch((err) => {
  console.error("OMNI Error 500: Fatal worker crash.", err);
  process.exit(1);
});
