import math

class FinRAGError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self):
        if not self.is_ok():
            raise self.error
        return self.value

# OMNI Engine: finragbench-v
# Computes logical mapping bounds for visual citations in dense financial document structures.
class FinRAGBenchEngine:
    def __init__(self, strictness_level: float = 0.95):
        self.strictness = strictness_level

    def verify_financial_visual_citation(self, extracted_number: float, chart_visual_value: float) -> Result:
        try:
            if chart_visual_value == 0.0 and extracted_number != 0.0:
                 return Result(error=FinRAGError("Zero-div bounds violation on chart logic"))
            
            if chart_visual_value == 0.0 and extracted_number == 0.0:
                 return Result(value={"citation_verified": True, "delta": 0.0})

            delta = abs(extracted_number - chart_visual_value) / abs(chart_visual_value)

            # In finance, strict bounds mean deviation must be extremely low (e.g., < 5%)
            verified = delta <= (1.0 - self.strictness)

            return Result(value={
                "citation_verified": verified,
                "delta": delta,
                "confidence": 1.0 - delta
            })

        except Exception as e:
            return Result(error=FinRAGError(f"Financial RAG bounds check structurally failed: {str(e)}"))
