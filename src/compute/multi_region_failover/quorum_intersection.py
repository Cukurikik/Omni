class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class QuorumIntersection:
    def __init__(self):
        pass

    def check_paxos_majority(self, total_regions: int, active_regions: int) -> OmniResult:
        if total_regions <= 0 or active_regions < 0 or active_regions > total_regions:
            return OmniResult(error="Invalid region counts")

        # Deterministic calculation of Paxos/Raft Quorum Intersection
        # Ensures that a distributed database across multiple global regions does not suffer a "Split-Brain"
        try:
            # A quorum requires strictly greater than 50% of the nodes
            required_quorum = (total_regions // 2) + 1
            
            has_quorum = active_regions >= required_quorum
            
            return OmniResult(value=has_quorum)
        except Exception as e:
            return OmniResult(error=str(e))
