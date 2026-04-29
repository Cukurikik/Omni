"""
OMNI MetaGPT Software Team Engine
Role-based finite state machine transitions for autonomous team workflows.
"""
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result, Ok, Err

class OmniMetaGPTSoftwareTeamEngine(OmniBaseEngine):
    def __init__(self):
        super().__init__()
        self.valid_roles = ["ProductManager", "Architect", "Engineer", "QA"]
        self.state_matrix = {
            "ProductManager": ["Architect"],
            "Architect": ["Engineer"],
            "Engineer": ["QA", "Engineer"],
            "QA": ["ProductManager", "Done"]
        }

    def process(self, execution_trace: List[str]) -> Result[bool, str]:
        if not execution_trace:
            return Err("Execution trace is empty.")
            
        try:
            if execution_trace[-1] != "Done":
                return Err("Trace must terminate at 'Done' state.")
                
            if execution_trace[0] != "ProductManager":
                return Err("Trace must begin at 'ProductManager'.")
                
            for i in range(len(execution_trace) - 1):
                current = execution_trace[i]
                next_node = execution_trace[i+1]
                
                if current not in self.state_matrix:
                    return Err(f"Invalid state: {current}")
                    
                if next_node not in self.state_matrix[current]:
                    return Err(f"Invalid transition from {current} to {next_node}")
                    
            return Ok(True)
        except Exception as e:
            return Err(f"FSM verification failed: {str(e)}")

    def diagnostics(self) -> Result[Dict[str, Any], str]:
        trace = ["ProductManager", "Architect", "Engineer", "QA", "Done"]
        res = self.process(trace)
        if hasattr(res, 'is_ok') and res.is_ok():
            return Ok({"status": "healthy", "fsm_nodes": len(self.valid_roles)})
        return Err("Diagnostics failed on MetaGPT engine.")
