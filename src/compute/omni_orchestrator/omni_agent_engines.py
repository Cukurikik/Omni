"""
@omni-domain Compute Layer (Agent Orchestration)
@omni-source various/agent-frameworks
@omni-description Omni Agent Engines mimicking multi-agent task orchestration.
@omni-requirement zero-mock, monadic-error
"""
from typing import Any, Optional, List, Dict

class OmniResult:
    def __init__(self, data=None, error=None):
        self.data = data
        self.error = error
    def is_ok(self): return self.error is None

class AgentError(Exception): pass

class OmniAgentEngines:
    def __init__(self):
        self.agents = {}
        self.task_queue = []

    def register_agent(self, agent_id: str, capabilities: List[str]) -> OmniResult:
        try:
            if not agent_id:
                return OmniResult(error=AgentError("Agent ID empty."))
            self.agents[agent_id] = {"capabilities": capabilities, "status": "idle", "tasks_completed": 0}
            return OmniResult(data=True)
        except Exception as e:
            return OmniResult(error=AgentError(f"Registration failed: {e}"))

    def submit_task(self, task_id: str, required_capability: str, payload: Dict) -> OmniResult:
        try:
            if not task_id:
                return OmniResult(error=AgentError("Task ID empty."))
            self.task_queue.append({"task_id": task_id, "capability": required_capability, "payload": payload, "status": "pending"})
            return OmniResult(data={"queued": True, "position": len(self.task_queue)})
        except Exception as e:
            return OmniResult(error=AgentError(f"Task submission failed: {e}"))

    def dispatch_next(self) -> OmniResult:
        try:
            pending = [t for t in self.task_queue if t["status"] == "pending"]
            if not pending:
                return OmniResult(data={"dispatched": False, "reason": "No pending tasks."})
            task = pending[0]
            for aid, agent in self.agents.items():
                if agent["status"] == "idle" and task["capability"] in agent["capabilities"]:
                    agent["status"] = "busy"
                    task["status"] = "running"
                    task["assigned_to"] = aid
                    return OmniResult(data={"dispatched": True, "task_id": task["task_id"], "agent": aid})
            return OmniResult(data={"dispatched": False, "reason": "No available agent."})
        except Exception as e:
            return OmniResult(error=AgentError(f"Dispatch failed: {e}"))
