"""
OMNI Compute Layer - Multi-Agent Streamlit UI
Load balancing and agent orchestration.
"""
from typing import Dict, Any, List

class AgentNode:
    def __init__(self, agent_id: str, capacity: int):
        self.agent_id = agent_id
        self.capacity = capacity
        self.load = 0

class AgentOrchestrator:
    def __init__(self):
        self.nodes: Dict[str, AgentNode] = {}

    def register_node(self, agent_id: str, capacity: int) -> None:
        if agent_id not in self.nodes:
            self.nodes[agent_id] = AgentNode(agent_id, capacity)

    async def distribute_task(self, task_id: str, weight: int) -> str:
        # Least loaded node (min-heap logic)
        available_nodes = [n for n in self.nodes.values() if n.load + weight <= n.capacity]
        if not available_nodes:
            raise SystemError("No available agent capacity for task distribution")
        
        selected = min(available_nodes, key=lambda x: x.load)
        selected.load += weight
        return selected.agent_id
