# OMNI Compute Layer - MLflow Experiment Tracker
import time

class MLflowError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def log_metric_step(run_id: str, key: str, value: float, step: int) -> Result:
    """Logs a single time-series metric into MLflow tracking format."""
    try:
        if not run_id or not key:
            return Result(error=MLflowError("Invalid run ID or metric key"))
            
        timestamp = int(time.time() * 1000)
        payload = {
            "run_id": run_id,
            "key": key,
            "value": value,
            "timestamp": timestamp,
            "step": step
        }
        
        return Result(value={"logged": payload})
    except Exception as e:
        return Result(error=MLflowError(f"Metric logging failed: {str(e)}"))
