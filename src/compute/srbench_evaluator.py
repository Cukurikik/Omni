# OMNI Compute Layer - SRBench Evaluator
import numpy as np

class SRBenchError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def evaluate_symbolic_equation(y_true: np.ndarray, y_pred: np.ndarray) -> Result:
    """
    Evaluates scientific equation discovery accuracy.
    """
    try:
        if y_true.shape != y_pred.shape:
            return Result(error=SRBenchError("Shape mismatch between true and predicted targets"))
            
        mse = np.mean((y_true - y_pred)**2)
        variance = np.var(y_true)
        if variance == 0:
            return Result(error=SRBenchError("Zero variance in true targets"))
            
        r_squared = 1 - (mse / variance)
        return Result(value={"mse": float(mse), "r_squared": float(r_squared)})
    except Exception as e:
        return Result(error=SRBenchError(f"Evaluation failed: {str(e)}"))
