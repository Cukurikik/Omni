class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class LZ77Math:
    def __init__(self):
        pass

    def calculate_back_reference(self, current_pos: int, match_pos: int, match_length: int) -> OmniResult:
        if current_pos < 0 or match_pos < 0 or match_length <= 0:
            return OmniResult(error="Positions and length must be valid")
            
        if match_pos >= current_pos:
            return OmniResult(error="Match position must strictly precede current position")

        # Snappy uses specific bounds for offsets and lengths
        offset = current_pos - match_pos
        
        if offset > 65535: # Snappy maximum offset
            return OmniResult(error="Offset exceeds Snappy LZ77 window limit (65535 bytes)")

        # Returns the encoded tuple structure (offset, length)
        return OmniResult(value={"offset": offset, "length": match_length})
