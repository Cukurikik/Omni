from typing import Any

class OmniResult:
    def __init__(self, value: Any, error: str = None):
        self.value = value
        self.error = error
        self.is_ok = error is None

class LLMEnvSimulator:
    def __init__(self, state_space: int, action_space: int):
        self.state_space = state_space
        self.action_space = action_space
        self.current_step = 0

    def step(self, action: int) -> OmniResult:
        if action < 0 or action >= self.action_space:
            return OmniResult(None, "Action out of bounds")
            
        try:
            # Deterministic mathematical state transition
            self.current_step += 1
            new_state = (action * 31 + self.current_step) % self.state_space
            reward = 1.0 if new_state == 0 else -0.1
            done = self.current_step >= 100
            
            return OmniResult({
                "next_state": new_state,
                "reward": reward,
                "done": done
            })
        except Exception as e:
            return OmniResult(None, str(e))
