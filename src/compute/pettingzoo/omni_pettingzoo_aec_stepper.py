# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# PettingZoo (OMNI Zero-Mock Implementation)
# Implements Agent Environment Cycle (AEC) turn stepping order mechanics.

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Result:
    value: Optional[str] # Next active agent identifier
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: str) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class AECStepperEngine:
    def __init__(self, agent_order: List[str]):
        self.agent_order = agent_order
        self.current_idx = 0
        self.active_agents = set(agent_order)

    def agent_completed(self, agent_id: str, is_terminated: bool) -> Result:
        """
        Advances the AEC turn counter mathematically accounting for terminated agents sequentially.
        """
        if not self.agent_order:
             return Result.err("Agent list cannot be empty.")
             
        if agent_id not in self.active_agents:
             # Already removed or invalid identifier
             pass
             
        if is_terminated and agent_id in self.active_agents:
             self.active_agents.remove(agent_id)
             
        if not self.active_agents:
             return Result.err("All agents terminated. Cycle closed.")
             
        # Cycle to the next valid agent mathematically
        for _ in range(len(self.agent_order)):
             self.current_idx = (self.current_idx + 1) % len(self.agent_order)
             next_agent = self.agent_order[self.current_idx]
             
             if next_agent in self.active_agents:
                  return Result.ok(next_agent)
                  
        return Result.err("Unreachable execution boundary in AEC stepper.")
