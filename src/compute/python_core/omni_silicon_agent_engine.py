from __future__ import annotations
from src.compute.python_core.omni_base_engine import Result, Ok, Err
from typing import Dict, Any, List, Set

class OmniSiliconAgentEngine:
    """OMNI Zero-Prod Production Implementation for OmniSiliconAgentEngine."""
    
    def __init__(self) -> None:
        self.agent_registry: Dict[str, Dict[str, Any]] = {}
        self.communication_dag: Dict[str, List[str]] = {}
        
    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniSiliconAgentEngine",
            "status": "operational",
            "batch": 51,
            "semester": 11,
            "domain": "DAG State Tracking"
        }
        
    def register_agent(self, agent_id: str, role: str, cpu_budget: float, mem_budget: float) -> Result[bool, Exception]:
        """Registers a silicon sandbox agent with deterministic resource constraints."""
        try:
            if not agent_id or not role:
                return Err(ValueError("Agent identity and role require explicit allocation bounds"))
            if cpu_budget <= 0.0 or mem_budget <= 0.0:
                return Err(ValueError("Resource budgets must exceed 0 for sandbox virtualization"))
                
            self.agent_registry[agent_id] = {
                "role": role,
                "cpu": cpu_budget,
                "mem": mem_budget,
                "state": "IDLE"
            }
            self.communication_dag[agent_id] = []
            return Ok(True)
        except Exception as e:
            return Err(e)

    def attach_communication_edge(self, source_id: str, target_id: str) -> Result[bool, Exception]:
        """Adds a directional edge to the multi-agent DAG. Fails if a cycle is induced."""
        try:
            if source_id not in self.agent_registry or target_id not in self.agent_registry:
                return Err(KeyError("Source or Target node not registered in Silicon Engine"))
                
            self.communication_dag[source_id].append(target_id)
            
            # DFS Cycle Detection
            visited: Set[str] = set()
            recursion_stack: Set[str] = set()
            
            def detect_cycle(node: str) -> bool:
                visited.add(node)
                recursion_stack.add(node)
                for neighbor in self.communication_dag.get(node, []):
                    if neighbor not in visited:
                        if detect_cycle(neighbor):
                            return True
                    elif neighbor in recursion_stack:
                        return True
                recursion_stack.remove(node)
                return False
                
            if detect_cycle(source_id):
                # Rollback structural induction
                self.communication_dag[source_id].remove(target_id)
                return Err(ValueError("Acyclic constraint violated. Sandbox edge rejected."))
                
            return Ok(True)
        except Exception as e:
            return Err(e)
            
    def compute_system_overhead(self) -> Result[Dict[str, float], Exception]:
        """Calculates total bound resource usage across active directed agents."""
        try:
            tc, tm = 0.0, 0.0
            for meta in self.agent_registry.values():
                tc += meta["cpu"]
                tm += meta["mem"]
            return Ok({"total_cpu_cores": tc, "total_memory_gb": tm})
        except Exception as e:
            return Err(e)
