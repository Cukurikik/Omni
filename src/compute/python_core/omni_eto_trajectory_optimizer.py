# Omni ETO Trajectory Optimizer (Python)
# Compute Layer: Exploration-based trajectory optimization for LLM agents.
# Ref: Yifan-Song793/ETO — ACL 2024, Trial and Error.

from typing import List, Dict, Tuple, Optional
import math

class TrajectoryStep:
    __slots__ = ('action', 'observation', 'reward', 'cumulative')
    def __init__(self, action: str, observation: str, reward: float):
        self.action = action
        self.observation = observation
        self.reward = reward
        self.cumulative = 0.0

def compute_trajectory_return(steps: List[TrajectoryStep], gamma: float = 0.99) -> float:
    if not steps:
        return 0.0
    G = 0.0
    for i in range(len(steps) - 1, -1, -1):
        G = steps[i].reward + gamma * G
        steps[i].cumulative = round(G, 8)
    return steps[0].cumulative

def rank_trajectories(trajectories: List[List[TrajectoryStep]], gamma: float = 0.99) -> List[Tuple[int, float]]:
    scored: List[Tuple[int, float]] = []
    for idx, traj in enumerate(trajectories):
        ret = compute_trajectory_return(traj, gamma)
        scored.append((idx, ret))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored

def select_contrastive_pairs(
    ranked: List[Tuple[int, float]], top_k: int = 3
) -> List[Tuple[int, int]]:
    if len(ranked) < 2:
        return []
    pairs: List[Tuple[int, int]] = []
    for i in range(min(top_k, len(ranked))):
        for j in range(max(0, len(ranked) - top_k), len(ranked)):
            if ranked[i][0] != ranked[j][0]:
                pairs.append((ranked[i][0], ranked[j][0]))
    return pairs
