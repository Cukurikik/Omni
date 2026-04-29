class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class RelationalAlgebra:
    def __init__(self):
        pass

    def compute_join_cardinality(self, rows_a: int, rows_b: int, selectivity: float) -> OmniResult:
        if rows_a < 0 or rows_b < 0:
            return OmniResult(error="Row counts must be non-negative")
            
        if selectivity < 0.0 or selectivity > 1.0:
            return OmniResult(error="Selectivity must be between 0.0 and 1.0")

        # Deterministic cost/cardinality estimation math for query planning
        # Estimated cardinality = |A| * |B| * selectivity
        
        try:
            estimated_rows = int(rows_a * rows_b * selectivity)
            return OmniResult(value=estimated_rows)
        except Exception as e:
            return OmniResult(error=str(e))
