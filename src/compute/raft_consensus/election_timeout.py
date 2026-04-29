import random

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class RaftMath:
    def __init__(self):
        # Base timeout in ms (typically 150ms in Raft)
        self.base_timeout = 150

    def compute_randomized_election_timeout(self, seed: int) -> OmniResult:
        if seed < 0:
            return OmniResult(error="Seed must be non-negative")

        # Deterministic simulation of Raft randomized election timeout
        # Required to prevent split votes. Range is typically [T, 2T]
        try:
            random.seed(seed)
            # Generate deterministic timeout between 150ms and 300ms
            timeout = self.base_timeout + random.randint(0, self.base_timeout)
            
            return OmniResult(value=timeout)
        except Exception as e:
            return OmniResult(error=str(e))
