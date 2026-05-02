"""
@omni-domain Compute Layer (Model Tuning)
@omni-source various/tuning-frameworks
@omni-description Omni Tuning Engines mimicking hyperparameter search.
@omni-requirement zero-mock, monadic-error
"""
import math
from typing import Any, Optional, List, Dict

class OmniResult:
    def __init__(self, data=None, error=None):
        self.data = data
        self.error = error
    def is_ok(self): return self.error is None

class TuningError(Exception): pass

class OmniTuningEngines:
    def __init__(self):
        self.trials = []

    def grid_search(self, param_grid: Dict[str, List], objective_fn) -> OmniResult:
        try:
            if not param_grid:
                return OmniResult(error=TuningError("Param grid empty."))
            keys = list(param_grid.keys())
            combos = [{}]
            for key in keys:
                new_combos = []
                for combo in combos:
                    for val in param_grid[key]:
                        new_combo = dict(combo)
                        new_combo[key] = val
                        new_combos.append(new_combo)
                combos = new_combos
            best_score = float('-inf')
            best_params = None
            for combo in combos:
                score = objective_fn(combo)
                self.trials.append({"params": combo, "score": score})
                if score > best_score:
                    best_score = score
                    best_params = combo
            return OmniResult(data={"best_params": best_params, "best_score": best_score, "n_trials": len(combos)})
        except Exception as e:
            return OmniResult(error=TuningError(f"Grid search failed: {e}"))

    def random_search(self, param_ranges: Dict[str, tuple], n_trials: int, objective_fn) -> OmniResult:
        try:
            if not param_ranges or n_trials <= 0:
                return OmniResult(error=TuningError("Invalid params or n_trials."))
            best_score = float('-inf')
            best_params = None
            for trial in range(n_trials):
                params = {}
                for key, (lo, hi) in param_ranges.items():
                    # Deterministic pseudo-random using sin
                    val = lo + (hi - lo) * abs(math.sin(trial * 137 + hash(key) * 0.001))
                    params[key] = val
                score = objective_fn(params)
                self.trials.append({"params": params, "score": score})
                if score > best_score:
                    best_score = score
                    best_params = params
            return OmniResult(data={"best_params": best_params, "best_score": best_score, "n_trials": n_trials})
        except Exception as e:
            return OmniResult(error=TuningError(f"Random search failed: {e}"))
