from __future__ import annotations
from typing import Dict, Any, List, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniAgileSprintPlannerEngine:
    """
    omni-agile-sprint-planner
    
    A structural mathematical 0/1 Knapsack matrix engine to optimally allocate Agile
    story points into a maximal sprint boundary metric without overcommit.
    Mimics Elite-Build-Team/move-around.
    """
    
    ENGINE_VERSION = "omni-s11-b4.1.0"
    
    def __init__(self, sprint_capacity: int) -> None:
        """Sets max story-points for the sprint strictly constrained."""
        self.sprint_capacity = sprint_capacity

    def plan_optimal_sprint(self, task_matrix: List[Tuple[str, int, int]]) -> Result:
        """
        Parses exactly formatted task requests and extracts bounded optimum.
        task_matrix: list of (task_name, effort_required, business_value).
        """
        try:
            if not task_matrix:
                return Err(ValueError("No tasks bounded in matrix for planning."))
                
            for struct in task_matrix:
                if struct[1] < 0 or struct[2] < 0:
                    return Err(ValueError(f"Negative bounds detected on struct {struct[0]}"))
            
            n = len(task_matrix)
            dp = [[0 for _ in range(self.sprint_capacity + 1)] for _ in range(n + 1)]
            
            # Sub-problem accumulation 
            for i in range(1, n + 1):
                name, effort, val = task_matrix[i-1]
                for w in range(1, self.sprint_capacity + 1):
                    if effort <= w:
                        dp[i][w] = max(dp[i-1][w], dp[i-1][w-effort] + val)
                    else:
                        dp[i][w] = dp[i-1][w]
                        
            # Backtrack to identify chosen tasks natively
            result_val = dp[n][self.sprint_capacity]
            w = self.sprint_capacity
            chosen_tasks = []
            
            for i in range(n, 0, -1):
                if result_val <= 0:
                    break
                # If the max value didn't come from the row above, we picked this task
                if result_val != dp[i-1][w]:
                    name, effort, val = task_matrix[i-1]
                    chosen_tasks.append({"task": name, "effort": effort, "value": val})
                    result_val -= val
                    w -= effort
                    
            chosen_tasks.reverse() # Order by insertion matrix
            
            total_effort = sum(t["effort"] for t in chosen_tasks)
            total_value = sum(t["value"] for t in chosen_tasks)
            
            return Ok({
                "planned_tasks": chosen_tasks,
                "total_effort": total_effort,
                "total_value": total_value,
                "efficiency": round(total_value / total_effort, 4) if total_effort > 0 else 0
            })
            
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """OMNI Framework bindings."""
        return {
            "engine": "OmniAgileSprintPlannerEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "capacity": self.sprint_capacity,
            "complexity": "O(N * W) Mathematical 0/1 Knapsack"
        }
