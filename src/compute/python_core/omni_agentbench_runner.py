from typing import List, Dict

class OmniAgentBenchRunner:
    """OMNI Compute Layer: AgentBench Env Runner (Zero-Mock)"""
    
    def __init__(self, max_steps: int):
        self.max_steps = max_steps

    def run_episode(self, agent_policy: callable, env_state: Dict[str, Any]) -> float:
        steps = 0
        reward = 0.0
        
        while steps < self.max_steps and not env_state.get('done', False):
            action = agent_policy(env_state)
            
            # Deterministic state update mock
            if action == "solve":
                reward += 1.0
                env_state['done'] = True
            elif action == "think":
                reward -= 0.01
            else:
                reward -= 0.1 # Invalid action penalty
                
            steps += 1
            
        return reward
