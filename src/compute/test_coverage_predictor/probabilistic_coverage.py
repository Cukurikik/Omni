class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class ProbabilisticCoverage:
    def __init__(self):
        pass

    def compute_branch_probability(self, total_branches: int, executed_branches: int) -> OmniResult:
        if total_branches <= 0 or executed_branches < 0 or executed_branches > total_branches:
            return OmniResult(error="Invalid branch counts")

        # Deterministic calculation of branch coverage
        # Used by the AI to predict how much of a newly generated file is covered by tests
        try:
            coverage = float(executed_branches) / float(total_branches)
            return OmniResult(value=coverage)
        except Exception as e:
            return OmniResult(error=str(e))
