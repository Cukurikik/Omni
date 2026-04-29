import re

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class KongRouting:
    def __init__(self):
        pass

    def compute_regex_priority(self, route_pattern: str, request_path: str) -> OmniResult:
        if not route_pattern or not request_path:
            return OmniResult(error="Route pattern and request path cannot be empty")

        # Deterministic Kong API Gateway routing math simulation
        try:
            regex = re.compile(route_pattern)
            match = regex.match(request_path)
            
            if match:
                # Priority math: Exact matches get highest priority, then prefix length, then regex capture groups
                score = len(match.group(0)) * 10
                score += len(match.groups()) * 5
                return OmniResult(value={"matched": True, "score": score})
            else:
                return OmniResult(value={"matched": False, "score": 0})
        except re.error as e:
            return OmniResult(error=f"Invalid regex pattern: {str(e)}")
