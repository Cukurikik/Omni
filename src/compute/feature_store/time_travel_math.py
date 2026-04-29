class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class TimeTravelMath:
    def __init__(self):
        pass

    def retrieve_point_in_time(self, events: list[dict], target_timestamp: int) -> OmniResult:
        if not events:
            return OmniResult(error="Empty events list")

        # Deterministic Time Travel interpolation for Feature Store
        # Assumes events is sorted by timestamp: [{'ts': 100, 'val': 5.0}, ...]
        
        latest_val = None
        
        for event in events:
            if event['ts'] <= target_timestamp:
                latest_val = event['val']
            else:
                break # Since sorted, we passed the target time

        if latest_val is None:
            return OmniResult(error="No events found prior to target timestamp")

        return OmniResult(value={
            "timestamp": target_timestamp,
            "feature_value": latest_val
        })
