class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class SymbolicRegression:
    def __init__(self):
        pass

    def evaluate_fitness(self, equation_evals: list[float], ground_truth: list[float]) -> OmniResult:
        if not equation_evals or not ground_truth or len(equation_evals) != len(ground_truth):
            return OmniResult(error="Invalid data arrays for fitness calculation")

        n = len(ground_truth)
        
        # Deterministic Mean Squared Error fitness calculation
        mse = 0.0
        for i in range(n):
            diff = equation_evals[i] - ground_truth[i]
            mse += diff * diff
            
        mse /= n
        
        # Fitness is inverse of error (with small epsilon for stability)
        fitness = 1.0 / (mse + 1e-6)

        return OmniResult(value={
            "mse": mse,
            "fitness": fitness
        })
