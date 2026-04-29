// OMNI Divine Memory Integration: Inspired by LLMsPracticalGuide
// Business Layer - Temporal SDK workflow for guided learning paths

import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';

const { fetchGuideData, generateLearningPath } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
});

// Physical boundaries for learning path length
const MAX_PATH_NODES = 20;

export class OmniError extends Error {
  constructor(public code: number, message: string) {
    super(message);
    this.name = 'OmniError';
  }
}

export async function LLMGuideWorkflow(userId: string, targetRole: string): Promise<string[]> {
  const guideData = await fetchGuideData();
  
  if (!guideData || guideData.length === 0) {
    throw new OmniError(404, "Guide dataset physically unavailable.");
  }

  const path = await generateLearningPath(targetRole, guideData);

  if (path.length > MAX_PATH_NODES) {
    throw new OmniError(413, `Path generation exceeded max physical nodes (${MAX_PATH_NODES}).`);
  }

  return path;
}
