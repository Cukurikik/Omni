class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class CRDTResolver:
    def __init__(self):
        pass

    def resolve_lww_register(self, local_value: str, local_timestamp: int, remote_value: str, remote_timestamp: int) -> OmniResult:
        if local_timestamp < 0 or remote_timestamp < 0:
            return OmniResult(error="Timestamps cannot be negative")

        # Deterministic Last-Writer-Wins (LWW) CRDT resolution
        # Essential for Edge devices syncing data after being offline in a tunnel or rural area
        try:
            if remote_timestamp > local_timestamp:
                return OmniResult(value={"resolved_value": remote_value, "resolved_timestamp": remote_timestamp})
            elif local_timestamp > remote_timestamp:
                return OmniResult(value={"resolved_value": local_value, "resolved_timestamp": local_timestamp})
            else:
                # Tie-breaker (lexicographical)
                if remote_value > local_value:
                    return OmniResult(value={"resolved_value": remote_value, "resolved_timestamp": remote_timestamp})
                else:
                    return OmniResult(value={"resolved_value": local_value, "resolved_timestamp": local_timestamp})
        except Exception as e:
            return OmniResult(error=str(e))
