from omni.core import Result, Ok, Err

class BenchmarkRunner:
    def run_suite(self, suite_id: str) -> Result[dict, ValueError]:
        if not suite_id:
            return Err(ValueError("Suite ID required"))
        return Ok({"score": 98.7, "latency_ms": 45.2})
