# Omni LLM Agent Benchmark Engine
# Ref: zhangxjohn/LLM-Agent-Benchmark-List
from typing import List, Dict

def evaluate_agent_trajectory(trajectory: List[Dict[str, str]], target_goal: str) -> Dict[str, float]:
    """Evaluate an agent's reasoning trajectory towards a goal."""
    if not trajectory:
        return {"success_rate": 0.0, "efficiency": 0.0, "tool_usage_ratio": 0.0}
        
    success = False
    tool_uses = 0
    
    for step in trajectory:
        if step.get("type") == "tool":
            tool_uses += 1
        if target_goal.lower() in step.get("output", "").lower():
            success = True
            break
            
    efficiency = 1.0 / len(trajectory) if success else 0.0
    tool_ratio = tool_uses / len(trajectory)
    
    return {
        "success_rate": 1.0 if success else 0.0,
        "efficiency": round(efficiency, 4),
        "tool_usage_ratio": round(tool_ratio, 4)
    }

def aggregate_benchmark_results(results: List[Dict[str, float]]) -> Dict[str, float]:
    if not results:
        return {"mean_success": 0.0, "mean_efficiency": 0.0}
        
    success = sum(r.get("success_rate", 0.0) for r in results) / len(results)
    efficiency = sum(r.get("efficiency", 0.0) for r in results) / len(results)
    
    return {
        "mean_success": round(success, 4),
        "mean_efficiency": round(efficiency, 4),
        "total_tasks": float(len(results))
    }
