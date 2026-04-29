# Omni AutoML Pipeline Engine
from typing import List, Dict

def hyperparameter_grid_search(param_grid: Dict[str, List[float]]) -> List[Dict[str, float]]:
    """Generate exhaustive combinations for hyperparameter tuning."""
    keys = list(param_grid.keys())
    if not keys: return []
    
    combinations = [{}]
    for key in keys:
        new_combinations = []
        for val in param_grid[key]:
            for combo in combinations:
                new_combo = dict(combo)
                new_combo[key] = val
                new_combinations.append(new_combo)
        combinations = new_combinations
        
    return combinations

def calculate_pipeline_fitness(accuracy: float, latency_ms: float, memory_mb: float) -> float:
    """Calculate fitness score of an AutoML pipeline (higher is better)."""
    # Penalty for latency and memory
    latency_penalty = max(0.0, latency_ms - 100.0) * 0.001
    memory_penalty = max(0.0, memory_mb - 512.0) * 0.0005
    
    fitness = accuracy - latency_penalty - memory_penalty
    return round(max(0.0, min(1.0, fitness)), 4)
