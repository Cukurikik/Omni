"""
@omni-layer Compute | @omni-source lucidrains/improving-transformers-world-model-for-rl
@omni-description World model RL engine: model-based reinforcement learning
with transformer dynamics, reward prediction, and value estimation.
@omni-lang Python | @omni-batch 17 | @omni-semester 16
"""
import math
from typing import List, Dict

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniWorldModelRL:
    def __init__(self, d_state=64, d_action=8, n_layers=4, gamma=0.99):
        self.d_state = d_state; self.d_action = d_action
        self.n_layers = n_layers; self.gamma = gamma
        self.replay: List[Dict] = []

    def dynamics_model(self, state: List[float], action: List[float]) -> List[float]:
        next_state = [0.0]*self.d_state
        for i in range(self.d_state):
            s = state[i] if i < len(state) else 0
            a = action[i % len(action)] if action else 0
            next_state[i] = math.tanh(s * 0.8 + a * 0.3 + math.sin(i*0.1)*0.1)
        return next_state

    def reward_predictor(self, state: List[float], action: List[float]) -> float:
        combined = sum(state[i]*action[i % len(action)] for i in range(min(len(state), 32)))
        return math.tanh(combined)

    def value_estimator(self, state: List[float]) -> float:
        return sum(math.tanh(s) for s in state) / max(len(state), 1) * 10.0

    def imagine_trajectory(self, initial_state: List[float], actions: List[List[float]], horizon: int = 15) -> OmniResult:
        try:
            states = [initial_state]; rewards = []; values = []
            state = initial_state
            for t in range(min(horizon, len(actions))):
                action = actions[t]
                reward = self.reward_predictor(state, action)
                state = self.dynamics_model(state, action)
                value = self.value_estimator(state)
                states.append(state); rewards.append(reward); values.append(value)
            returns = [0.0]*len(rewards)
            g = 0
            for t in reversed(range(len(rewards))):
                g = rewards[t] + self.gamma * g
                returns[t] = g
            return OmniResult(data={"n_steps": len(rewards), "total_reward": sum(rewards), "final_value": values[-1] if values else 0, "discounted_return": returns[0] if returns else 0, "avg_reward": sum(rewards)/max(len(rewards),1)})
        except Exception as e: return OmniResult(error=e)

    def store_experience(self, state, action, reward, next_state) -> OmniResult:
        self.replay.append({"s": state, "a": action, "r": reward, "ns": next_state})
        return OmniResult(data={"buffer_size": len(self.replay)})
