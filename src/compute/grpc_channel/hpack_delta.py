class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class HpackCompression:
    def __init__(self):
        # Simulated static table
        self.static_table = {
            ":method": "GET",
            ":path": "/",
            ":status": "200"
        }

    def compute_delta_index(self, header_key: str, header_val: str) -> OmniResult:
        if not header_key:
            return OmniResult(error="Header key cannot be empty")

        # Deterministic simulation of HTTP/2 HPACK delta compression math
        # Returns an index if it exists in the static table, else 0 (requires literal transmission)
        if header_key in self.static_table and self.static_table[header_key] == header_val:
            # Hash to simulate index
            idx = sum(ord(c) for c in header_key) % 61 + 1
            return OmniResult(value=idx)
            
        return OmniResult(value=0)
