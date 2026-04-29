// Omni ETO Trajectory Scorer (TypeScript)
// Domain Layer: Contrastive trajectory ranking for LLM agent optimization.
// Ref: Yifan-Song793/ETO — ACL 2024

interface Trajectory { actions: string[]; rewards: number[]; }

export function computeReturn(rewards: number[], gamma: number = 0.99): number {
  let G = 0;
  for (let i = rewards.length - 1; i >= 0; i--) {
    G = rewards[i] + gamma * G;
  }
  return Math.round(G * 1e8) / 1e8;
}

export function rankTrajectories(trajs: Trajectory[], gamma: number = 0.99): { idx: number; ret: number }[] {
  const scored = trajs.map((t, idx) => ({ idx, ret: computeReturn(t.rewards, gamma) }));
  scored.sort((a, b) => b.ret - a.ret);
  return scored;
}
